from .dataclasses import Journal, LatexPresets

latex_none = LatexPresets(article="article",
                         layout="",
                         bibliographystyle="abbrv",
                         macros=rf"",
                         affiliation=rf"\date{{Anthropic, Gemini \& OpenAI servers. Planet Earth.}}",
                         keywords=lambda x: "",
                         abstract=lambda x: rf"\maketitle \begin{{abstract}}{x}\end{{abstract}}",
                         )
"""No Latex preset"""

latex_aas = LatexPresets(article="aastex631",
                         layout="twocolumn",
                         bibliographystyle="aasjournal",
                         macros=rf"\usepackage{{aas_macros}}",
                         affiliation=rf"\affiliation{{Anthropic, Gemini \& OpenAI servers. Planet Earth.}}",
                         keywords=lambda x: x,
                         abstract=lambda x: rf"\begin{{abstract}}{x}\end{{abstract}}",
                         )
"""AAS Latex preset"""

latex_jhep = LatexPresets(article="article",
                         layout="",
                         bibliographystyle="JHEP",
                         macros=rf"\usepackage{{jcappub}}",
                         affiliation=rf"\affiliation{{Anthropic, Gemini \& OpenAI servers. Planet Earth.}}",
                         keywords=lambda x: "",
                         abstract=lambda x: rf"\abstract{{{x}}} \maketitle",
                         )
"""JHEP Latex preset"""

latex_pasj = LatexPresets(article="pasj01",
                         layout="twocolumn",
                         bibliographystyle="aasjournal",
                         macros=rf"\usepackage{{aas_macros}}",
                         affiliation=rf"\affiliation{{Anthropic, Gemini \& OpenAI servers. Planet Earth.}}",
                         keywords=lambda x: x,
                         abstract=lambda x: rf"\begin{{abstract}}{x}\end{{abstract}}",
                         )
"""PASJ Latex preset"""

journal_dict = {
    Journal.NONE: latex_none,
    Journal.AAS: latex_aas,
    Journal.JHEP: latex_jhep,
    Journal.PASJ: latex_pasj,
}
