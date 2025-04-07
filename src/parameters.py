from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, AIMessage
from typing import Annotated, Literal
from langgraph.graph.message import add_messages

# Paper class
class PAPER(TypedDict):
    Title: str
    Abstract: str
    Introduction: str
    Methods: str
    Results: str
    Conclusions: str
    summary: str

# Class for Input/Output files
class FILES(TypedDict):
    Idea: str
    Methods: str
    Results: str
    Plots: str
    Paper_folder: str #location of the paper
    Paper: str  #name of LaTeX file
    Paper2: str #name of LaTeX file after adding the plots: last agent may fail
    Error: str  #location of the error file
    LaTeX_log: str #name of the file with the LaTeX log (when compiling it)

# Idea class
class IDEA(TypedDict):
    Idea: str
    Methods: str
    Results: str
    
# Graph state class
class GraphState(TypedDict):
    #query: str
    #papers: str
    next_node: str
    messages: Annotated[list[AnyMessage], add_messages]
    f_out: str
    paper: PAPER
    files: FILES
    idea: IDEA
