"""
Lightweight adapter to use GPT-5 Responses API in a chat-completions-like way.

Goal:
- Provide a minimal wrapper so existing call sites that expect
  response.choices[0].message.content can work with GPT-5 reasoning.

This does NOT modify autogen/cmbagent. It’s a PoC to confirm we can
map Responses API outputs into the familiar chat-completions shape.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import os

try:
    from dotenv import load_dotenv
except Exception:  # Optional dependency; we handle absence gracefully
    def load_dotenv(*args, **kwargs):
        return False

try:
    from openai import OpenAI
except Exception as e:  # Provide a helpful error if openai is missing
    OpenAI = None  # type: ignore


# Simple dataclasses to mimic OpenAI chat completions response shape
@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class Choice:
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


@dataclass
class UsageDetails:
    reasoning_tokens: int = 0


@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    completion_tokens_details: UsageDetails = field(default_factory=UsageDetails)


@dataclass
class ChatCompletionLike:
    id: str
    model: str
    choices: List[Choice]
    usage: Usage


def _concat_messages_as_prompt(messages: List[Dict[str, str]]) -> str:
    """Flatten chat messages into a single textual prompt for Responses API.

    Note: This is a pragmatic choice. For best results, you may want to
    preserve system vs user roles more formally, or format with tags.
    """
    parts: List[str] = []
    for msg in messages:
        role = msg.get("role", "user").strip()
        content = msg.get("content", "").strip()
        if not content:
            continue
        # Simple tagged format
        parts.append(f"[{role.upper()}]\n{content}\n")
    return "\n".join(parts).strip()


def gpt5_responses_chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gpt-5",
    *,
    verbosity: str = "medium",  # low | medium | high
    reasoning_effort: str = "medium",  # minimal | low | medium | high
    max_output_tokens: int = 512,
    api_key: Optional[str] = None,
) -> ChatCompletionLike:
    """Call GPT-5 via Responses API and return a chat-completions-like object.

    Args:
        messages: Standard chat messages list: [{"role": "user|system|assistant", "content": "..."}, ...]
        model: GPT-5 family model name, e.g., "gpt-5", "gpt-5-mini", "gpt-5-nano".
        verbosity: GPT-5 text verbosity hint.
        reasoning_effort: GPT-5 reasoning effort hint.
        max_output_tokens: Upper bound on output tokens (Responses API respects limits differently).
        api_key: Optional override for OPENAI_API_KEY.

    Returns:
        ChatCompletionLike object with choices[0].message.content populated.
    """
    # Load env if present; allow explicit override.
    load_dotenv(os.getenv("DENARIO_ENV_FILE", ".env"))
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set for GPT-5 Responses API.")

    if OpenAI is None:
        raise RuntimeError(
            "The 'openai' package is required for GPT-5 Responses API. Please install 'openai'."
        )

    client = OpenAI(api_key=key)

    # Flatten messages to a single input string
    input_text = _concat_messages_as_prompt(messages)

    # Call Responses API with reasoning + text controls
    result = client.responses.create(
        model=model,
        input=input_text,
        reasoning={"effort": reasoning_effort},
        text={"verbosity": verbosity},
        # Some SDK variants accept this; if ignored, API will cap appropriately.
        max_output_tokens=max_output_tokens,
    )

    # Extract plain text robustly (works across SDK variants)
    text: str = getattr(result, "output_text", "") or ""
    if not text:
        # Fallback parse across possible shapes
        parts: List[str] = []
        items = getattr(result, "output", None) or []
        for item in items:
            if getattr(item, "type", None) == "message":
                for c in getattr(item, "content", None) or []:
                    if getattr(c, "type", None) in ("output_text", "text"):
                        parts.append(getattr(c, "text", ""))
        text = "".join(parts)

    # Build a chat-completions-like object
    choice = Choice(
        index=0,
        message=ChatMessage(role="assistant", content=text),
        finish_reason=None,
    )

    # Map usage if present
    usage = Usage()
    usage_obj = getattr(result, "usage", None)
    if usage_obj is not None:
        try:
            usage.prompt_tokens = getattr(usage_obj, "input_tokens", 0) or 0
            usage.completion_tokens = getattr(usage_obj, "output_tokens", 0) or 0
            usage.total_tokens = getattr(usage_obj, "total_tokens", 0) or (
                usage.prompt_tokens + usage.completion_tokens
            )
            # Reasoning tokens subfield (if provided)
            details = getattr(usage_obj, "output_tokens_details", None)
            if details is not None:
                usage.completion_tokens_details = UsageDetails(
                    reasoning_tokens=getattr(details, "reasoning_tokens", 0) or 0
                )
        except Exception:
            # Best-effort mapping; don’t fail the call due to usage parsing
            pass

    return ChatCompletionLike(
        id=getattr(result, "id", "responses"),
        model=model,
        choices=[choice],
        usage=usage,
    )


__all__ = [
    "gpt5_responses_chat_completion",
    "ChatCompletionLike",
]
