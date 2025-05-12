from .journal import Journal, LatexPresets

affiliation = r"Anthropic, Gemini \& OpenAI servers. Planet Earth."

#---
# Latex journal presets definition
#---

latex_none = LatexPresets(article="article",
                         layout="",
                         bibliographystyle=r"\bibliographystyle{abbrv}",
                         macros=r"",
                         affiliation=rf"\date{{{affiliation}}}",
                         keywords=lambda x: "",
                         abstract=lambda x: rf"\maketitle \begin{{abstract}}{x}\end{{abstract}}",
                         files=["abbvr.bst"],
                         )
"""No Latex preset"""

latex_aas = LatexPresets(article="aastex631",
                         layout="twocolumn",
                         bibliographystyle=r"\bibliographystyle{aasjournal}",
                         macros=r"\usepackage{aas_macros}",
                         affiliation=rf"\affiliation{{{affiliation}}}",
                         keywords=lambda x: x,
                         abstract=lambda x: f"\\begin{{abstract}}\n {x} \n\\end{{abstract}}\n",
                         files=['aasjournal.bst', 'aastex631.cls', 'aas_macros.sty'],
                         )
"""AAS Latex preset"""

latex_aps = LatexPresets(article="revtex4",
                         layout="twocolumn",
                         bibliographystyle="",
                         macros=r"\usepackage{aas_macros}",
                         affiliation=rf"\affiliation{{{affiliation}}}",
                         keywords=lambda x: "",
                         abstract=lambda x: f"\\begin{{abstract}} \n {x} \n\\end{{abstract}} \n \\maketitle",
                         files=['revtex4.cls'],
                         )
"""APS Latex preset"""

latex_icml = LatexPresets(article="article",
                        layout="",
                        bibliographystyle="",
                        macros=r"\usepackage{icml2025}",
                        #  affiliation=rf"\begin{{icmlauthorlist}} \n \icmlauthor{{{affiliation}}}{{aff}} \n \end{{icmlauthorlist}} \n \icmlaffiliation{{aff}}{{affiliation}}",
                        affiliation=r"\icmlaffiliation{aff}{affiliation} \n \printAffiliationsAndNotice{}",
                        keywords=lambda x: "",
                        abstract=lambda x: f"\\begin{{abstract}} \n {x} \n\\end{{abstract}} \n",
                        files=['icml2015.sty'],
                         )
"""ICML Latex preset"""

latex_jhep = LatexPresets(article="article",
                         layout="",
                         bibliographystyle=r"\bibliographystyle{JHEP}",
                         macros=r"\usepackage{jcappub}",
                         affiliation=rf"\affiliation{{{affiliation}}}",
                         keywords=lambda x: "",
                         abstract=lambda x: f"\\abstract{{{x}}} \\maketitle",
                         files=['JHEP.bst', 'jcappub.sty'],
                         )
"""JHEP Latex preset"""

latex_neurips = LatexPresets(article="article",
                        layout="",
                        bibliographystyle="",
                        macros=r"\usepackage{neurips}",
                        affiliation=r"",
                        keywords=lambda x: "",
                        abstract=lambda x: r"\maketitle \begin{{abstract}}{x}\end{{abstract}} \n",
                        files=['neurips.sty']
                         )
"""NeurIPS Latex preset"""

latex_pasj = LatexPresets(article="pasj01",
                         layout="twocolumn",
                         bibliographystyle=r"\bibliographystyle{aasjournal}",
                         macros=r"\usepackage{aas_macros}",
                         affiliation=rf"\altaffiltext{{1}}{{{affiliation}}}",
                         keywords=lambda x: "",
                         abstract=lambda x: f"\\maketitle \n \\begin{{abstract}} \n {x} \n \\end{{abstract}}",
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
