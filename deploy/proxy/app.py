from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any
import logging

import httpx
from aiolimiter import AsyncLimiter
from fastapi import FastAPI, Request, Response
try:
    from fastapi.middleware.cors import CORSMiddleware  # type: ignore
except Exception:  # pragma: no cover
    CORSMiddleware = None  # type: ignore
from fastapi.responses import JSONResponse, StreamingResponse

from .config import settings
from .tokenizer import count_chat_message_tokens
from .cache import SimpleTTLCache


app = FastAPI(title="Denario TPM/RPM Proxy", version="0.1.0")
logging.basicConfig(level=logging.INFO, format="[proxy] %(levelname)s: %(message)s")

# Cache environment variables to avoid repeated lookups
_TIMEOUT_JSON_BASE = float(os.getenv("TIMEOUT_JSON_BASE", "20"))
_TIMEOUT_JSON_TOKENS_PER_SEC = float(os.getenv("TIMEOUT_JSON_TOKENS_PER_SEC", "40"))
_TIMEOUT_JSON_MIN = float(os.getenv("TIMEOUT_JSON_MIN", "30"))
_TIMEOUT_JSON_MAX = float(os.getenv("TIMEOUT_JSON_MAX", str(settings.timeout_stream_seconds)))
_UPSTREAM_RETRY_ATTEMPTS = int(os.getenv("UPSTREAM_RETRY_ATTEMPTS", "3"))


# Global limiters/state
rpm_limiter = AsyncLimiter(max_rate=settings.rpm_budget, time_period=60)
concurrency_sem = asyncio.Semaphore(settings.max_concurrency)
cache = SimpleTTLCache(maxsize=settings.cache_maxsize, ttl=settings.cache_ttl_seconds)

_token_lock = asyncio.Lock()
_tokens_window_reset = 0.0
_tokens_used = 0


def _now() -> float:
    return time.monotonic()


async def _check_and_consume_tpm(tokens_estimate: int) -> float | None:
    """Return retry-after seconds if over budget; else consume and return None."""
    global _tokens_window_reset, _tokens_used
    async with _token_lock:
        now = _now()
        if now >= _tokens_window_reset:
            _tokens_window_reset = now + 60.0
            _tokens_used = 0
        if _tokens_used + tokens_estimate > settings.tpm_budget:
            return max(0.0, _tokens_window_reset - now)
        _tokens_used += tokens_estimate
        return None


def _upstream_headers(incoming: Request) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    # Prefer configured key; else forward Authorization
    api_key = settings.upstream_api_key
    auth = incoming.headers.get("authorization")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    elif auth:
        headers["Authorization"] = auth
    # Forward org header if present
    org = incoming.headers.get("openai-organization")
    if org:
        headers["OpenAI-Organization"] = org
    return headers


# Cache sorted prefix keys to avoid repeated sorting
_sorted_prefix_keys = []
_prefix_cache_lock = asyncio.Lock()

async def _get_sorted_prefix_keys():
    global _sorted_prefix_keys
    if not settings.model_alias_prefixes:
        return []
    async with _prefix_cache_lock:
        if not _sorted_prefix_keys or len(_sorted_prefix_keys) != len(settings.model_alias_prefixes):
            _sorted_prefix_keys = sorted(settings.model_alias_prefixes.keys(), key=len, reverse=True)
        return _sorted_prefix_keys

def _resolve_model_alias(model: str | None) -> str | None:
    """Resolve model via force/aliases, allowing prefix/exact chaining with a small cap.

    This enables scenarios like gpt-4* -> gpt-5-mini (prefix) and then
    gpt-5-mini -> gpt-4o-mini (exact), producing a real upstream model.
    """
    if model is None:
        return None
    # Force model takes precedence always
    if settings.force_model:
        return settings.force_model

    current = str(model)
    seen: set[str] = set()
    # Cap to avoid loops
    for _ in range(5):
        if current in seen:
            break
        seen.add(current)
        target: str | None = None
        # Try exact alias
        if current in settings.model_aliases:
            target = settings.model_aliases[current]
        # Then prefix alias (longest match wins)
        if not target and settings.model_alias_prefixes:
            # Use synchronous access since this is called from sync context
            sorted_keys = sorted(settings.model_alias_prefixes.keys(), key=len, reverse=True)
            for prefix in sorted_keys:
                if current.startswith(prefix):
                    target = settings.model_alias_prefixes[prefix]
                    break
        if not target or target == current:
            break
        current = str(target)
    return current


async def _forward_stream(method: str, url: str, headers: dict[str, str], data: bytes):
    client = httpx.AsyncClient(timeout=settings.timeout_stream_seconds)
    try:
        try:
            resp = await client.stream(method, url, headers=headers, content=data)
        except Exception:
            await client.aclose()
            raise
            
        response_headers = {
            k: v for k, v in resp.headers.items() if k.lower().startswith("content-") or k.lower().startswith("x-")
        }
        
        async def stream_with_cleanup():
            try:
                async for chunk in resp.aiter_raw():
                    yield chunk
            finally:
                await resp.aclose()
                await client.aclose()

        return StreamingResponse(stream_with_cleanup(), status_code=resp.status_code, headers=response_headers)
    except httpx.ReadTimeout:
        await client.aclose()
        return JSONResponse(status_code=504, content={
            "error": {
                "message": "Upstream stream timeout",
                "type": "upstream_timeout",
            }
        })
    except Exception as e:
        await client.aclose()
        safe_error = str(e)[:200].replace('\n', '\\n').replace('\r', '\\r')
        return JSONResponse(status_code=502, content={
            "error": {
                "message": f"Upstream stream error: {safe_error}",
                "type": "upstream_error",
            }
        })


def _calculate_backoff_delay(attempt: int) -> float:
    """Calculate exponential backoff delay with jitter."""
    return min(2 ** attempt + (0.1 * attempt), 5.0)

async def _forward_json(method: str, url: str, headers: dict[str, str], json_body: Any) -> Response:
    # Derive a token-aware timeout for JSON requests
    timeout_seconds = settings.timeout_json_seconds
    try:
        if isinstance(json_body, dict):
            tokens_est = 0
            if "messages" in json_body:
                tokens_est = _estimate_tokens_for_chat(json_body)
            # Base + tokens_est / throughput (tokens/sec), clamped to [MIN, MAX]
            dyn = _TIMEOUT_JSON_BASE + (tokens_est / max(1.0, _TIMEOUT_JSON_TOKENS_PER_SEC))
            timeout_seconds = max(_TIMEOUT_JSON_MIN, min(_TIMEOUT_JSON_MAX, dyn))
            # Optional per-request override (clamped)
            req_override = json_body.get("timeout_seconds")
            if isinstance(req_override, (int, float)) and req_override > 0:
                timeout_seconds = max(_TIMEOUT_JSON_MIN, min(_TIMEOUT_JSON_MAX, float(req_override)))
    except (AttributeError, TypeError, ValueError):
        timeout_seconds = settings.timeout_json_seconds

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        # Retry policy for 429/5xx and transient read/protocol errors
        max_attempts = _UPSTREAM_RETRY_ATTEMPTS
        for attempt in range(max_attempts):
            try:
                resp = await client.request(method, url, headers=headers, json=json_body)
            except (httpx.ReadError, httpx.RemoteProtocolError, httpx.TransportError) as e:
                safe_error = str(e)[:200].replace('\n', '\\n').replace('\r', '\\r')
                logging.warning(f"Upstream read/protocol error (attempt {attempt+1}/{max_attempts}): {safe_error}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(_calculate_backoff_delay(attempt))
                continue

            if resp.status_code in (429, 500, 502, 503, 504):
                retry_after = float(resp.headers.get("Retry-After", "0") or 0)
                logging.warning(f"Upstream {resp.status_code}; retrying (attempt {attempt+1}/{max_attempts})")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(_calculate_backoff_delay(attempt) + retry_after)
                continue

            if resp.status_code >= 400:
                try:
                    # Sanitize inputs for logging to prevent log injection
                    safe_model = str((json_body or {}).get('model', ''))[:50].replace('\n', '\\n').replace('\r', '\\r')
                    safe_keys = [str(k)[:20].replace('\n', '\\n').replace('\r', '\\r') for k in list((json_body or {}).keys())[:10]]
                    safe_error_body = resp.text[:500].replace('\n', '\\n').replace('\r', '\\r')
                    logging.warning(f"Upstream {resp.status_code} at {url}; model={safe_model} keys={safe_keys}")
                    logging.warning(f"Upstream error body: {safe_error_body}")
                except (AttributeError, TypeError, httpx.ResponseNotRead) as e:
                    logging.warning(f"Failed to log upstream error details: {e}")
            try:
                payload = resp.json()
            except Exception:
                payload = {"error": {"message": resp.text, "status": resp.status_code}}
            return JSONResponse(status_code=resp.status_code, content=payload)
        return JSONResponse(status_code=502, content={"error": {"message": "Upstream incomplete/protocol error after retries"}})


def _estimate_tokens_for_chat(body: dict[str, Any]) -> int:
    model = body.get("model") or ""
    messages = body.get("messages") or []
    input_tokens = count_chat_message_tokens(messages, model)
    # Support multiple parameter names across providers/SDKs
    try:
        max_out = int(
            body.get("max_tokens")
            or body.get("max_completion_tokens")
            or body.get("max_output_tokens")
            or 0
        )
    except (ValueError, TypeError):
        max_out = 0
    # Budget both input and planned output
    return input_tokens + max(0, max_out)


@app.api_route("/v1/{path:path}", methods=["GET", "POST"])
async def openai_compatible_proxy(path: str, request: Request) -> Response:
    method = request.method
    upstream_url = settings.upstream_base_url.rstrip("/") + "/" + path
    headers = _upstream_headers(request)

    # Concurrency limit + RPM limit
    async with concurrency_sem:
        async with rpm_limiter:
            # Read body for POST; forward streaming if requested
            if method == "POST":
                raw = await request.body()
                try:
                    body = json.loads(raw.decode() or "{}")
                except Exception:
                    body = {}

                # Apply model override/aliases with recursive resolution if configured
                model_before = body.get("model") if isinstance(body, dict) else None
                if isinstance(body, dict):
                    resolved = _resolve_model_alias(model_before)
                    if resolved and resolved != model_before:
                        body["model"] = resolved
                    # Apply default/allow policy: if default_model set, remap anything not allowed
                    eff_model = str(body.get("model") or "")
                    if settings.default_model and eff_model and (eff_model not in settings.allow_models):
                        body["model"] = settings.default_model
                    # Do not rename max_tokens for OpenAI chat/completions; pass through as provided
                    # Targeted normalization for gpt-5*: translate max_tokens -> max_completion_tokens
                    eff_model = str(body.get("model") or "")
                    if eff_model.startswith("gpt-5") and "max_tokens" in body and "max_completion_tokens" not in body and "max_output_tokens" not in body:
                        try:
                            body["max_completion_tokens"] = int(body.get("max_tokens") or 0)
                        except (ValueError, TypeError):
                            body["max_completion_tokens"] = body.get("max_tokens")
                        body.pop("max_tokens", None)

                    # Sanitize unsupported/invalid parameters for upstream
                    # Remove null temperature (some clients send explicit null)
                    if body.get("temperature", "__absent__") is None:
                        body.pop("temperature", None)
                    # Drop logprobs fields that some models don't allow
                    if "logprobs" in body:
                        body.pop("logprobs", None)
                    if "top_logprobs" in body:
                        body.pop("top_logprobs", None)
                    # Refresh raw payload after any changes and log summary
                    raw = json.dumps(body, separators=(",", ":")).encode()
                    try:
                        # Sanitize inputs for logging to prevent log injection
                        safe_model = str(body.get('model', ''))[:50].replace('\n', '\\n').replace('\r', '\\r')
                        safe_model_before = str(model_before or '')[:50].replace('\n', '\\n').replace('\r', '\\r') if model_before else None
                        safe_keys = [str(k)[:20].replace('\n', '\\n').replace('\r', '\\r') for k in list(body.keys())[:10]]
                        safe_path = str(path)[:50].replace('\n', '\\n').replace('\r', '\\r')
                        logging.info(
                            f"Forwarding /v1/{safe_path} model={safe_model}" +
                            (f" (from {safe_model_before})" if safe_model_before and safe_model != safe_model_before else "") +
                            f" stream={bool(body.get('stream'))} keys={safe_keys}"
                        )
                    except (AttributeError, TypeError) as e:
                        safe_error = str(e)[:100].replace('\n', '\\n').replace('\r', '\\r')
                        logging.warning(f"Failed to log request details: {safe_error}")

                # Estimate tokens for chat completions; otherwise 0
                tokens_est = 0
                if path.startswith("chat/completions"):
                    tokens_est = _estimate_tokens_for_chat(body)

                # Context-aware fallback: if requesting primary_model and tokens exceed window, switch to fallback_model
                if (
                    isinstance(body, dict)
                    and settings.primary_model
                    and settings.fallback_model
                    and str(body.get("model") or "") == settings.primary_model
                    and tokens_est > max(0, settings.primary_ctx_window)
                ):
                    body["model"] = settings.fallback_model
                    try:
                        # Sanitize model names for logging
                        safe_primary = str(settings.primary_model or '')[:50].replace('\n', '\\n').replace('\r', '\\r')
                        safe_fallback = str(settings.fallback_model or '')[:50].replace('\n', '\\n').replace('\r', '\\r')
                        logging.info(f"Fallback: tokens_est={tokens_est} > {settings.primary_ctx_window}; model={safe_primary} -> {safe_fallback}")
                    except (AttributeError, TypeError) as e:
                        safe_error = str(e)[:100].replace('\n', '\\n').replace('\r', '\\r')
                        logging.warning(f"Failed to log fallback details: {safe_error}")
                    # Refresh raw after change
                    raw = json.dumps(body, separators=(",", ":")).encode()

                # Enforce TPM budget
                retry_after = await _check_and_consume_tpm(tokens_est)
                if retry_after is not None:
                    return JSONResponse(status_code=429, content={
                        "error": {
                            "message": "TPM budget exceeded; try later",
                            "type": "rate_limit_exceeded",
                            "retry_after": retry_after,
                        }
                    }, headers={"Retry-After": f"{retry_after:.0f}"})

                # Optional override: force non-streaming for chat/completions regardless of client flag
                try:
                    if os.getenv("FORCE_STREAM_OFF", "0") == "1":
                        if path.startswith("chat/completions") and isinstance(body, dict):
                            body["stream"] = False
                            raw = json.dumps(body, separators=(",", ":")).encode()
                except (json.JSONEncodeError, TypeError):
                    pass

                # Cache only non-streaming requests
                stream = bool(body.get("stream"))
                if not stream and method == "POST" and path in ("chat/completions", "embeddings"):
                    # Namespace cache by upstream base and a stable auth identity hash (non-secret)
                    auth_hdr = headers.get("Authorization", "")
                    identity = "anon"
                    if auth_hdr:
                        try:
                            # Use a short hash of the presented token without storing the secret itself
                            import hashlib
                            identity = hashlib.sha256(auth_hdr.encode()).hexdigest()[:16]
                        except Exception:
                            identity = "anon"
                    namespace = f"{settings.upstream_base_url}|{identity}"
                    key = cache.key_for(method, upstream_url, body, namespace=namespace)
                    cached = cache.get(key)
                    if cached:
                        status, payload = cached
                        return JSONResponse(status_code=status, content=payload, headers={"X-Proxy-Cache": "HIT"})
                    resp = await _forward_json(method, upstream_url, headers, body)
                    try:
                        payload = json.loads(resp.body)
                    except Exception:
                        payload = None
                    if isinstance(resp, JSONResponse) and isinstance(payload, dict) and resp.status_code == 200:
                        cache.set(key, resp.status_code, payload)
                    return resp

                # Streaming or non-cacheable
                if stream:
                    return await _forward_stream(method, upstream_url, headers, raw)
                return await _forward_json(method, upstream_url, headers, body)

            # GET (rare for OpenAI API) — just forward
            async with httpx.AsyncClient(timeout=settings.timeout_get_seconds) as client:
                resp = await client.get(upstream_url, headers=headers)
                try:
                    payload = resp.json()
                except Exception:
                    payload = {"error": {"message": resp.text, "status": resp.status_code}}
                return JSONResponse(status_code=resp.status_code, content=payload)


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    # Compute token window status under lock for consistency
    global _tokens_window_reset, _tokens_used
    async with _token_lock:
        now = _now()
        window_reset_in = max(0.0, _tokens_window_reset - now)
        tokens_used = int(_tokens_used)
        tpm_budget = int(settings.tpm_budget)
    # Best-effort concurrency usage snapshot
    try:
        available = int(getattr(concurrency_sem, "_value", settings.max_concurrency))
        in_flight = max(0, int(settings.max_concurrency) - available)
    except Exception:
        in_flight = None
    return {
        "ok": True,
        "rpm_budget": settings.rpm_budget,
        "tpm_budget": settings.tpm_budget,
        "tpm_used": tokens_used,
        "tpm_window_reset_seconds": window_reset_in,
        "max_concurrency": settings.max_concurrency,
        "concurrency_in_flight": in_flight,
        "upstream_base_url": settings.upstream_base_url,
        "model_force": settings.force_model,
        "model_aliases": settings.model_aliases,
        "model_alias_prefixes": settings.model_alias_prefixes,
        "cache": {
            "size": cache.size(),
            "maxsize": settings.cache_maxsize,
            "ttl_seconds": settings.cache_ttl_seconds,
        },
    }


@app.options("/healthz")
async def healthz_preflight() -> Response:
    # Empty 204; CORS headers will be injected by CORSMiddleware when enabled
    return Response(status_code=204)


def configure_app() -> FastAPI:
    # Optional CORS toggle via env
    try:
        if os.getenv("PROXY_ENABLE_CORS", "0") == "1" and CORSMiddleware is not None:
            origins = [o.strip() for o in os.getenv("PROXY_CORS_ORIGINS", "*").split(",") if o.strip()]
            app.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
    except (ImportError, AttributeError) as e:
        logging.warning(f"Failed to setup CORS middleware: {e}")
    return app


def create_app() -> FastAPI:
    # Compatibility factory for uvicorn --factory
    return configure_app()
