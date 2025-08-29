import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

try:
    # As of 2025, Anthropic's Python SDK does not provide a direct model listing endpoint.
    # Instead, we can test a set of known model names and report which ones work.
    model_names = [
        "claude-opus-4.x",           # Claude Opus 4.x
        "claude-sonnet-4",           # Claude Sonnet 4
        "claude-sonnet-3.7",         # Claude Sonnet 3.7
        "claude-sonnet-3.5-2024-10-22", # Claude Sonnet 3.5 2024-10-22
        "claude-haiku-3.5",          # Claude Haiku 3.5
        "claude-sonnet-3.5-2024-06-20", # Claude Sonnet 3.5 2024-06-20
        "claude-haiku-3"              # Claude Haiku 3
    ]
    print("Testing Anthropic model access:")
    for model in model_names:
        try:
            response = client.messages.create(
                model=model,
                max_tokens=5,
                messages=[{"role": "user", "content": "Hello"}],
            )
            print(f"Access: {model}")
        except Exception as e:
            print(f"No access: {model} ({e})")
except Exception as e:
    print("Error testing Anthropic models:", e)
