import subprocess
import sys,os
from pathlib import Path

from .parameters import GraphState



def compile_latex(state: GraphState, paper_name: str):
    """
    Function used to compile the paper
    Args:
       state: the state of the graph
       paper: the name of file to compile
    """
    
    # get the current directory
    original_dir = os.getcwd()

    # go to the folder containing the paper
    os.chdir(state['files']['Paper_folder'])

    # try to compile twice for citations and links
    for i in range(3):  #compile three times to add citations
        try:
            result = subprocess.run(["xelatex", paper_name],
                                    input="\n",
                                    capture_output=True,
                                    text=True, check=True)
            print(f"    LaTeX compiled successfully: iteration {i+1}")

            # Write stdout to log
            with open(state['files']['LaTeX_log'], 'a') as f:
                f.write(f"\n==== LaTeX Compilation Pass {i + 1} ====\n")
                f.write(result.stdout)

            if i==0:
                result = subprocess.run(["bibtex", Path(paper_name).stem],
                                        capture_output=True,
                                        text=True, check=True)

            
        except subprocess.CalledProcessError as e:
            print(f"    LaTeX compilation failed: iteration {i+1}")
            with open(state['files']['LaTeX_log'], 'a') as f:
                f.write(f"\n==== ERROR on Pass {i + 1} ====\n")
                f.write(e.stdout or "")
                f.write(e.stderr or "")
                        
    os.chdir(original_dir)



def save_paper(state: GraphState, paper_name: str):
    """
    This function just saves the current state of the paper

    Args:
       state: state of the graph
       name: name of the file to save the paper
    """

    paper = rf"""\documentclass[twocolumn]{{aastex631}}

\newcommand{{\vdag}}{{(v)^\dagger}}
\newcommand\aastex{{AAS\TeX}}
\newcommand\latex{{La\TeX}}
\usepackage{{amsmath}}

\begin{{document}}

\title{{{state['paper'].get('Title','')}}}

\author{{AstroPilot}}
\affiliation{{Anthropic, Gemini \& OpenAI servers. Planet Earth.}}

\begin{{abstract}}
{state['paper'].get('Abstract','')}
\end{{abstract}}

\keywords{{{state['paper']['Keywords']}}}


\section{{Introduction}}
\label{{sec:intro}}
{state['paper'].get('Introduction','')}

\section{{Methods}}
\label{{sec:methods}}
{state['paper'].get('Methods','')}

\section{{Results}}
\label{{sec:results}}
{state['paper'].get('Results','')}

\section{{Conclusions}}
\label{{sec:conclusions}}
{state['paper'].get('Conclusions','')}

\bibliography{{bibliography}}{{}}
\bibliographystyle{{aasjournal}}

\end{{document}}
"""
    
    # save paper to file
    f_in = f"{state['files']['Paper_folder']}/{paper_name}"
    with open(f_in, 'w', encoding='utf-8') as f:
        f.write(paper)


def save_bib(state: GraphState):
    with open(f"{state['files']['Paper_folder']}/bibliography.bib", 'a', encoding='utf-8') as f:
        f.write(state['paper']['References'].strip() + "\n")    

