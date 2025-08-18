import os
from dotenv import load_dotenv
from denario import Denario, Journal

# Load environment variables
load_dotenv()

project_dir = "project_gemini"

# Load your custom prompt
with open("myprompts/dsa2000psr_prompt.md", "r") as f:
    data_description = f.read()

den = Denario(project_dir=project_dir)

den.set_data_description(data_description)
print("\n--- Data Description ---\n")
den.show_data_description()

print("\n--- Research Idea ---\n")
den.get_idea(idea_maker_model="gemini-2.5-pro", idea_hater_model="gemini-2.5-pro")
den.show_idea()

print("\n--- Methodology ---\n")
den.get_method()  # If you want to force model, update Method class or use get_method_fast
# den.get_method_fast(llm="gemini-2.5-pro")  # Uncomment if you want to use the fast method

den.show_method()

print("\n--- Results ---\n")
den.get_results(engineer_model="gemini-2.5-pro", researcher_model="gemini-2.5-pro")
den.show_results()

print("\n--- Paper Draft ---\n")
den.get_paper(journal=Journal.AAS, llm="gemini-2.5-pro")
den.show_paper()
