from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, AIMessage
from typing import Annotated, Literal
from langgraph.graph.message import add_messages

# Paper class
class PAPER(TypedDict):
    Title: str
    Abstract: str
    Keywords: str
    Introduction: str
    Methods: str
    Results: str
    Conclusions: str
    References: str
    summary: str

# Class for Input/Output files
class FILES(TypedDict):
    Idea: str
    Methods: str
    Results: str
    Plots: str
    Paper_folder: str #name of folder containing the paper
    Paper_v1: str     #name of the file containing the version 1 of the paper 
    Paper_v2: str     #name of the file containing the version 2 of the paper 
    Paper_V3: str     #name of the file containing the version 3 of the paper 
    Error: str        #name of the error file
    LaTeX_log: str    #name of the file with the LaTeX log (when compiling it)

# Idea class
class IDEA(TypedDict):
    Idea: str
    Methods: str
    Results: str
    
# Graph state class
class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    files: FILES
    idea: IDEA
    paper: PAPER
