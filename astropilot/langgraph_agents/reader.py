import os,sys
from pathlib import Path
import hashlib
import shutil
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from .parameters import GraphState

def preprocess_node(state: GraphState, config: RunnableConfig):
    """
    This agent reads the input files, clean up files, and set the name of some files
    """
    
    # set the LLM
    if 'gemini' in state['llm']['model']:
        state['llm']['llm'] = ChatGoogleGenerativeAI(model=state['llm']['model'],
                                                temperature=state['llm']['temperature'],
                                                google_api_key=state["keys"].GEMINI)

    elif any(key in state['llm']['model'] for key in ['gpt', 'o3']):
        state['llm']['llm'] = ChatOpenAI(model=state['llm']['model'],
                                         temperature=state['llm']['temperature'],
                                         openai_api_key=state["keys"].OPENAI)
                    
    elif 'claude' in state['llm']['model']  or 'anthropic' in state['llm']['model'] :
        state['llm']['llm'] = ChatAnthropic(model=state['llm']['model'],
                                            temperature=state['llm']['temperature'],
                                            anthropic_api_key=state["keys"].ANTHROPIC)
    
    # set the tokens usage
    state['tokens'] = {'ti': 0, 'to': 0, 'i': 0, 'o': 0}

    # set idea class
    idea = {**state['idea'],
            'iteration':0, 'previous_ideas': "", 'idea': "", 'criticism': ""}

    # set the name of the other files
    state['files'] = {**state['files'],
                      "Temp":      f"{state['files']['Folder']}/temp",
                      "LLM_calls": f"{state['files']['Folder']}/LLM_calls.txt",
                      "idea":      f"{state['files']['Folder']}/input_files/idea.md",
                      "idea_log":  f"{state['files']['Folder']}/temp/idea.log",
    }

    # create project folder, input files, and temp files
    os.makedirs(state['files']['Folder'],                  exist_ok=True)
    os.makedirs(state['files']['Temp'],                    exist_ok=True)
    os.makedirs(f"{state['files']['Folder']}/input_files", exist_ok=True)

    # clean existing files
    for f in ["LLM_calls", "idea", "idea_log"]:
        file_path = state['files'][f]
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # read data description
    try:
        with open(state['files']['data_description'], 'r', encoding='utf-8') as f:
            description = f.read()
    except FileNotFoundError:
        raise Exception("File not found!")
    except Exception as e:
        raise Exception("Error reading the data description file!")

    return {
        "files": state['files'],
        "llm": state['llm'],
        "tokens": state['tokens'],
        "idea": idea,
        "data_description": description,
    }

