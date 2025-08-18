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

# Add paths for Denario and cmbagent
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('./third_party/cmbagent'))

# Import GPT-5 integration (auto-installs monkey patch)
from denario.gpt5_integration import install_gpt5_reasoning_support
from denario import Denario
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
        
        # Show results
        denario.show_results()
        
    except Exception as e:
        print(f"❌ Error during results generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
