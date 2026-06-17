from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Tuple
import hmac

from cachetools import TTLCache


class SimpleTTLCache:
    def __init__(self, maxsize: int = 1024, ttl: int = 60) -> None:
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)

    @staticmethod
    def key_for(method: str, url: str, json_body: Any, *, namespace: str | None = None) -> str:
        if json_body is not None:
            try:
                payload = json.dumps(json_body, sort_keys=True, separators=(",", ":"))
            except (TypeError, ValueError) as e:
                # Fallback for non-serializable objects
                payload = f"non_serializable_{type(json_body).__name__}_{hash(str(json_body))}"
        else:
            payload = ""
        base = hashlib.sha256()
        base.update(method.encode())
        base.update(b"\n")
        base.update(url.encode())
        base.update(b"\n")
        base.update(payload.encode())
        digest = base.digest()
        if namespace:
            # Bind to namespace using HMAC for stability
            return hmac.new(namespace.encode(), digest, hashlib.sha256).hexdigest()
        return digest.hex()

    def get(self, key: str) -> Tuple[int, dict] | None:
        return self._cache.get(key)

    def set(self, key: str, status_code: int, json_data: dict) -> None:
        self._cache[key] = (status_code, json_data)

    def size(self) -> int:
        return self._cache.currsize

    def maxsize(self) -> int:
        return self._cache.maxsize

