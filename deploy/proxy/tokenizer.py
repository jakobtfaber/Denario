from __future__ import annotations

from typing import Any

try:
    import tiktoken
except Exception:  # pragma: no cover - tiktoken optional at runtime
    tiktoken = None


# Minimal model -> encoding map. Fallback to cl100k_base.
MODEL_TO_ENCODING = {
    # OpenAI
    "gpt-4o": "o200k_base",
    "gpt-4o-mini": "o200k_base",
    "gpt-4.1": "o200k_base",
    "gpt-4.1-mini": "o200k_base",
    "gpt-4-turbo": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    # Others may be OpenAI-compatible; fallback below.
}

# Cache sorted keys to avoid repeated sorting
_SORTED_MODEL_KEYS = sorted(MODEL_TO_ENCODING.keys(), key=len, reverse=True)


def get_encoding_for_model(model: str) -> str:
    model_l = (model or "").lower()
    # Use cached sorted keys for performance - exact prefix matching
    for key in _SORTED_MODEL_KEYS:
        if model_l.startswith(key):
            return MODEL_TO_ENCODING[key]
    # Fallback: cl100k_base widely used
    return "cl100k_base"


def count_tokens(text: str, model: str | None = None) -> int:
    if not text:
        return 0
    if tiktoken is None:
        # Rough fallback: ~4 chars per token
        return max(1, len(text) // 4)
    enc_name = get_encoding_for_model(model or "")
    try:
        enc = tiktoken.get_encoding(enc_name)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def count_chat_message_tokens(messages: list[dict[str, Any]] | None, model: str | None = None) -> int:
    if not messages:
        return 0
    total = 0
    for m in messages:
        # Count role + content string parts
        role = m.get("role") or ""
        total += count_tokens(role, model)
        content = m.get("content")
        if isinstance(content, str):
            total += count_tokens(content, model)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict):
                    if "text" in part and isinstance(part["text"], str):
                        total += count_tokens(part["text"], model)
                    # Ignore binary parts for budgeting
        # Name and tool_calls add overhead but we keep it simple
    return total

