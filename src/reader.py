from langchain_core.runnables import RunnableConfig
import sys,os
from pathlib import Path
import hashlib
import shutil

from src.parameters import GraphState


def preprocess_node(state: GraphState, config: RunnableConfig):
    """
    This agent reads the input files, clean up files, and set the name of some files
    """

    # set the names of standard files
    state['files'] = {**state['files'],
                      "Paper_v1":  "paper_v1.tex",
                      "Paper_v2":  "paper_v2.tex",
                      "Paper_v3":  "paper_v3.tex",
                      "Paper_v4":  "paper_v4.tex",
                      "Error":     "Error.txt",
                      "LaTeX_log": "LaTeX_compilation.log"}
    idea = {}
    
    # read input files
    for key in ["Idea", "Methods", "Results"]:
        try:
            path = Path(f"{state['files']['Folder']}/{state['files'][key]}")
            with path.open("r", encoding="utf-8") as f:
                idea[key] = f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read {key} file: {e}")

    # remove these files if they already exist
    for f in ['Paper_v1', 'Paper_v2', 'Paper_v3', 'Paper_v4']:
        f_in = f"{state['files']['Folder']}/{state['files'][f]}"
        if os.path.exists(f_in): os.remove(f"{f_in}")

        # get the root of the paper file (if paper.tex, root=paper)
        root = Path(state['files'][f]).stem
        
        for f_in in [f'{root}.pdf', f'{root}.aux', f'{root}.log', f'{root}.out',
                     f'{root}.bbl', f'{root}.blg', f'{root}.synctex.gz',
                     f'{root}.synctex(busy)', 'bibliography.bib',
                     'bibliography_temp.bib',]:
            fin = f"{state['files']['Folder']}/{f_in}"
            if os.path.exists(fin): os.remove(f"{fin}")

    for f_in in [state['files']['Error']]:
        if os.path.exists(f_in):  os.remove(f"{f_in}")

    # remove LaTeX compilation log file
    f_in = f"{state['files']['Folder']}/{state['files']['LaTeX_log']}"
    if os.path.exists(f_in):  os.remove(f"{f_in}")

    # copy LaTeX files to project folder
    for f in ['aasjournal.bst', 'aastex631.cls']:
        f_in = f"{state['files']['Folder']}/{f}"
        if not(os.path.exists(f_in)):
            os.system(f"cp LaTeX/{f} {state['files']['Folder']}")

    # deal with repeated plots
    plots_dir    = Path(f"{state['files']['Folder']}/{state['files']['Plots']}")
    repeated_dir = Path(f"{plots_dir}_repeated")
    repeated_dir.mkdir(exist_ok=True)

    # Hash dictionary
    hash_dict = {}

    # Walk through all PNG files
    for file in plots_dir.iterdir():
        if file.is_file():

            # Compute hash
            with open(file, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
    
            if file_hash in hash_dict:
                # This is a repeated file: copy it to repeated_plots
                print(f"Repeated: {file.name} (same as {hash_dict[file_hash].name})")
                shutil.move(file, repeated_dir / file.name)
            else:
                hash_dict[file_hash] = file


    return {"idea": idea,  "files": state['files'],  "paper": {"summary": ""}}

