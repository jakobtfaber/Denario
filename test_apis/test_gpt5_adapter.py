import os
from denario.gpt5_responses_adapter import gpt5_responses_chat_completion


def test_adapter_returns_text():
    # Skip if no key
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set; skipping.")
        return

    messages = [
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "Give me one bullet point about the Moon."},
    ]
    resp = gpt5_responses_chat_completion(
        messages,
        model="gpt-5",  # change to gpt-5-mini if needed
        reasoning_effort="low",
        verbosity="low",
        max_output_tokens=128,
    )

    assert resp.choices and resp.choices[0].message.content
    print("Text:", resp.choices[0].message.content)
    # Optional: show reasoning token usage if present
    print("Reasoning tokens:", resp.usage.completion_tokens_details.reasoning_tokens)
