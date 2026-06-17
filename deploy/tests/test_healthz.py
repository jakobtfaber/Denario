import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so `proxy` can be imported
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient

try:
    from proxy.app import create_app  # type: ignore
except Exception:
    create_app = None  # type: ignore
from proxy.app import app as app_instance  # type: ignore


def test_healthz_basic_fields():
    os.environ.setdefault("RPM_BUDGET", "60")
    os.environ.setdefault("TPM_BUDGET", "80000")
    os.environ.setdefault("MAX_CONCURRENCY", "4")
    app = create_app() if callable(create_app) else app_instance
    client = TestClient(app)

    resp = client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()

    # Required numeric budgets
    assert isinstance(data["rpm_budget"], int)
    assert isinstance(data["tpm_budget"], int)
    assert isinstance(data["max_concurrency"], int)

    # Token window usage fields
    assert "tpm_used" in data
    assert "tpm_window_reset_seconds" in data
    assert isinstance(data["tpm_used"], int)
    assert isinstance(data["tpm_window_reset_seconds"], (int, float))
    assert data["tpm_used"] >= 0
    assert data["tpm_window_reset_seconds"] >= 0

    # Cache stats
    assert "cache" in data
    cache = data["cache"]
    assert isinstance(cache.get("size", 0), int)
    assert isinstance(cache.get("maxsize", 0), int)
    assert isinstance(cache.get("ttl_seconds", 0), int)

    # Concurrency snapshot present (may be None on some runtimes)
    assert "concurrency_in_flight" in data
    if data["concurrency_in_flight"] is not None:
        assert isinstance(data["concurrency_in_flight"], int)
        assert 0 <= data["concurrency_in_flight"] <= data["max_concurrency"]


