import os
import json


def getenv_str(name: str, default: str) -> str:
    return os.getenv(name, default)


def getenv_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def getenv_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


class Settings:
    # Proxy bind
    host: str = getenv_str("PROXY_HOST", "0.0.0.0")
    port: int = getenv_int("PROXY_PORT", 8080)

    # Upstream OpenAI-compatible base URL
    upstream_base_url: str = getenv_str("UPSTREAM_OPENAI_BASE_URL", "https://api.openai.com/v1")

    # API key fallback (if not provided by Authorization header)
    upstream_api_key: str | None = os.getenv("OPENAI_API_KEY")

    # Budgets per minute
    rpm_budget: int = getenv_int("RPM_BUDGET", 60)
    tpm_budget: int = getenv_int("TPM_BUDGET", 80000)

    # Concurrency and caching
    max_concurrency: int = getenv_int("MAX_CONCURRENCY", 4)
    cache_ttl_seconds: int = getenv_int("CACHE_TTL_SECONDS", 60)
    cache_maxsize: int = getenv_int("CACHE_MAXSIZE", 1024)

    # Model context window defaults (used for budgeting/validation)
    default_ctx_window: int = getenv_int("CTX_WINDOW", 128000)
    default_max_output: int = getenv_int("MAX_OUTPUT_TOKENS", 4096)

    # Optional model override/aliases
    force_model: str | None = os.getenv("FORCE_MODEL")
    # MODEL_ALIASES can be JSON (e.g., '{"gpt-4.1":"gpt-4o-mini"}') or comma-separated pairs 'a=b,c=d'
    _aliases_raw: str | None = os.getenv("MODEL_ALIASES")
    model_aliases: dict[str, str] = {}
    # MODEL_ALIAS_PREFIXES maps prefixes to targets, same formats as MODEL_ALIASES
    _prefixes_raw: str | None = os.getenv("MODEL_ALIAS_PREFIXES")
    model_alias_prefixes: dict[str, str] = {}

    # Default/allow/fallback policy
    # If set, any model not in allow_models will be remapped to default_model after aliasing
    default_model: str | None = os.getenv("DEFAULT_MODEL")
    _allow_models_raw: str | None = os.getenv("ALLOW_MODELS")
    allow_models: set[str] = set()

    # Optional primary/fallback model with context-aware fallback
    primary_model: str | None = os.getenv("PRIMARY_MODEL")
    fallback_model: str | None = os.getenv("FALLBACK_MODEL")
    # If not provided, falls back to default_ctx_window
    primary_ctx_window: int = getenv_int("PRIMARY_CTX_WINDOW", 128000)

    # Upstream HTTP timeouts (seconds)
    timeout_json_seconds: float = getenv_float("TIMEOUT_JSON_SECONDS", 60.0)
    timeout_stream_seconds: float = getenv_float("TIMEOUT_STREAM_SECONDS", 300.0)
    timeout_get_seconds: float = getenv_float("TIMEOUT_GET_SECONDS", 30.0)

    def _parse_dict_config(self, raw: str) -> dict[str, str]:
        """Parse JSON dict or CSV pairs format."""
        result = {}
        if not raw:
            return result
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return {str(k): str(v) for k, v in parsed.items()}
            raise ValueError("Expected dict format")
        except (json.JSONDecodeError, ValueError):
            for part in raw.split(','):
                part = part.strip()
                if not part or '=' not in part:
                    continue
                k, v = part.split('=', 1)
                k = k.strip()
                v = v.strip()
                if k and v:
                    result[k] = v
        return result

    def _parse_list_config(self, raw: str) -> set[str]:
        """Parse JSON list or CSV format."""
        result = set()
        if not raw:
            return result
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, (list, set, tuple)):
                return {str(x) for x in parsed}
            raise ValueError("Expected list format")
        except (json.JSONDecodeError, ValueError):
            for part in raw.split(','):
                part = part.strip()
                if part:
                    result.add(part)
        return result

    def __init__(self) -> None:
        # Populate configurations using helper methods
        self.model_aliases = self._parse_dict_config(self._aliases_raw or "")
        self.model_alias_prefixes = self._parse_dict_config(self._prefixes_raw or "")
        self.allow_models = self._parse_list_config(self._allow_models_raw or "")


settings = Settings()
