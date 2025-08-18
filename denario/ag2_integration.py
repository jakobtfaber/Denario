"""
AG2 (next-generation autogen) integration for native GPT-5 reasoning support.

This module provides a clean interface to AG2's built-in GPT-5 reasoning capabilities,
eliminating the need for monkey-patching and custom API adapters.
"""

import logging
import sys
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def setup_ag2_path():
    """Add AG2 to Python path for import."""
    ag2_path = Path(__file__).parent.parent / "third_party" / "ag2"
    if ag2_path.exists():
        sys.path.insert(0, str(ag2_path))
        logger.info(f"Added AG2 path: {ag2_path}")
        return True
    else:
        logger.warning(f"AG2 path not found: {ag2_path}")
        return False

def create_gpt5_reasoning_config(
    model: str = "gpt-5",
    reasoning_effort: str = "medium",
    verbosity: str = "medium",
    **kwargs
) -> dict:
    """
    Create AG2 native config for GPT-5 reasoning.
    
    Args:
        model: GPT-5 model name
        reasoning_effort: "low", "minimal", "medium", or "high"
        verbosity: "low", "medium", or "high"
        **kwargs: Additional config parameters
        
    Returns:
        AG2-compatible config dict with native GPT-5 reasoning support
    """
    
    # AG2 native GPT-5 reasoning config
    config = {
        "config_list": [
            {
                "api_type": "responses",  # Uses responses API automatically
                "model": model,
                "reasoning_effort": reasoning_effort,
                "verbosity": verbosity,
                "api_key": os.getenv("OPENAI_API_KEY"),
                **kwargs
            }
        ],
        "timeout": 300,  # GPT-5 reasoning can take longer
    }
    
    logger.info(f"Created AG2 GPT-5 config: model={model}, effort={reasoning_effort}, verbosity={verbosity}")
    return config

def is_ag2_available() -> bool:
    """Check if AG2 is available and can be imported.

    Simpler detection: ensure AG2 path is added, then try importing the
    expected AG2 symbols. This avoids brittle filesystem path string checks
    in environments with differing import semantics.
    """
    try:
        # Ensure AG2 path is present
        if not setup_ag2_path():
            return False

        # If autogen was already imported, remove it so we pick up AG2
        if "autogen" in sys.modules:
            try:
                del sys.modules["autogen"]
            except Exception:
                pass

        # Try importing AG2's autogen and the Responses client class
        import importlib
        autogen = importlib.import_module("autogen")
        from autogen.oai.client import OpenAIResponsesLLMConfigEntry  # type: ignore
        logger.info("AG2 with GPT-5 reasoning support is available")
        return True
    except Exception as e:
        logger.warning(f"AG2 not available: {e}")
        return False

def create_ag2_agent(
    name: str,
    system_message: str,
    model: str = "gpt-5",
    reasoning_effort: str = "medium",
    verbosity: str = "medium",
    **kwargs
):
    """
    Create an AG2 ConversableAgent with GPT-5 reasoning.
    
    Args:
        name: Agent name
        system_message: System message for the agent
        model: GPT-5 model name
        reasoning_effort: Reasoning effort level
        verbosity: Verbosity level
        **kwargs: Additional agent parameters
        
    Returns:
        AG2 ConversableAgent configured for GPT-5 reasoning
    """
    
    if not is_ag2_available():
        raise ImportError("AG2 is not available. Please ensure it's properly installed as a submodule.")
    
    from autogen import ConversableAgent
    
    # Create native AG2 GPT-5 config
    llm_config = create_gpt5_reasoning_config(
        model=model,
        reasoning_effort=reasoning_effort,
        verbosity=verbosity
    )
    
    agent = ConversableAgent(
        name=name,
        system_message=system_message,
        llm_config=llm_config,
        **kwargs
    )
    
    logger.info(f"Created AG2 agent '{name}' with GPT-5 reasoning")
    return agent

def upgrade_cmbagent_to_ag2(cmbagent_config: dict) -> dict:
    """
    Convert cmbagent config to AG2 format with GPT-5 reasoning support.
    
    Args:
        cmbagent_config: Original cmbagent configuration
        
    Returns:
        AG2-compatible configuration with GPT-5 reasoning
    """
    
    # Extract model from config
    config_list = cmbagent_config.get("config_list", [{}])
    first_config = config_list[0] if config_list else {}
    model = first_config.get("model", "gpt-5")
    
    # Check if this should use GPT-5 reasoning
    if model.startswith("gpt-5"):
        # Convert to AG2 native reasoning config
        reasoning_effort = "medium"  # Default
        verbosity = "medium"  # Default
        
        # Preserve other settings
        ag2_config = create_gpt5_reasoning_config(
            model=model,
            reasoning_effort=reasoning_effort,
            verbosity=verbosity
        )
        
        # Copy other settings from original config
        for key, value in cmbagent_config.items():
            if key not in ["config_list"]:
                ag2_config[key] = value
                
        logger.info(f"Upgraded cmbagent config to AG2 with GPT-5 reasoning")
        return ag2_config
    else:
        # Non-GPT-5 models can use original config
        return cmbagent_config

if __name__ == "__main__":
    # Test AG2 availability
    if is_ag2_available():
        print("✅ AG2 with GPT-5 reasoning support is available")
        
        # Test config creation
        config = create_gpt5_reasoning_config()
        print(f"✅ Created GPT-5 config: {config}")
        
    else:
        print("❌ AG2 is not available")
