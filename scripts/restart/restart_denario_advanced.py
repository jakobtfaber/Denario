import os
from dotenv import load_dotenv
from denario import Denario, Journal

# Load environment variables
load_dotenv()

project_dir = "project_gemini"

# Load your custom prompt
with open("myprompts/dsa2000psr_prompt.md", "r") as f:
    data_description = f.read()

print("=== Denario Restart Script ===")
print("Available restart options:")
print("1. Restart from beginning of results generation (safest)")
print("2. Restart from step 1 of results generation")
print("3. Restart from step 2 of results generation") 
print("4. Restart from step 3 of results generation")
print("5. Restart from step 4 of results generation")
print("6. Restart from step 5 of results generation")
print("7. Restart from step 6 of results generation")

choice = input("\nEnter your choice (1-7): ")

# Initialize Denario
den = Denario(project_dir=project_dir)
den.set_data_description(data_description)

restart_step = -1  # Default: full restart
if choice == "1":
    restart_step = -1
    print("Restarting from beginning of results generation...")
elif choice == "2":
    restart_step = 1
    print("Restarting from step 1...")
elif choice == "3":
    restart_step = 2
    print("Restarting from step 2...")
elif choice == "4":
    restart_step = 3
    print("Restarting from step 3...")
elif choice == "5":
    restart_step = 4
    print("Restarting from step 4...")
elif choice == "6":
    restart_step = 5
    print("Restarting from step 5...")
elif choice == "7":
    restart_step = 6
    print("Restarting from step 6...")
else:
    print("Invalid choice, using default (full restart)")

print(f"\n--- Starting Results Generation with GPT-5 (restart_at_step={restart_step}) ---\n")

# This will automatically load existing idea and methodology files
# and proceed with results generation from the specified step using GPT-5
den.get_results(
    engineer_model="gpt-5", 
    researcher_model="gpt-5",
    restart_at_step=restart_step
)
den.show_results()

print("\n--- Paper Draft ---\n")
den.get_paper(journal=Journal.AAS, llm="gemini-2.5-pro")
den.show_paper()
