# test_gpt5.py
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv("/workspaces/Denario/.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

result = client.responses.create(
    model="gpt-5",
    input="Write a haiku about code.",
    reasoning={ "effort": "low" },
    text={ "verbosity": "low" },
)

# Safe extraction across SDK variants and output shapes
text = result.output_text
if not text:
    parts = []
    for item in (resp.output or []):
        if getattr(item, "type", None) == "message":
            for c in (getattr(item, "content", None) or []):
                if getattr(c, "type", None) in ("output_text", "text"):
                    parts.append(getattr(c, "text", ""))
    text = "".join(parts)

print("Items:", [getattr(o, "type", None) for o in (result.output or [])])
print("Text:", text)
print("Usage:", result.usage)
