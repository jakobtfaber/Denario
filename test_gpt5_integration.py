#!/usr/bin/env python3
"""
Test GPT-5 reasoning integration with a minimal cmbagent setup.

This tests the integration layer without running a full Denario workflow.
"""

import os
import sys

# Import the integration layer (this auto-installs the monkey patch)
from denario.gpt5_integration import install_gpt5_reasoning_support, is_gpt5_with_reasoning

def test_gpt5_integration():
    """Test basic GPT-5 reasoning integration."""
    
    # Ensure the integration is installed
    success = install_gpt5_reasoning_support()
    print(f"GPT-5 integration installed: {success}")
    
    # Test config detection
    gpt5_config = {
        "config_list": [{
            "model": "gpt-5",
            "api_type": "openai",
            "reasoning_effort": "medium",
            "verbosity": "medium"
        }]
    }
    
    regular_config = {
        "config_list": [{
            "model": "gpt-4",
            "api_type": "openai"
        }]
    }
    
    print(f"GPT-5 config detected: {is_gpt5_with_reasoning(gpt5_config)}")
    print(f"Regular config detected: {is_gpt5_with_reasoning(regular_config)}")
    
    # Test with minimal autogen agent (if API key available)
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set; skipping live test")
        return
    
    try:
        import autogen
        
        agent = autogen.ConversableAgent(
            name="test_gpt5_agent",
            llm_config=gpt5_config,
            human_input_mode="NEVER",
        )
        
        # Test message
        messages = [
            {"role": "user", "content": "Explain quantum entanglement in exactly 2 sentences."}
        ]
        
        print("\nTesting GPT-5 reasoning call...")
        success, response = agent.generate_oai_reply(messages=messages)
        
        print(f"Success: {success}")
        print(f"Response: {response}")
        
        if success and response:
            print("✅ GPT-5 reasoning integration working!")
        else:
            print("❌ GPT-5 reasoning integration failed")
            
    except Exception as e:
        print(f"Live test failed: {e}")


if __name__ == "__main__":
    test_gpt5_integration()
