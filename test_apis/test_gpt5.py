import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

try:
    response = openai.ChatCompletion.create(
        model="gpt-5",  # Replace with the exact model name if needed
        messages=[{"role": "user", "content": "Hello, are you GPT-5?"}],
        max_tokens=10,
    )
    print("GPT-5 response:", response.choices[0].message['content'])
except Exception as e:
    print("Error with GPT-5:", e)
