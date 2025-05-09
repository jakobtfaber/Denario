import time
from .agents_graph import build_idea
from ..key_manager import KeyManager


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
    "llm": {"model": LLM[llm]['name'],  #name of the LLM model to use
            "temperature": LLM[llm]['temperature'],
            "max_output_tokens": LLM[llm]['max_output_tokens']},
    "keys": self.keys,
}

# Run the graph
graph.invoke(input_state, config)
        
# End timer and report duration in minutes and seconds
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = int(elapsed_time % 60)
print(f"Paper written in {minutes} min {seconds} sec.")    
