from langchain_core.runnables import RunnableConfig
import sys,os
from pathlib import Path

from src.parameters import GraphState


def reader_node(state: GraphState, config: RunnableConfig):
    """
    This agent just read the input files and clean up files
    """

    # read input files
    for key in ["Idea", "Methods", "Results"]:
        try:
            path = Path(state["files"][key])
            with path.open("r", encoding="utf-8") as f:
                state["idea"][key] = f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read {key} file: {e}")

    # remove these files if they already exist
    for f in ['Paper', 'Paper2']:
        f_in = f"{state['files']['Paper_folder']}/{state['files'][f]}"
        if os.path.exists(f_in): os.remove(f"{f_in}")

    # get the root of the paper file (if paper.tex, root=paper)
    root = Path(state['files']['Paper']).stem
        
    for f_in in [f'{root}.pdf', f'{root}.aux', f'{root}.log', f'{root}.out']:
        fin = f"{state['files']['Paper_folder']}/{f_in}"
        if os.path.exists(fin): os.remove(f"{fin}")

    for f_in in [state['files']['Error'], state['files']['LaTeX_log']]:
        if os.path.exists(f_in): os.remove(f"{f_in}")
        

    return {"idea":{**state['idea'],
                    "idea":state["idea"]["Idea"],
                    "methods":state["idea"]["Methods"],
                    "results":state["idea"]["Results"]}}

