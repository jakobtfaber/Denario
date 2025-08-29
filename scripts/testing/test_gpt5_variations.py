import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("/workspaces/Denario/.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Testing GPT-5 with various parameter combinations...")

# Test 1: Try with reasoning_effort parameter in extra_body
print("\n=== Test 1: With reasoning_effort in extra_body ===")
try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": "Explain the mathematical concept behind Bayesian inference in 2-3 sentences."}],
        max_completion_tokens=150,
        extra_body={"reasoning": {"effort": "medium"}, "text": {"verbosity": "medium"}}
    )
    print("SUCCESS!")
    print("Response:", response.choices[0].message.content)
    print("Reasoning tokens:", response.usage.completion_tokens_details.reasoning_tokens)
except Exception as e:
    print("FAILED:", e)

# Test 2: Try with different system prompt
print("\n=== Test 2: With explicit instruction to show reasoning ===")
try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Always provide your reasoning and then your final answer."},
            {"role": "user", "content": "What is 15 * 23?"}
        ],
        max_completion_tokens=100,
    )
    print("SUCCESS!")
    print("Response:", response.choices[0].message.content)
    print("Reasoning tokens:", response.usage.completion_tokens_details.reasoning_tokens)
except Exception as e:
    print("FAILED:", e)

# Test 3: Try with temperature
print("\n=== Test 3: With temperature adjustment ===")
try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": "Hello, please respond with a simple greeting."}],
        max_completion_tokens=50,
        temperature=0.7
    )
    print("SUCCESS!")
    print("Response:", response.choices[0].message.content)
    print("Reasoning tokens:", response.usage.completion_tokens_details.reasoning_tokens)
except Exception as e:
    print("FAILED:", e)
