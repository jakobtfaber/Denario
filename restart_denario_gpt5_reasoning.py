#!/usr/bin/env python3
"""
Restart Denario using GPT-5 reasoning for results generation.

This script resumes from the experiment/results phase using GPT-5's reasoning
capabilities to enhance the quality of scientific analysis and interpretation.
"""

import os
import sys

# --- Force use of vendored cmbagent ---
# This ensures the correctly configured version is used, not the installed one.
# It MUST be done before any denario imports.
# The cmbagent package is nested: third_party/cmbagent/cmbagent/
third_party_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'third_party', 'cmbagent'))
if third_party_path not in sys.path:
    sys.path.insert(0, third_party_path)
    
# Verify the path modification
print(f"[DEBUG] sys.path[0] = {sys.path[0]}")
print(f"[DEBUG] third_party_path = {third_party_path}")

# Pre-import cmbagent to ensure correct version is loaded
try:
    import cmbagent
    print(f"[DEBUG] cmbagent loaded from: {cmbagent.__file__}")
except Exception as e:
    print(f"[DEBUG] Failed to pre-import cmbagent: {e}")
# --- End force vendored cmbagent ---

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use installed packages; no path mangling required



# Load environment variables from .env file
load_dotenv()

# Use installed packages; no path mangling required
try:
    print("Importing gpt5_integration...")
    from denario.gpt5_integration import install_gpt5_reasoning_support
    print("...gpt5_integration imported.")
    
    print("Importing Denario...")
    from denario import Denario, Journal
    print("...Denario imported.")

    print("Importing llm_parser...")
    from denario.utils import llm_parser
    print("...llm_parser imported.")

except ImportError as e:
    print(f"❌ Failed to import a module: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"❌ An unexpected error occurred during imports: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


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
        print("📝 Generating paper draft from computed results…")
        denario.get_paper(journal=Journal.AAS)
        print("✅ Paper draft generated (see project input_files and output).")
        
    except Exception as e:
        print(f"❌ Error during results generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

import os
import sys
from dotenv import load_dotenv

# --- Force use of vendored cmbagent ---
# This ensures the correctly configured version is used, not the installed one.
# It MUST be done before any denario imports.
third_party_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'third_party'))
if third_party_path not in sys.path:
    sys.path.insert(0, third_party_path)
# --- End force vendored cmbagent ---

# Load environment variables from .env file
load_dotenv()

# Use installed packages; no path mangling required

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use installed packages; no path mangling required

# Import GPT-5 integration (auto-installs monkey patch)
try:
    print("Importing gpt5_integration...")
    from denario.gpt5_integration import install_gpt5_reasoning_support
    print("...gpt5_integration imported.")
    
    print("Importing Denario...")
    from denario import Denario, Journal
    print("...Denario imported.")

    print("Importing llm_parser...")
    from denario.utils import llm_parser
    print("...llm_parser imported.")

except ImportError as e:
    print(f"❌ Failed to import a module: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"❌ An unexpected error occurred during imports: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


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
