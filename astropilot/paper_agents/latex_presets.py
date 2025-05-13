from .journal import Journal, LatexPresets

#---
# Latex journal presets definition
#---

latex_none = LatexPresets(article="article",
                         bibliographystyle=r"\bibliographystyle{abbrv}",
                         affiliation=lambda x: rf"\date{{{x}}}",
                         abstract=lambda x: f"\\maketitle\n\\begin{{abstract}}\n{x}\n\end{{abstract}}\n",
                         files=["abbrv.bst"],
                         )
"""No Latex preset"""

latex_aas = LatexPresets(article="aastex631",
                         layout="twocolumn",
                         bibliographystyle=r"\bibliographystyle{aasjournal}",
                         usepackage=r"\usepackage{aas_macros}",
                         abstract=lambda x: f"\\begin{{abstract}}\n{x}\n\\end{{abstract}}\n",
                         files=['aasjournal.bst', 'aastex631.cls', 'aas_macros.sty'],
                         keywords=lambda x: f"\keywords{{{x}}}",
                         )
"""AAS Latex preset"""

latex_aps = LatexPresets(article="revtex4",
                         layout="twocolumn",
                         bibliographystyle="",
                         abstract=lambda x: f"\\begin{{abstract}}\n{x}\n\\end{{abstract}}\n\\maketitle",
                         files=[],
                         )
"""APS Latex preset"""

latex_icml = LatexPresets(article="article",
                        title=r"\icmltitle",
                        author=lambda x: f"\\begin{{icmlauthorlist}}\n\\icmlauthor{{{x}}}{{aff}}\n\\end{{icmlauthorlist}}",
                        bibliographystyle="",
                        usepackage=r"\usepackage[accepted]{icml2025}",
                        affiliation=lambda x: f"\\icmlaffiliation{{aff}}{{{x}}}\n",
                        abstract=lambda x: f"\\printAffiliationsAndNotice{{}}\n\\begin{{abstract}}\n{x}\n\\end{{abstract}}\n",
                        files=['icml2025.sty'],
                        icmlkeywords=lambda x: f"\keywords{{{x}}}",
                         )
"""ICML Latex preset"""

latex_jhep = LatexPresets(article="article",
                         bibliographystyle=r"\bibliographystyle{JHEP}",
                         usepackage=r"\usepackage{jcappub}",
                         abstract=lambda x: f"\\abstract{{\n{x}\n}}\n\\maketitle",
                         files=['JHEP.bst', 'jcappub.sty'],
                         )
"""JHEP Latex preset"""

latex_neurips = LatexPresets(article="article",
                        bibliographystyle="",
                        usepackage=r"\usepackage{neurips}",
                        abstract=lambda x: f"\\maketitle\n\begin{{abstract}}\n{x}\n\end{{abstract}}\n",
                        files=['neurips.sty']
                         )
"""NeurIPS Latex preset"""

latex_pasj = LatexPresets(article="pasj01",
                         layout="twocolumn",
                         bibliographystyle=r"\bibliographystyle{aasjournal}",
                         usepackage=r"\usepackage{aas_macros}",
                         affiliation=lambda x: rf"\altaffiltext{{1}}{{{x}}}",
                         abstract=lambda x: f"\\maketitle\n\\begin{{abstract}}\n{x}\n\\end{{abstract}}",
                         files=['aasjournal.bst', 'pasj01.cls', 'aas_macros.sty'],
                         )
"""PASJ Latex preset"""

#---

journal_dict = {
    Journal.NONE: latex_none,
    Journal.AAS: latex_aas,
    Journal.APS: latex_aps,
    Journal.ICML: latex_icml,
    Journal.JHEP: latex_jhep,
    Journal.NeurIPS: latex_neurips,
    Journal.PASJ: latex_pasj,
}
"""Dictionary to relate the journal with their presets."""
