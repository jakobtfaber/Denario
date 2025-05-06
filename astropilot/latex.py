import subprocess
import os
import re
from pathlib import Path

from .parameters import GraphState
from .prompts import fix_latex_bug_prompt
from .tools import LLM_call, extract_latex_block
from .dataclasses import Journal

# Characters that should be escaped in BibTeX (outside math mode)
special_chars = {
    "_": r"\_",
    "&": r"\&",
    "%": r"\%",
    "#": r"\#",
    "$": r"\$",
    "{": r"\{",
    "}": r"\}",
    "~": r"\~{}",
    "^": r"\^{}",
}


def compile_latex(state: GraphState, paper_name: str, verbose=True):

    # get the paper stem
    paper_stem = Path(paper_name).stem

    def run_xelatex():
        return subprocess.run(["xelatex", paper_name],
                              cwd=state['files']['Folder'],
                              input="\n", capture_output=True,
                              text=True, check=True)

    def run_bibtex():
        subprocess.run(["bibtex", paper_stem],
                       cwd=state['files']['Folder'],
                       capture_output=True, text=True)

    def log_output(i, result_or_error, is_error=False):
        with open(state['files']['LaTeX_log'], 'a') as f:
            f.write(f"\n==== {'ERROR' if is_error else 'PASS'} on iteration {i} ====\n")
            f.write("---- STDOUT ----\n")
            f.write(result_or_error.stdout or "")
            f.write("---- STDERR ----\n")
            f.write(result_or_error.stderr or "")

    def fix_error(e):
        lines = (e.stdout or "").splitlines() + (e.stderr or "").splitlines()
        error_lines = []
        show_context = 0
        for line in lines:
            if line.lstrip().startswith("!"):
                error_lines.append("\n" + line)
                show_context = 3
            elif show_context > 0:
                error_lines.append(line)
                show_context -= 1
        error_msg = ' '.join(line.strip() for line in error_lines if line.strip())
        section = state['latex']['section']
        fixed_text = fix_latex_bug(state, state['paper'][section], error_msg)
        state['paper'][section] = fixed_text
        save_paper(state, paper_name)

    # --- Retry loop ---
    #for attempt in range(3):
    #    try:
    #        run_xelatex()
    #        break  # success
    #    except subprocess.CalledProcessError as e:
    #        print('Fixing things...')
    #        fix_error(e)
    #else:
    #    os.chdir(original_dir)
    #    raise RuntimeError("LaTeX failed after 3 attempts")

    # Try to compile it the first time
    try:
        run_xelatex()
        if verbose:
            print("    LaTeX compiled successfully: Pass 1")
    except subprocess.CalledProcessError as e:
        log_output("Pass 1", e, is_error=True)
        print("LaTeX failed on pass 1")

    # if there is bibliography, compile it
    further_iterations = 1
    if os.path.exists(f"{state['files']['Folder']}/bibliography.bib"):
        run_bibtex()
        further_iterations =2

    # Compile it two more times to put references and citations
    for i in range(further_iterations):        
        try:
            run_xelatex()
            if verbose:
                print(f"    LaTeX compiled successfully: Pass {i+2}")
        except subprocess.CalledProcessError as e:
            log_output(f"Final Pass {i+1}", e, is_error=True)
            print(f"LaTeX failed on pass {i+2}")

    # remove auxiliary files
    for fin in [f'{paper_stem}.aux', f'{paper_stem}.log', f'{paper_stem}.out',
                f'{paper_stem}.bbl', f'{paper_stem}.blg', f'{paper_stem}.synctex.gz',
                f'{paper_stem}.synctex(busy)']:
        if os.path.exists(f"{state['files']['Folder']}/{fin}"):
            os.remove(f"{state['files']['Folder']}/{fin}")




#def compile_latex(state: GraphState, paper_name: str, verbose=True):
#    """
#    Function used to compile the paper
#    Args:
#       state: the state of the graph
#       paper: the name of file to compile
#    """
    
#    # get the current directory
#    original_dir = os.getcwd()

#    # go to the folder containing the paper
#    os.chdir(state['files']['Folder'])

#    # get the stem of the paper paper name
#    paper_stem = Path(paper_name).stem
    
#    # try to compile twice for citations and links
#    for i in range(4):  #compile three times to add citations
#        if i==1:
#            if os.path.exists('bibliography.bib'):
#                result = subprocess.run(["bibtex", paper_stem],
#                                        capture_output=True,
#                                        text=True, check=True)
#            continue
            
#        try:
#            result = subprocess.run(["xelatex", paper_name],
#                                    input="\n",
#                                    capture_output=True,
#                                    text=True, check=True)
#            if verbose:
#                print(f"    LaTeX compiled successfully: iteration {i+1}")

#            # Write stdout to log
#            with open(state['files']['LaTeX_log'], 'a') as f:
#                f.write(f"\n==== LaTeX Compilation Pass {i + 1} ====\n")
#                f.write(result.stdout)
            
#        except subprocess.CalledProcessError as e:
#            print(f"    LaTeX compilation failed: iteration {i+1}")
#            with open(state['files']['LaTeX_log'], 'a') as f:
#                f.write(f"\n==== ERROR on Pass {i + 1} ====\n")
#                f.write("---- STDOUT ----\n")
#                f.write(e.stdout or "")
#                f.write("---- STDERR ----\n")
#                f.write(e.stderr or "")

#            # section to fix
#            section = state['latex']['section']

#            # Filter actual errors from stdout/stderr
#            error_lines = []
#            lines = (e.stdout or "") .splitlines() + (e.stderr or "").splitlines()
#            show_context = 0
#            for line in lines:
#                if line.lstrip().startswith("!"):
#                    error_lines.append("\n" + line)
#                    show_context = 3  # show 3 lines after the error
#                elif show_context > 0:
#                    error_lines.append(line)
#                    show_context -= 1
#            error_msg = ' '.join(line.strip() for line in error_lines if line.strip())

#            print(error_lines)
#            latex_lines = []
#            for line in lines:
#                match = re.search(r'l\.(\d+)', line)
#                if match:
#                    latex_lines.append(match.group(1))
#                    print(f"Found line number: {match.group(1)}")
#            latex_lines = set(latex_lines)

#            fixed_text = fix_latex_bug(state, state['paper'][section], error_msg)
#            state['paper'][section] = fixed_text
#            sys.exit()

#    # remove auxiliary files
#    for fin in [f'{paper_stem}.aux', f'{paper_stem}.log', f'{paper_stem}.out',
#                f'{paper_stem}.bbl', f'{paper_stem}.blg', f'{paper_stem}.synctex.gz',
#                f'{paper_stem}.synctex(busy)']:
#        if os.path.exists(fin):  os.remove(fin)
                        
#    os.chdir(original_dir)


journal_dict = {
    Journal.NONE: {"article": "article",
                   "bibliographystyle": "abbrv",
                   "sty": rf"",
                   "affiliation":rf"\date{{Anthropic, Gemini \& OpenAI servers. Planet Earth.}}",
                   "maketitle":rf"\maketitle",
                },
    Journal.AAS: {"article": "aastex631",
                  "bibliographystyle":"aasjournal",
                  "sty": rf"\usepackage{{aas_macros}}",
                  "affiliation":rf"\affiliation{{Anthropic, Gemini \& OpenAI servers. Planet Earth.}}",
                  "maketitle":rf"",
                },
    Journal.JHEP: {"article": "article",
                   "bibliographystyle":"JHEP",
                   "sty": rf"\usepackage{{jcappub}}",
                   "affiliation": rf"\affiliation{{Anthropic, Gemini \& OpenAI servers. Planet Earth.}}",
                   "maketitle":rf"\maketitle",
                },
    Journal.PASJ: {"article": "pasj01",
                   "bibliographystyle":"aasjournal",
                   "sty": rf"\usepackage{{aas_macros}}",
                   "affiliation":rf"\affiliation{{Anthropic, Gemini \& OpenAI servers. Planet Earth.}}"
                },
}


def save_paper(state: GraphState, paper_name: str):
    """
    This function just saves the current state of the paper

    Args:
       state: state of the graph
       name: name of the file to save the paper
    """

    journaldict = journal_dict[state['journal']]

    paper = rf"""\documentclass[twocolumn]{{{journaldict["article"]}}}

\newcommand{{\vdag}}{{(v)^\dagger}}
\newcommand\aastex{{AAS\TeX}}
\newcommand\latex{{La\TeX}}
\usepackage{{amsmath}}
\usepackage{{multirow}}
\usepackage{{natbib}}
\usepackage{{graphicx}} 
{journaldict["sty"]}

\begin{{document}}

\title{{{state['paper'].get('Title','')}}}

\author{{AstroPilot}}
{journaldict["affiliation"]}

{journaldict["maketitle"]}

\begin{{abstract}}
{state['paper'].get('Abstract','')}
\end{{abstract}}

\keywords{{{state['paper']['Keywords']}}}


\section{{Introduction}}
\label{{sec:intro}}
{state['paper'].get('Introduction','')}

\section{{Methods}}
\label{{sec:methods}}
{state['paper'].get('Methods','')}

\section{{Results}}
\label{{sec:results}}
{state['paper'].get('Results','')}

\section{{Conclusions}}
\label{{sec:conclusions}}
{state['paper'].get('Conclusions','')}

\bibliography{{bibliography}}{{}}
\bibliographystyle{{{journal_dict[journal]["bibliographystyle"]}}}

\end{{document}}
"""
    
    # save paper to file
    f_in = f"{state['files']['Folder']}/{paper_name}"
    with open(f_in, 'w', encoding='utf-8') as f:
        f.write(paper)


def save_bib(state: GraphState):
    with open(f"{state['files']['Folder']}/bibliography_temp.bib", 'a', encoding='utf-8') as f:
        f.write(state['paper']['References'].strip() + "\n")    



def escape_special_chars(text):
    # Split into math and non-math parts
    parts = re.split(r'(\$.*?\$)', text)  # keep $...$ parts intact
    sanitized = []

    for part in parts:
        if part.startswith('$') and part.endswith('$'):
            # Don't touch math parts
            sanitized.append(part)
        else:
            # Escape special characters
            for char, escaped in special_chars.items():
                part = part.replace(char, escaped)
            sanitized.append(part)

    return ''.join(sanitized)


def process_bib_file(input_file, output_file):
    with open(input_file, 'r') as fin:
        lines = fin.readlines()

    processed_lines = []
    for line in lines:
        if line.strip().startswith('title') or line.strip().startswith('journal'):
            key, value = line.split('=', 1)
            # quote_char = '"' if '"' in value else '{'
            content = re.search(r'[{\"](.+)[}\"]', value).group(1)
            escaped_content = escape_special_chars(content)

            # Optional: preserve acronyms (wrap them in braces)
            escaped_content = re.sub(r'\b([A-Z]{2,})\b', r'{\1}', escaped_content)

            processed_lines.append(f'  {key.strip()} = {{{escaped_content}}},\n')
        else:
            processed_lines.append(line)

    with open(output_file, 'w') as fout:
        fout.writelines(processed_lines)

    print(f"Sanitized BibTeX saved to: {output_file}")



def fix_latex_bug(state, text, error):
    """
    This function tries to fix the error identified by LaTeX
    """

    PROMPT = fix_latex_bug_prompt(state, text, error)
    state, result = LLM_call(PROMPT, state)
    result = extract_latex_block(state, result, "Text")

    return result
