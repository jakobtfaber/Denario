from src.graph import build_graph
import asyncio

# Thread
config = {"configurable": {"thread_id": "1"}, "recursion_limit":100}

# build graph
graph = build_graph(mermaid_diagram=True)

# run the graph
result = asyncio.run(graph.ainvoke(
    {"files":{"Idea":         "Input_Files/idea.md",
              "Methods":      "Input_Files/methods.md",
              "Results":      "Input_Files/results.md",
              "Plots":        "Input_Files/plots",
              "Paper_folder": "LaTeX",
              "Paper_v1":     "paper_v1.tex",
              "Paper_v2":     "paper_v2.tex",
              "Paper_v3":     "paper_v3.tex",
              "Error":        "Error.txt",
              "LaTeX_log":    "LaTeX_compilation.log"},
     "idea": {},
     "paper":{"summary":""}},
    config)
)
