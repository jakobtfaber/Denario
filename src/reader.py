from langchain_core.runnables import RunnableConfig
import sys,os
from pathlib import Path
import hashlib
import shutil
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from src.parameters import GraphState


load_dotenv()
GOOGLE_API_KEY     = os.getenv("GOOGLE_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
OPENAI_API_KEY     = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY")


def preprocess_node(state: GraphState, config: RunnableConfig):
    """
    This agent reads the input files, clean up files, and set the name of some files
    """

    # set the LLM
    if 'gemini' in state['llm']['model']:
        state['llm']['llm'] = ChatGoogleGenerativeAI(model=state['llm']['model'],
                                                temperature=state['llm']['temperature'],
                                                google_api_key=GOOGLE_API_KEY)

    elif any(key in state['llm']['model'] for key in ['gpt', 'o3']):
        state['llm']['llm'] = ChatOpenAI(model=state['llm']['model'],
                                         temperature=state['llm']['temperature'],
                                         openai_api_key=OPENAI_API_KEY)
                    
    elif 'claude' in model or 'anthropic' in model:
        state['llm']['llm'] = ChatAnthropic(model=state['llm']['model'],
                                            temperature=state['llm']['temperature'],
                                            anthropic_api_key=ANTHROPIC_API_KEY)
    
    # set the tokens usage
    state['tokens'] = {}
    state['tokens']['ti']  = 0
    state['tokens']['to']  = 0
    state['tokens']['i']   = 0
    state['tokens']['o']   = 0
    
    # set the names of standard files
    state['files'] = {**state['files'],
                      "Paper_v1":  "paper_v1.tex",
                      "Paper_v2":  "paper_v2.tex",
                      "Paper_v3":  "paper_v3.tex",
                      "Paper_v4":  "paper_v4.tex",
                      "Error":     f"{state['files']['Folder']}/Error.txt",
                      "LaTeX_log": f"{state['files']['Folder']}/LaTeX_compilation.log",
                      "Temp":      f"{state['files']['Folder']}/Temp",
                      "LLM_calls": f"{state['files']['Folder']}/LLM_calls.txt"}

    # set the Latex class
    state['latex'] = {}
    state['latex']['section'] = ""
    
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

    # remove these files if they already exist
    for f_in in [state['files']['Error'], state['files']['LLM_calls'],
                 state['files']['LaTeX_log']]:
        if os.path.exists(f_in):  os.remove(f"{f_in}")

    # copy LaTeX files to project folder
    for f in ['aasjournal.bst', 'aastex631.cls']:
        f_in = f"{state['files']['Folder']}/{f}"
        if not(os.path.exists(f_in)):
            os.system(f"cp LaTeX/{f} {state['files']['Folder']}")

    # create a folder to save LaTeX progress
    os.makedirs(state['files']['Temp'], exist_ok=True)

    # deal with repeated plots
    plots_dir    = Path(f"{state['files']['Folder']}/{state['files']['Plots']}")
    repeated_dir = Path(f"{plots_dir}_repeated")

    # Walk through all plot files
    hash_dict = {}  # create hash dictionary
    for file in plots_dir.iterdir():
        if file.is_file():

            # Compute hash
            with open(file, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
    
            if file_hash in hash_dict:
                repeated_dir.mkdir(exist_ok=True)
                # This is a repeated file: copy it to repeated_plots
                print(f"Repeated: {file.name} (same as {hash_dict[file_hash].name})")
                shutil.move(file, repeated_dir / file.name)
            else:
                hash_dict[file_hash] = file


    return {
        "llm": state['llm'],
        "tokens": state['tokens'],
        "files": state['files'],
        "latex": state['latex'],
        "idea": idea,
        "paper": {"summary": ""},
    }

