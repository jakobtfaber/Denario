#!/usr/bin/env python3
"""
Restart Denario using GPT-5 reasoning for results generation.

This script resumes from the experiment/results phase using GPT-5's reasoning
capabilities to enhance the quality of scientific analysis and interpretation.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import the Denario system
try:
    print("Importing Denario...")
    from denario import Denario, Journal
    print("...Denario imported.")

except ImportError as e:
    print(f"❌ Failed to import Denario: {e}")
    sys.exit(1)


def main():
    """Resume Denario with GPT-5 reasoning for results generation."""

    # Verify API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set")
        sys.exit(1)
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set") 
        sys.exit(1)

    # Load project data
    project_dir = "project_gemini"

    # Load custom prompt
    with open("config/prompts/dsa2000psr_prompt.md", "r") as f:
        data_description = f.read()

    # Initialize Denario with project directory
    denario = Denario(project_dir=project_dir)
    denario.set_data_description(data_description)

    # Configure models - GPT-5 for research/engineering
    engineer_model = "gpt-5"
    researcher_model = "gpt-5"
    print(f"Engineer model: {engineer_model}")
    print(f"Researcher model: {researcher_model}")

    # Ensure prerequisite files from Gemini exist
    input_dir = os.path.join(project_dir, "input_files")
    idea_md = os.path.join(input_dir, "idea.md")
    method_md = os.path.join(input_dir, "methods.md")
    missing = [p for p in (idea_md, method_md) if not os.path.exists(p)]
    if missing:
        print("ERROR: Missing prerequisite files to resume results generation:")
        for p in missing:
            print(f"   - {p}")
        print("Please run the Gemini idea/method stages first or provide these files.")
        sys.exit(1)

    print("Starting Denario results generation with GPT-5 reasoning...")
    print("   This will leverage advanced reasoning for scientific analysis")

    try:
        # Resume from experiment/results phase using GPT-5
        denario.get_results(
            engineer_model=engineer_model,
            researcher_model=researcher_model,
            restart_at_step=-1  # Resume from beginning of results generation
        )
        print("✅ Results generation completed successfully!")

        # Print results to stdout for confirmation
        if not denario.research.results:
            print("WARNING: No textual results produced; continuing to paper generation with available plots/context.")
        denario.show_results()

        # Optionally skip paper generation when running in CI or when the
        # Google generative API is blocked. Use SKIP_PAPER=1 to bypass.
        if os.getenv('SKIP_PAPER') == '1':
            print('SKIP_PAPER set: skipping paper generation step')
        else:
            # Proceed to paper generation using default writer LLM (Gemini)
            print("\n📝 Generating paper draft from computed results...")
            denario.get_paper(journal=Journal.AAS)
            print("✅ Paper draft generated (see project input_files and output).")

    except Exception as e:
        print(f"❌ ERROR during results generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
