import importlib.util
import sys
from pathlib import Path
import types

# Load ag2_integration directly by path to avoid importing denario package
_ag2_path = Path(__file__).resolve().parents[1] / "denario" / "ag2_integration.py"
spec = importlib.util.spec_from_file_location("ag2_integration", str(_ag2_path))
ag2 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(ag2)  # type: ignore
is_ag2_available = ag2.is_ag2_available
setup_ag2_path = ag2.setup_ag2_path


def test_restart_flow_happy_path(monkeypatch):
    # Simulate successful setup
    monkeypatch.setattr(ag2, 'setup_ag2_path', lambda: True)

    # Simulate autogen import
    # Provide fake autogen via patched importlib used inside ag2
    import importlib as _importlib
    real_import_module = _importlib.import_module

    def _fake_import_module(name: str):
        if name == 'autogen':
            pkg = types.ModuleType('autogen')
            oai = types.ModuleType('autogen.oai')
            client = types.ModuleType('autogen.oai.client')
            setattr(client, 'OpenAIResponsesLLMConfigEntry', object)
            sys.modules['autogen'] = pkg
            sys.modules['autogen.oai'] = oai
            sys.modules['autogen.oai.client'] = client
            return pkg
        return real_import_module(name)

    # Patch global importlib so ag2 uses fake autogen
    monkeypatch.setattr(sys.modules['importlib'], 'import_module', _fake_import_module)

    try:
        assert is_ag2_available() is True
        assert setup_ag2_path() is True
    finally:
        sys.modules.pop('autogen', None)
        sys.modules.pop('autogen.oai.client', None)


def test_restart_flow_negative(monkeypatch):
    monkeypatch.setattr(ag2, 'setup_ag2_path', lambda: False)
    assert is_ag2_available() is False
