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

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import AG2 integration first
from denario.ag2_integration import is_ag2_available, setup_ag2_path

def main():
    """Main execution function."""
    
    print("🚀 Starting Denario with AG2 native GPT-5 reasoning support...")
    
    # Check AG2 availability
    if not is_ag2_available():
        print("❌ AG2 is not available. Please check the submodule installation.")
        return False
    
    print("✅ AG2 with GPT-5 reasoning support detected")
    
    # Set up AG2 path
    setup_ag2_path()
    
    # Import denario components
    from denario import get_results
    from denario.utils import load_project
    
    # Load project context
    project_path = "/workspaces/Denario/project_gemini"
    project = load_project(project_path)
    
    if not project:
        print(f"❌ Failed to load project from {project_path}")
        return False
    
    print(f"✅ Loaded project from {project_path}")
    
    # Configure for AG2 GPT-5 reasoning
    print("🧠 Configuring AG2 GPT-5 reasoning workflow...")
    
    try:
        # Use AG2's native GPT-5 reasoning instead of monkey-patching
        results = get_results(
            project=project,
            engineer_model="gpt-5",      # AG2 will auto-configure reasoning
            researcher_model="gpt-5",    # AG2 will auto-configure reasoning  
            restart_at_step=-1,          # Resume from results generation
            use_ag2=True                 # Enable AG2 native mode
        )
        
        if results:
            print("✅ AG2 GPT-5 reasoning workflow completed successfully!")
            print(f"📊 Results generated with enhanced reasoning capabilities")
            return True
        else:
            print("❌ Workflow failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in AG2 GPT-5 workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
