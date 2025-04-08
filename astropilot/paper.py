from langgraph.graph import START, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from .parameters import GraphState
from .paper_node import *
from .reader import *

from .config import REPO_DIR

def write_paper(params, **kwargs):
    # Thread
    config = {"configurable": {"thread_id": "1"}, "recursion_limit":100}

    # Define the graph
    builder = StateGraph(GraphState)

    # Define nodes: these do the work
    builder.add_node("reader_node",       reader_node)
    builder.add_node("abstract_node",     abstract_node)
    builder.add_node("introduction_node", introduction_node)
    builder.add_node("methods_node",      methods_node)
    builder.add_node("results_node",      results_node)
    builder.add_node("conclusions_node",  conclusions_node)
    builder.add_node("generate_paper",    generate_paper)
    builder.add_node("plots_node",        plots_node)
    builder.add_node("refine_results",    refine_results)
    builder.add_node("LaTeX_node",        LaTeX_node)
    builder.add_node("keywords_node",     keywords_node)


    # Define edges: these determine how the control flow moves
    builder.add_edge(START,               "reader_node")
    builder.add_edge("reader_node",       "keywords_node")
    builder.add_edge("keywords_node",     "abstract_node")
    builder.add_edge("abstract_node",     "introduction_node")
    builder.add_edge("introduction_node", "methods_node")
    builder.add_edge("methods_node",      "results_node")
    builder.add_edge("results_node",      "conclusions_node")
    builder.add_edge("conclusions_node",  "plots_node")
    builder.add_edge("plots_node",        "refine_results")
    builder.add_edge("refine_results",    "LaTeX_node")
    builder.add_edge("LaTeX_node",        "generate_paper")
    builder.add_edge("generate_paper",    "__end__")


    memory = MemorySaver()
    #memory = SqliteSaver(conn)
    graph = builder.compile(checkpointer=memory)

    #graph_image = graph.get_graph(xray=True).draw_mermaid_png()
    #with open("graph_diagram.png", "wb") as f:
    #    f.write(graph_image)
        
    result = graph.invoke({"files": {"Idea":        os.path.join(REPO_DIR,"input_files/idea.md"),
                                    "Methods":      os.path.join(REPO_DIR,"input_files/methods.md"),
                                    "Results":      os.path.join(REPO_DIR,"input_files/results.md"),
                                    "Plots":        os.path.join(REPO_DIR,"input_files/plots"),
                                    "Paper_folder": os.path.join(REPO_DIR,"paper"),
                                    "Paper":        "paper.tex",
                                    "Paper2":       "paper_w_plots.tex",
                                    "Error":        "Error.txt",
                                    "LaTeX_log":    "LaTeX_compilation.log"},
                        "idea": {},
                        "paper":{"summary":""}},
                        config)
    

    print("[astropilot.paper] Paper generation workflow complete.")

