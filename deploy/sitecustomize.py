"""
Runtime shim to ensure gpt-5-mini appears in DenarioApp dropdowns.

Python automatically imports `sitecustomize` if present on sys.path.
We use this hook to add a safe default entry to `denario.models` when missing.
"""

try:
    from denario.llm import LLM
    from denario import models as _denario_models

    if isinstance(_denario_models, dict) and "gpt-5-mini" not in _denario_models:
        # Use temperature=1.0 because gpt-5* only supports default temperature upstream.
        _denario_models["gpt-5-mini"] = LLM(name="gpt-5-mini", max_output_tokens=16384, temperature=1.0)
except (ImportError, AttributeError, TypeError):
    # Stay silent if package layout changes or import fails; this is a best-effort shim.
    pass

