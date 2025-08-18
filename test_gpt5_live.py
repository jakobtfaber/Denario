#!/usr/bin/env python3
"""
Quick live test of GPT-5 reasoning with autogen agent.
"""

import os
import sys

# Import and activate integration
from denario.gpt5_integration import install_gpt5_reasoning_support

def test_live_gpt5():
    """Test GPT-5 reasoning with a real API call."""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set")
        return
        
    # Install integration
    install_gpt5_reasoning_support()
    print("GPT-5 integration activated")
    
    import autogen
    
    # Create agent with GPT-5 reasoning config
    gpt5_config = {
        "config_list": [{
            "model": "gpt-5",
            "api_type": "openai",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "reasoning_effort": "medium",
            "verbosity": "low",
            "max_output_tokens": 150
        }]
    }
    
    agent = autogen.ConversableAgent(
        name="gpt5_test",
        llm_config=gpt5_config,
        human_input_mode="NEVER",
    )
    
    messages = [
        {"role": "user", "content": "Write a 2-sentence scientific explanation of photosynthesis."}
    ]
    
    print("Testing GPT-5 reasoning...")
    success, response = agent.generate_oai_reply(messages=messages)
    
    print(f"Success: {success}")
    print(f"Response: {response}")
    
    if success and response and len(response) > 20:
        print("✅ GPT-5 reasoning is working!")
    else:
        print("❌ GPT-5 reasoning failed")

if __name__ == "__main__":
    test_live_gpt5()
