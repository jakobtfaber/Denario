from src.graph import build_graph
import asyncio
import time

# Start timer
start_time = time.time()

# Thread
config = {"configurable": {"thread_id": "1"}, "recursion_limit":100}

# build graph
graph = build_graph(mermaid_diagram=True)

# run the graph
result = asyncio.run(graph.ainvoke(
    {"files":{"Folder":       "Project8",   #name of folder containing input files
              "Idea":         "idea.md",    #name of file containing idea description
              "Methods":      "methods.md", #name of file with methods description
              "Results":      "results.md", #name of file with results description
              "Plots":        "plots"}      #name of folder containing plots
     }, config))

# End timer and report duration in minutes and seconds
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = int(elapsed_time % 60)
print(f"Paper written in {minutes} min {seconds} sec.")
