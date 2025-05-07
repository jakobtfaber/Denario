from .journal import Journal, LatexPresets

affiliation = rf"Anthropic, Gemini \& OpenAI servers. Planet Earth."

#---
# Latex journal presets definition
#---

latex_none = LatexPresets(article="article",
                         layout="",
                         bibliographystyle=rf"\bibliographystyle{{abbrv}}",
                         macros=rf"",
                         affiliation=rf"\date{{{affiliation}}}",
                         keywords=lambda x: "",
                         abstract=lambda x: rf"\maketitle \begin{{abstract}}{x}\end{{abstract}}",
                         )
"""No Latex preset"""

latex_aas = LatexPresets(article="aastex631",
                         layout="twocolumn",
                         bibliographystyle=rf"\bibliographystyle{{aasjournal}}",
                         macros=rf"\usepackage{{aas_macros}}",
                         affiliation=rf"\affiliation{{{affiliation}}}",
                         keywords=lambda x: x,
                         abstract=lambda x: rf"\begin{{abstract}}{x}\end{{abstract}}",
                         )
"""AAS Latex preset"""

latex_aps = LatexPresets(article="revtex4",
                         layout="twocolumn",
                         bibliographystyle="",
                         macros=rf"\usepackage{{aas_macros}}",
                         affiliation=rf"\affiliation{{{affiliation}}}",
                         keywords=lambda x: "",
                         abstract=lambda x: rf"\begin{{abstract}}{x}\end{{abstract}} \maketitle",
                         )
"""APS Latex preset"""

latex_jhep = LatexPresets(article="article",
                         layout="",
                         bibliographystyle=rf"\bibliographystyle{{JHEP}}",
                         macros=rf"\usepackage{{jcappub}}",
                         affiliation=rf"\affiliation{{{affiliation}}}",
                         keywords=lambda x: "",
                         abstract=lambda x: rf"\abstract{{{x}}} \maketitle",
                         )
"""JHEP Latex preset"""

latex_pasj = LatexPresets(article="pasj01",
                         layout="twocolumn",
                         bibliographystyle=rf"\bibliographystyle{{aasjournal}}",
                         macros=rf"\usepackage{{aas_macros}}",
                         affiliation=rf"\altaffiltext{{1}}{{{affiliation}}}",
                         keywords=lambda x: "",
                         abstract=lambda x: rf"\maketitle \begin{{abstract}}{x}\end{{abstract}}",
                         )
"""PASJ Latex preset"""

#---

journal_dict = {
    Journal.NONE: latex_none,
    Journal.AAS: latex_aas,
    Journal.APS: latex_aps,
    Journal.JHEP: latex_jhep,
    Journal.PASJ: latex_pasj,
}
"""Dictionary to relate the journal with their presets."""

def get_journal_latex_files(journal: Journal) -> list[str]:
    """Get journal .bst, .cls and .sty files according to the selected journal."""

    if journal==Journal.NONE:
        journal_files = []
    elif journal==Journal.AAS:
        journal_files = ['aasjournal.bst', 'aastex631.cls', 'aas_macros.sty']
    elif journal==Journal.APS:
        journal_files = ['revtex4.cls']
    elif journal==Journal.JHEP:
        journal_files = ['JHEP.bst', 'jcappub.sty']
    elif journal==Journal.PASJ:
        journal_files = ['aasjournal.bst', 'pasj01.cls', 'aas_macros.sty']

    return journal_files