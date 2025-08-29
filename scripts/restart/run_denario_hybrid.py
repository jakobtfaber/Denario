#!/usr/bin/env python3
"""
Denario Hybrid Pipeline: Gemini-2.5-pro + GPT-5

This script runs the full Denario pipeline with optimal model selection:
- Gemini-2.5-pro for planning/coordination (idea, method)  
- GPT-5 for research/engineering (results, analysis)
- Gemini-2.5-pro for paper writing (consistent with templates)
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable display for non-interactive mode, preventing hangs
os.environ["CMBAGENT_DISABLE_DISPLAY"] = "1"

# Ensure we're using the vendored cmbagent
script_dir = os.path.dirname(__file__)
vendored_path = os.path.join(script_dir, "..", "..", "third_party", "cmbagent")
sys.path.insert(0, vendored_path)

try:
    print("Importing Denario with hybrid configuration...")
    from denario import Denario, Journal
    from denario.llm import models
    print("...Denario imported successfully.")
except ImportError as e:
    print(f"❌ Failed to import Denario: {e}")
    sys.exit(1)


def main():
    """Run the full Denario pipeline with hybrid model configuration."""
    
    # Verify API keys
    required_keys = ["OPENAI_API_KEY", "GOOGLE_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        print(f"❌ Missing required API keys: {', '.join(missing_keys)}")
        sys.exit(1)

    # Project configuration
    project_dir = "project_gemini"
    
    # Load custom prompt
    prompt_path = "config/prompts/dsa2000psr_prompt.md"
    if not os.path.exists(prompt_path):
        # Fallback to old location during transition
        prompt_path = "myprompts/dsa2000psr_prompt.md"
    
    with open(prompt_path, "r") as f:
        data_description = f.read()

    # Configure hybrid model selection
    llm_defaults = {
        # Gemini for planning and coordination
        'idea_maker': models["gemini-2.5-pro"],
        'idea_hater': models["gemini-2.5-pro"],
        'planner': models["gemini-2.5-pro"],
        'plan_reviewer': models["gemini-2.5-pro"],
        
        # GPT-5 for research and engineering
        'engineer': models["gpt-5"],
        'researcher': models["gpt-5"],
        
        # Gemini for paper writing (consistent with templates)
        'default_llm': models["gemini-2.5-pro"],
    }

    print("🔧 Initializing Denario with hybrid configuration:")
    print("   📋 Planning (Gemini-2.5-pro): idea generation, methodology")
    print("   🔬 Research (GPT-5): results analysis, scientific interpretation")
    print("   📝 Writing (Gemini-2.5-pro): paper generation")

    # Initialize Denario with hybrid configuration
    denario = Denario(
        project_dir=project_dir,
        llm_defaults=llm_defaults,
        clear_project_dir=False  # Preserve existing work
    )
    
    denario.set_data_description(data_description)
    print("\n--- Data Description ---")
    denario.show_data_description()

    try:
        # Phase 1: Idea Generation (Gemini-2.5-pro)
        print("\n🧠 Phase 1: Research Idea Generation")
        denario.get_idea(
            idea_maker_model="gemini-2.5-pro",
            idea_hater_model="gemini-2.5-pro"
        )
        denario.show_idea()

        # Phase 2: Methodology (Gemini-2.5-pro)
        print("\n📐 Phase 2: Methodology Development")
        denario.get_method(llm="gemini-2.5-pro")
        denario.show_method()

        # Phase 3: Results (GPT-5 for enhanced reasoning)
        print("\n🔬 Phase 3: Results Analysis (GPT-5 reasoning)")
        denario.get_results(
            engineer_model="gpt-5",
            researcher_model="gpt-5"
        )
        denario.show_results()

        # Phase 4: Paper Generation (skip if requested)
        if os.getenv('SKIP_PAPER') == '1':
            print('📄 SKIP_PAPER set: skipping paper generation')
        else:
            print("\n📝 Phase 4: Paper Draft Generation")
            denario.get_paper(journal=Journal.AAS, llm="gemini-2.5-pro")
            denario.show_paper()

        print("\n✅ Hybrid pipeline completed successfully!")
        print("   🎯 Used optimal models for each phase")
        print("   📊 Check project_gemini/ for all outputs")

    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
