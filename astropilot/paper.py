from langgraph.graph import START, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from .parameters import GraphState
from .paper_node import *
from .reader import *
from .graph import build_graph

from .config import REPO_DIR

def write_paper(params, **kwargs):

    config = {"configurable": {"thread_id": "1"}, "recursion_limit":100}

    # build graph
    graph = build_graph(mermaid_diagram=False)

    # run the graph
    result = asyncio.run(graph.ainvoke(
        {"files":{"Idea":       os.path.join(REPO_DIR,"input_files/idea.md"),
                "Methods":      os.path.join(REPO_DIR,"input_files/methods.md"),
                "Results":      os.path.join(REPO_DIR,"input_files/results.md"),
                "Plots":        os.path.join(REPO_DIR,"input_files/plots"),
                "Paper_folder": os.path.join(REPO_DIR,"paper"),
                "Paper_v1":     "paper_v1.tex",
                "Paper_v2":     "paper_v2.tex",
                "Paper_v3":     "paper_v3.tex",
                "Error":        "Error.txt",
                "LaTeX_log":    "LaTeX_compilation.log"},
        "idea": {},
        "paper":{"summary":""}},
        config)
    )
    print("[astropilot.paper] Paper generation workflow complete.")

