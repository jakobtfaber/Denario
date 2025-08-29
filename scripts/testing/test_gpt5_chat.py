import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("/workspaces/Denario/.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Testing GPT-5 with standard chat completions API...")

try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": "Write a very short greeting. Just say hello."}],
        max_completion_tokens=50,
    )
    print("SUCCESS with chat.completions!")
    print("Response:", response.choices[0].message.content)
    print("Usage:", response.usage)
except Exception as e:
    print("FAILED with chat.completions:")
    print("Error:", e)
