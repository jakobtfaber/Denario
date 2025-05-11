from typing import Callable
from pydantic import BaseModel
from enum import Enum

class Journal(str, Enum):
    """Enum which includes the different journals considered."""
    NONE = None
    """No journal, use standard latex presets with abbrv for bibliography style."""
    AAS  = "AAS"
    """American Astronomical Society journals, including the Astrophysical Journal."""
    APS = "APS"
    """Physical Review Journals from the American Physical Society, including Physical Review Letters, PRA, etc."""
    ICML = "ICML"
    """ICML - International Conference on Machine Learning."""
    JHEP = "JHEP"
    """Journal of High Energy Physics, including JHEP, JCAP, etc."""
    NeurIPS = "NeurIPS"
    """NeurIPS - Conference on Neural Information Processing Systems."""
    PASJ = "PASJ"
    """Publications of the Astronomical Society of Japan."""

class LatexPresets(BaseModel):
    """Latex presets to be set depending on the journal"""
    article: str
    """Article preset or .cls file."""
    layout: str
    """Layout, twocolumn or singlecolum layout."""
    bibliographystyle: str
    """Bibliography style, indicated by a .bst file."""
    macros: str
    """Usepackage with .sty file including macros."""
    affiliation: str
    """Command for affiliations."""
    abstract: Callable[[str], str]
    """Command for abstract. Include maketitle here if needed since some journals require before or after the abstract."""
    keywords: Callable[[str], str]
    """Keywords of the research."""
    files: list[str]
    """Files to be included in the latex: .bst, .cls and .sty."""
