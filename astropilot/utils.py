from .llm import LLM, models
from .key_manager import KeyManager

def input_check(str_input: str) -> str:
    """Check if the input is a string with the desired content or the path markdown file, in which case reads it to get the content."""

    if str_input.endswith(".md"):
        with open(str_input, 'r') as f:
            content = f.read()
    elif isinstance(str_input, str):
        content = str_input
    else:
        raise ValueError("Input must be a string or a path to a markdown file.")
    return content

def llm_parser(llm: LLM | str) -> LLM:
    """Get the LLM instance from a string."""
    if isinstance(llm, str):
        try:
            llm = models[llm]
        except KeyError:
            raise KeyError(f"LLM '{llm}' not available. Please select from: {list(models.keys())}")
    return llm

def get_model_config_from_env(model: str, key_manager: KeyManager):
    """Indicate api key and other options depending on the model"""
    config = {
        "model": model,
        "api_key": None,
        "api_type": None
    }
    
    if 'o3' in model:
        config.update({
            "reasoning_effort": "medium",
            "api_key": key_manager.OPENAI,
            "api_type": "openai"
        })
    elif "gemini" in model:
        config.update({
            "api_key": key_manager.GEMINI, 
            "api_type": "google"
        })
    elif "claude" in model:
        config.update({
            "api_key": key_manager.ANTHROPIC,
            "api_type": "anthropic"
        })
    else:
        config.update({
            "api_key": key_manager.OPENAI,
            "api_type": "openai"
        })
    return config
