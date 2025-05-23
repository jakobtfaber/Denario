# Prompts

Here are detailed the exact prompts employed for the agents in each of the steps in the AstroPilot generation process.

## Idea

### Planner instructions

```py
--8<-- "astropilot/prompts/idea.py"
```

## Methods

### Planner instructions

```py
--8<-- "astropilot/prompts/method.py:1:21"
```

### Researcher instructions

```py
--8<-- "astropilot/prompts/method.py:22:"
```

## Experiment

### Planner instructions

```py
--8<-- "astropilot/prompts/experiment.py:1:16"
```

### Engineer instructions

```py
--8<-- "astropilot/prompts/experiment.py:18:34"
```

### Researcher instructions

```py
--8<-- "astropilot/prompts/experiment.py:36:46"
```

## Paper

### Summary

```py
rf"""
Summarize the text below and combine with the summarized text. 

Summarized text:
{summary}

Text to summarize:
{text}

Respond in this format:
\begin{{Summary}}
<Summary>
\end{{Summary}}

In <Summary> put the total summary.
"""
```

### References

```py
rf"""
You are provided an original text from a scientific paper written in LaTeX. In the text, there are figures and references to figures. Your task is to make sure that the references to the figures are correct. If there are errors, please correct the text to fix it. Follow these guidelines:

- Do not add or remove text
- Focus on fixing errors in references to figures
- For instance, given this figure
- If references match with its corresponding figure label, do not change it

\\begin{{figure}}[h!]
    \\centering
    \\includegraphics[width=0.5\textwidth]{{../{state['files']['Folder']}/plots/A.png}}
    \\caption{{Histogram of GroupSFR for two different values of non-Gaussianities. The blue histogram represents $f = 200$ and the red histogram represents $f = -200$. Large differences are seen in the normalized density of GroupSFR for the two different values of $f$.}}
    \\label{{fig:GroupSFR_hist}}
\\end{{figure}}

This reference is wrong \\ref{{fig:A.png}} and should be changed to \\ref{{fig:GroupSFR_hist}}

Please, check that the name of the references match with their respective labels.

Original text:
{text}

**Respond in this format**

\\begin{{Text}}
<TEXT>
\\end{{Text}}

In <TEXT> put the corrected text.

"""
```

### Fix errors

```py
rf"""
The text below has problems and LaTeX cannot compile it. You are provided with the text together with the LaTeX compilation error. Your task is to fix the text so that it compiles properly in LaTeX. Please follow these instructions:

- The text you are given is just a small part of a LaTeX paper. Thus, you dont need to add things like \\begin{{document}}.
- Fix **all LaTeX errors** found in the compilation error
- Pay special attention to underscores. It is likely that an underscores _ may need to be \\_ to compile properly
- Return the original text but with the errors fixed
- Keep the text intact. Only fix the errors without changing anything else

Text:
{state['paper'][state['latex']['section_to_fix']]}

Error:
{error}
    
Respond in this format:

\begin{{Text}}
<TEXT>
\end{{Text}}

In <TEXT>, put the new version of the text with the LaTeX errors fixed.
"""
```