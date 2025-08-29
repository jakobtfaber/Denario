import os
from dotenv import load_dotenv
from google.generativeai import GenerativeModel, configure

# Load environment variables from .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

configure(api_key=api_key)

models_to_test = ["gemini-2.5-pro", "gemini-2.5-flash"]

for model_name in models_to_test:
    try:
        model = GenerativeModel(model_name)
        response = model.generate_content(["Hello, are you " + model_name + "?"])
        print(f"{model_name} response:", response.text)
    except Exception as e:
        print(f"Error with {model_name}: {e}")
