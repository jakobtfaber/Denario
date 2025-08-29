"""
Basic AG2 availability test to ensure the pinned dependency is importable
and exposes expected modules for cmbagent to use.
"""

def test_ag2_importable():
    try:
        import autogen  # provided by ag2
        from autogen.oai import client as _client  # noqa: F401
    except Exception as e:
        raise AssertionError(f"AG2 (autogen) not importable: {e}")
