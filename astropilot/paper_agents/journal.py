from typing import Callable
from pydantic import BaseModel
from enum import Enum

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
