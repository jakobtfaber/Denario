import sys
import types
import importlib as _importlib

import importlib.util
from pathlib import Path

# Load ag2_integration as a standalone module to avoid importing the entire denario package
_ag2_path = Path(__file__).resolve().parents[1] / "denario" / "ag2_integration.py"
spec = importlib.util.spec_from_file_location("ag2_integration", str(_ag2_path))
ag2 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(ag2)  # type: ignore


def test_is_ag2_available_positive(monkeypatch):
    """Unit test: when AG2 path setup succeeds and autogen exposes the expected symbol,
    is_ag2_available() should return True.
    """
    # Force setup_ag2_path to succeed without touching the filesystem
    monkeypatch.setattr(ag2, "setup_ag2_path", lambda: True)

    # Patch importlib.import_module used inside ag2 to create a fake autogen package tree
    real_import_module = _importlib.import_module

    def _fake_import_module(name: str):
        if name == "autogen":
            pkg = types.ModuleType("autogen")
            oai = types.ModuleType("autogen.oai")
            client = types.ModuleType("autogen.oai.client")
            setattr(client, "OpenAIResponsesLLMConfigEntry", object)
            sys.modules["autogen"] = pkg
            sys.modules["autogen.oai"] = oai
            sys.modules["autogen.oai.client"] = client
            return pkg
        return real_import_module(name)

    # Patch the global importlib module so ag2's inner import uses our fake
    monkeypatch.setattr(sys.modules["importlib"], "import_module", _fake_import_module)

    try:
        assert ag2.is_ag2_available() is True
    finally:
        # Clean up
        for k in ["autogen", "autogen.oai", "autogen.oai.client"]:
            sys.modules.pop(k, None)


def test_is_ag2_available_negative_setup_fails(monkeypatch):
    """If setup_ag2_path returns False, detection should be False."""
    monkeypatch.setattr(ag2, "setup_ag2_path", lambda: False)
    assert ag2.is_ag2_available() is False


def test_is_ag2_available_negative_import_fails(monkeypatch):
    """If autogen import raises, detection should be False."""
    monkeypatch.setattr(ag2, "setup_ag2_path", lambda: True)

    # Ensure importing autogen will raise
    monkeypatch.setitem(sys.modules, "autogen", None)

    # Remove any existing autogen module reference
    sys.modules.pop("autogen", None)

    assert ag2.is_ag2_available() is False
