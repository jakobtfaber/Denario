import os
from dotenv import load_dotenv
from denario import Denario, Journal

# Load environment variables
load_dotenv()

project_dir = "project_gemini"

# Load your custom prompt
with open("myprompts/dsa2000psr_prompt.md", "r") as f:
    data_description = f.read()

# Initialize Denario with existing project directory
# This will automatically detect and load existing generated content
den = Denario(project_dir=project_dir)

den.set_data_description(data_description)

print("\n--- Restarting from Results Generation ---\n")
print("Note: Idea and methodology will be automatically loaded from existing files")
print("Using GPT-4.5 for results generation to avoid Gemini protobuf issues")

# This will automatically load the existing idea and methodology files
# and proceed with results generation using GPT-4.5 (more reliable than GPT-5)
den.get_results(engineer_model="gpt-4.5", researcher_model="gpt-4.5")
den.show_results()

print("\n--- Paper Draft ---\n")
den.get_paper(journal=Journal.AAS, llm="gemini-2.5-pro")
den.show_paper()
