from typing_extensions import TypedDict, Any
from typing import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from ..key_manager import KeyManager


# Class for Input/Output files
class FILES(TypedDict):
    data_description: str #name of the file with the data description
    LLM_calls: str        #name of the file with the calls to the LLM
    Temp: str             #name of the folder with the temporary LaTeX files

# Token class
class TOKENS(TypedDict):
    ti: int #total input tokens
    to: int #total output tokens 
    i:  int #input tokens (just for individual calls or functions)
    o:  int #output tokens (just for individual calls or functions)

# LLM class
class LLM(TypedDict):
    model: str
    max_output_tokens: int
    llm: Any
    temperature: float

# Idea class
class IDEA(TypedDict):
    iteration: int
    previous_ideas: str
    idea: str
    criticism: str

# Graph state class
class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    idea: IDEA
    tokens: TOKENS
    llm: LLM
    files: FILES
    keys: KeyManager
    data_description: str
