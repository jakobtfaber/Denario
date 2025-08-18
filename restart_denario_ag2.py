#!/usr/bin/env python3
"""
Restart Denario workflow using AG2's native GPT-5 reasoning support.

This script uses AG2 (next-generation autogen) which has built-in support for 
GPT-5 reasoning API, eliminating the need for monkey-patching.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use installed packages; no path mangling required

# Verify AG2 (autogen) availability via installed package
def _check_ag2_available() -> bool:
    try:
        import autogen  # provided by ag2
        # Light sanity check: presence of oai.client
        from autogen.oai import client as _client  # noqa: F401
        return True
    except Exception:
        return False

def main():
    """Main execution function."""
    
    print("🚀 Starting Denario with AG2 native GPT-5 reasoning support...")
    
    # Check AG2 availability
    if not _check_ag2_available():
        print("❌ AG2 is not available. Please check the submodule installation.")
        return False
    
    print("✅ AG2 with GPT-5 reasoning support detected")
    
    # AG2 provided via installed dependency; no path setup needed
    
    # Import Denario and run results with GPT-5
    try:
        from denario import Denario
        from denario.utils import input_check

        project_dir = "project_gemini"
        # Load a default prompt file if present; otherwise use a minimal prompt
        prompt_path = Path("myprompts/dsa2000psr_prompt.md")
        if prompt_path.exists():
            data_description = prompt_path.read_text()
        else:
            data_description = "Analyze the provided dataset and generate results using standard scientific methods."

        den = Denario(project_dir=project_dir)
        den.set_data_description(data_description)

        print("🧠 Running results generation with GPT-5 via AG2…")
        den.get_results(
            engineer_model="gpt-5",
            researcher_model="gpt-5",
            restart_at_step=-1,
        )
        den.show_results()
        print("✅ AG2 GPT-5 reasoning workflow completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error in AG2 GPT-5 workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
