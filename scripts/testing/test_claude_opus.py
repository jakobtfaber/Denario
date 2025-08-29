import os
from dotenv import load_dotenv
import anthropic

#load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

try:
    # Use a known working model ID (e.g., "claude-3-sonnet-20240229" or check Anthropic docs for current IDs)
    response = client.messages.create(
        model="claude-opus-4-1-20250805",
        model="claude-sonnet-4-20250514",
        max_tokens=5,
        messages=[{"role": "user", "content": "ping"}],
    )
    print("API key is valid. Response:", response.content)
except Exception as e:
    print("API key may be invalid or model name is wrong:", e)