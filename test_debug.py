#!/usr/bin/env python3
"""Simple test to debug the current state."""

import sys
import os
from pathlib import Path

print("🔍 Starting debug test...")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Test basic imports
try:
    print("Testing basic imports...")
    from denario.gpt5_integration import install_gpt5_reasoning_support
    print("✅ GPT-5 integration import successful")
    
    success = install_gpt5_reasoning_support()
    print(f"✅ GPT-5 integration activated: {success}")
    
except Exception as e:
    print(f"❌ GPT-5 integration failed: {e}")
    import traceback
    traceback.print_exc()

# Test vendored cmbagent
try:
    print("\nTesting vendored cmbagent...")
    third_party_path = str(Path(__file__).resolve().parent / "third_party")
    original_path = sys.path.copy()
    sys.path.insert(0, third_party_path)
    
    import cmbagent
    print("✅ Vendored cmbagent imported successfully")
    
    import cmbagent.utils as cu
    print(f"Default LLM model: {cu.default_llm_model}")
    print(f"Engineer model default: {cu.default_agents_llm_model.get('engineer', 'NOT_SET')}")
    
    sys.path[:] = original_path
    print("✅ sys.path restored")
    
except Exception as e:
    print(f"❌ Vendored cmbagent failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 Debug test completed")
