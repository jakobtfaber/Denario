"""
GPT-5 Responses API integration layer for autogen/cmbagent.

This module provides a minimal monkey-patch to handle GPT-5 reasoning
via the Responses API while preserving existing autogen/cmbagent workflows.
"""

import os
import logging
from typing import Any, Dict, List, Optional
from unittest.mock import patch

from denario.gpt5_responses_adapter import gpt5_responses_chat_completion

logger = logging.getLogger(__name__)


def _extract_model_from_llm_config(config: Any) -> str:
    """Best-effort extraction of model name from autogen llm_config."""
    try:
        # Common dict shape
        if isinstance(config, dict):
            config_list = (
                config.get("config_list")
                or config.get("config")
                or []
            )
            if isinstance(config_list, list) and config_list:
                first = config_list[0]
                if isinstance(first, dict):
                    return first.get("model", "") or first.get("name", "")
                return getattr(first, "model", "") or getattr(first, "name", "")
        # Object with attributes (e.g., pydantic model)
        config_list = getattr(config, "config_list", None) or getattr(config, "config", None)
        if isinstance(config_list, list) and config_list:
            first = config_list[0]
            if isinstance(first, dict):
                return first.get("model", "") or first.get("name", "")
            return getattr(first, "model", "") or getattr(first, "name", "")
    except Exception:
        pass
    return ""


def is_gpt5_with_reasoning(config: Any) -> bool:
    """Check if this config should use GPT-5 Responses API."""
    model = _extract_model_from_llm_config(config)
    return isinstance(model, str) and model.startswith("gpt-5")


def create_gpt5_interceptor(original_method):
    """Create an interceptor that routes GPT-5+reasoning to Responses API."""

    def interceptor(self, messages=None, sender=None, config=None):
        # Check if this should use GPT-5 reasoning
        llm_config = getattr(self, "llm_config", None)

        # Auto-configure GPT-5 reasoning if not already set
        if llm_config and is_gpt5_model(llm_config) and not has_reasoning_config(llm_config):
            inject_gpt5_reasoning_config(llm_config)

        if llm_config and is_gpt5_with_reasoning(llm_config):
            logger.info("Routing to GPT-5 Responses API for reasoning")
            return handle_gpt5_reasoning_call(self, messages, sender, config)
        else:
            # Standard autogen behavior
            return original_method(self, messages, sender, config)

    return interceptor


def is_gpt5_model(config: Any) -> bool:
    """Check if this config uses a GPT-5 model."""
    model = _extract_model_from_llm_config(config)
    return isinstance(model, str) and model.startswith("gpt-5")


def has_reasoning_config(config: Any) -> bool:
    """Consider GPT-5 models as requiring reasoning routing regardless of prior config."""
    return is_gpt5_model(config)


def inject_gpt5_reasoning_config(config: Any) -> None:
    """Inject default GPT-5 reasoning configuration."""
    try:
        # Remove unsupported parameters for GPT-5 if present in common shapes
        if isinstance(config, dict):
            cfg = config
            first = None
            cl = cfg.get("config_list") or cfg.get("config")
            if isinstance(cl, list) and cl:
                first = cl[0]
            for key in ("temperature", "top_p"):
                if key in cfg:
                    cfg.pop(key, None)
                if isinstance(first, dict) and key in first:
                    first.pop(key, None)
        else:
            # Object-like; attempt attribute cleanup on top-level only
            for key in ("temperature", "top_p"):
                if hasattr(config, key):
                    try:
                        setattr(config, key, None)
                    except Exception:
                        pass
        logger.info("Auto-configured GPT-5: removed temperature/top_p")
    except Exception:
        pass


def handle_gpt5_reasoning_call(agent_instance, messages=None, sender=None, config=None):
    """Handle GPT-5 reasoning API call and return autogen-compatible response."""

    if not messages:
        logger.warning("No messages found in GPT-5 reasoning call")
        return False, None

    # Get config details from agent's llm_config
    agent_config = agent_instance.llm_config["config_list"][0]
    model = agent_config.get("model", "gpt-5")

    # Check for reasoning config in separate section first, then inline
    gpt5_reasoning = agent_instance.llm_config.get("gpt5_reasoning", {})
    reasoning_effort = (gpt5_reasoning.get("reasoning_effort") or
                       agent_config.get("reasoning_effort", "medium"))
    verbosity = (gpt5_reasoning.get("verbosity") or
                agent_config.get("verbosity", "medium"))
    max_output_tokens = (gpt5_reasoning.get("max_output_tokens") or
                        agent_config.get("max_output_tokens", 2048))

    try:
        # Call our adapter
        response = gpt5_responses_chat_completion(
            messages=messages,
            model=model,
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
            max_output_tokens=max_output_tokens,
        )

        # Return in autogen's expected format: (bool, response)
        # autogen expects the message content as a string
        content = response.choices[0].message.content if response.choices else ""
        return True, content

    except Exception as e:
        logger.error(f"GPT-5 Responses API call failed: {e}")
        # Return failure - autogen will handle fallback
        return False, None


def install_gpt5_reasoning_support():
    """Install GPT-5 reasoning support into autogen ConversableAgent."""

    try:
        from autogen import ConversableAgent

        # Target the correct method that handles OpenAI API calls
        original_generate_reply = getattr(ConversableAgent, "generate_oai_reply", None)

        if original_generate_reply:
            # Monkey-patch the method
            ConversableAgent.generate_oai_reply = create_gpt5_interceptor(original_generate_reply)
            logger.info("GPT-5 reasoning support installed successfully")
            return True
        else:
            logger.warning("Could not find generate_oai_reply method for GPT-5 integration")
            return False

    except Exception as e:
        logger.error(f"Failed to install GPT-5 reasoning support: {e}")
        return False


def remove_gpt5_reasoning_support():
    """Remove GPT-5 reasoning support (restore original behavior)."""
    # Implementation would restore original methods if needed
    pass


# Auto-install on import (can be disabled by setting env var)
if os.getenv("DENARIO_DISABLE_GPT5_AUTO_INSTALL") != "1":
    install_gpt5_reasoning_support()
