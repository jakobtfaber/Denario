#!/usr/bin/env python3
"""
Restart Denario using GPT-5 reasoning for results generation.

This script resumes from the experiment/results phase using GPT-5's reasoning
capabilities to enhance the quality of scientific analysis and interpretation.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use installed packages; no path mangling required

# Import GPT-5 integration (auto-installs monkey patch)
from denario.gpt5_integration import install_gpt5_reasoning_support
from denario import Denario, Journal
from denario.utils import llm_parser

def main():
    """Resume Denario with GPT-5 reasoning for results generation."""
    
    # Ensure GPT-5 integration is active
    success = install_gpt5_reasoning_support()
    if success:
        print("✅ GPT-5 reasoning integration activated")
    else:
        print("⚠️  GPT-5 integration failed - falling back to standard behavior")
    
    # Verify API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set")
        sys.exit(1)
    
    # Load project data
    project_dir = "project_gemini"
    
    # Load custom prompt
    with open("myprompts/dsa2000psr_prompt.md", "r") as f:
        data_description = f.read()
    
    # Initialize Denario with project directory
    denario = Denario(project_dir=project_dir)
    denario.set_data_description(data_description)

    # Ensure prerequisite files from Gemini exist
    input_dir = os.path.join(project_dir, "input_files")
    idea_md = os.path.join(input_dir, "idea.md")
    method_md = os.path.join(input_dir, "methods.md")
    missing = [p for p in (idea_md, method_md) if not os.path.exists(p)]
    if missing:
        print("❌ Missing prerequisite files to resume results generation:")
        for p in missing:
            print(f"   - {p}")
        print("Please run the Gemini idea/method stages first or provide these files.")
        sys.exit(1)
    
    print("🚀 Starting Denario results generation with GPT-5 reasoning...")
    print("   This will leverage advanced reasoning for scientific analysis")
    
    try:
        # Resume from experiment/results phase using GPT-5
        # The GPT-5 integration will automatically add reasoning_effort when GPT-5 is detected
        denario.get_results(
            engineer_model="gpt-5",      # GPT-5 for engineering analysis
            researcher_model="gpt-5",    # GPT-5 for research analysis
            restart_at_step=-1           # Resume from beginning of results generation
        )
        print("✅ Results generation completed successfully!")
        
        # Print results to stdout for confirmation
        if not denario.research.results:
            print("⚠️ No textual results produced; continuing to paper generation with available plots/context.")
        denario.show_results()

        # Proceed to paper generation using default writer LLM (Gemini)
        print("\n📝 Generating paper draft from computed results…")
        denario.get_paper(journal=Journal.AAS)
        print("✅ Paper draft generated (see project input_files and output).")
        
    except Exception as e:
        print(f"❌ Error during results generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
