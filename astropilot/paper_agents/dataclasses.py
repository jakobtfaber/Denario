from typing import List, Dict, Callable
from pydantic import BaseModel, Field
from enum import Enum

class Research(BaseModel):
    """Research class."""
    data_description: str = Field(default="", description="The data description of the project")
    idea: str = Field(default="", description="The idea of the project")
    methodology: str = Field(default="", description="The methodology of the project")
    results: str = Field(default="", description="The results of the project")
    plot_paths: List[str] = Field(default_factory=list, description="The plot paths of the project")
    keywords: Dict[str, str] = Field(default_factory=dict, description="The AAS keywords describing the project")

class Journal(str, Enum):
    """Enum which includes the different journals considered."""
    NONE = None
    AAS  = "AAS"
    JHEP = "JHEP"
    PASJ = "PASJ"

class LatexPresets(BaseModel):
    """Latex presets to be set depending on the journal"""
    article: str
    layout: str
    bibliographystyle: str
    macros: str
    affiliation: str
    abstract: Callable[[str], str]
    keywords: Callable[[str], str]
