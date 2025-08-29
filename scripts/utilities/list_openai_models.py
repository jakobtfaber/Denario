import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    models = openai.models.list()
    print("OpenAI models available to your API key:")
    for model in models.data:
        print(model.id)
except Exception as e:
    print("Error listing OpenAI models:", e)
