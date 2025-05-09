import time
from astropilot.langgraph_agents.agents_graph import build_idea
from astropilot.key_manager import KeyManager
from astropilot.llm import LLM

# Start timer
start_time = time.time()
config = {"configurable": {"thread_id": "1"}, "recursion_limit":100}

# Get keys
keys = KeyManager()
keys.get_keys_from_env()

# Build graph
graph = build_idea(mermaid_diagram=False)

# Initialize the state
input_state = {
    "files":{"data_description": "data.txt"}, #name of data_description file
    "llm": {"model": 'gemini-2.0-flash',  #name of the LLM model to use
            "temperature": 0.7,
            "max_output_tokens": 8192},
    "keys": keys,
}

# Run the graph
graph.invoke(input_state, config)
        
# End timer and report duration in minutes and seconds
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = int(elapsed_time % 60)
print(f"Idea generated in {minutes} min {seconds} sec.")    
