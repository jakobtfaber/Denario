from langchain_core.runnables import RunnableConfig
from pdflatex import PDFLaTeX
import sys,os,json,re,time, base64
from pathlib import Path
from tqdm import tqdm
import subprocess
import requests
import asyncio
from functools import partial

from src.parameters import GraphState
from src.prompts import *
from src.llm import llm
from src.tools import json_parser
from src.literature import process_tex_file_with_references


def clean_section(text, section):
    """
    This function performs some clean up of unwanted LaTeX wrappers
    """

    text = text.replace(r"\documentclass{article}", "")
    text = text.replace(r"\begin{document}", "")
    text = text.replace(r"\end{document}", "")
    text = text.replace(fr"\section{{{section}}}", "")
    text = text.replace(fr"\section*{{{section}}}", "")
    text = text.replace(fr"\begin{{{section}}}", "")
    text = text.replace(fr"\end{{{section}}}", "")
    text = text.replace(fr"\maketitle", "")
    text = text.replace(fr"<PARAGRAPH>", "")
    text = text.replace(fr"</PARAGRAPH>", "")

    return text


def section_node(state: GraphState, config: RunnableConfig, section_name: str,
                 prompt_fn, reflection_fn=None):
    """
    This function generates a section of the paper
    Args:
      state: the state of the graph
      config: the config of the graph
      section_name: the name of the section to write
      prompt_fn: the prompt function for the section
      reflection_fn: whether to use self-reflections to improve the text
    """
    
    # --- Step 1: Prompt and parse section ---
    print(f'Writing {section_name}...', end="", flush=True)
    prompt = prompt_fn(state)
    result = llm.invoke(prompt).content

    # Try to extract section content via markers
    pattern = fr"\\begin{{{section_name}}}(.*?)\\end{{{section_name}}}"
    match = re.search(pattern, result, re.DOTALL)
    if match:
        section_text = match.group(1).strip()
    else:
        raise ValueError(f"No valid \\begin{{{section_name}}} section found.")
    state['paper'][section_name] = section_text

    # --- Step 2: Optional self-reflection ---
    if reflection_fn:
        for _ in range(2):
            prompt = reflection_fn(state)
            section_text = llm.invoke(prompt).content

    # --- Step 3: Check LaTeX ---
    section_text = LaTeX_checker(section_text)

    # --- Step 4: Remove unwanted LaTeX wrappers ---
    section_text = clean_section(section_text, section_name)

    # --- Step 5: Save paper ---
    state['paper'][section_name] = section_text
    _ = save_paper(state)
    print('done')

    # --- Step 6: Summarize ---
    prompt = summary_prompt(state['paper']['summary'], section_text)
    result = llm.invoke(prompt).content
    match = re.search(r"\\begin{Summary}(.*?)\\end{Summary}", result, re.DOTALL)
    if match:
        state['paper']['summary'] = match.group(1).strip()
    else:
        raise ValueError("No valid summary found.")

    # --- Step 7: Update state ---
    return {"paper": {**state["paper"],
                      section_name: section_text,
                      "summary": state["paper"]["summary"]}}


# get the functions for the different nodes
def introduction_node(state: GraphState, config: RunnableConfig):
    return section_node(state, config, section_name="Introduction",
                        prompt_fn=introduction_prompt,
                        reflection_fn=introduction_reflection)

def methods_node(state: GraphState, config: RunnableConfig):
    return section_node(state, config, section_name="Methods",
                        prompt_fn=methods_prompt,
                        reflection_fn=None)

def results_node(state: GraphState, config: RunnableConfig):
    return section_node(state, config, section_name="Results",
                        prompt_fn=results_prompt,
                        reflection_fn=None)

def conclusions_node(state: GraphState, config: RunnableConfig):
    return section_node(state, config, section_name="Conclusions",
                        prompt_fn=conclusions_prompt,
                        reflection_fn=None)


def abstract_node(state: GraphState, config: RunnableConfig):
    """
    This node gets the title and the abstract of the paper
    """

    print(f"Writing Abstract...", end="", flush=True)
    PROMPT = abstract_prompt(state['idea']['idea'])
    result = llm.invoke(PROMPT)
    result = result.content
    
    # Get the abstract
    parsed_json = json_parser(result, llm)
    state['paper']['Title'] = parsed_json["Title"]
    state['paper']['Abstract'] = parsed_json["Abstract"]
    
    # several self-reflection rounds
    for i in range(2):

        # improve abstract
        PROMPT = abstract_reflection(state)
        abstract = (llm.invoke(PROMPT)).content
        pattern = r"\\begin{Abstract}(.*?)\\end{Abstract}"
        match = re.search(pattern, abstract, re.DOTALL)
        if match:  abstract = match.group(1).strip()
        else:      raise ValueError("No valid Abstract section found.")
    print('done')

    # --- Save paper ---
    state['paper']['Abstract'] = abstract
    _ = save_paper(state)

    # summarize text
    PROMPT = summary_prompt("", abstract)
    result = llm.invoke(PROMPT)
    pattern = r"\\begin{Summary}(.*?)\\end{Summary}"
    match = re.search(pattern, result.content, re.DOTALL)
    if match:  state['paper']['summary'] = match.group(1).strip()  
    else:      raise ValueError("No valid summary found.")

    return {'paper':{**state['paper'],
                     'Title': state['paper']['Title'],
                     'Abstract': abstract,
                     'summary': state['paper']['summary']}}

    
def compile_latex(state):
    """
    Function used to compile the paper
    """
    
    # get the current directory
    original_dir = os.getcwd()

    # go to the folder containing the paper
    os.chdir(state['files']['Paper_folder'])

    # try to compile twice for citations and links
    for i in range(3):  # compile twice to resolve references
        try:
            result = subprocess.run(["xelatex", state['files']['Paper3']],
                                    capture_output=True,
                                    text=True, check=True)
            print(f"LaTeX compiled successfully: iteration {i+1}")

            # Write stdout to log
            with open(state['files']['LaTeX_log'], 'a') as f:
                f.write(f"\n==== LaTeX Compilation Pass {i + 1} ====\n")
                f.write(result.stdout)

            if i==0:
                result = subprocess.run(["bibtex", Path(state['files']['Paper3']).stem],
                                        capture_output=True,
                                        text=True, check=True)

            
        except subprocess.CalledProcessError as e:
            print(f"LaTeX compilation failed: iteration {i+1}")
            with open(state['files']['LaTeX_log'], 'a') as f:
                f.write(f"\n==== ERROR on Pass {i + 1} ====\n")
                f.write(e.stdout or "")
                f.write(e.stderr or "")
                        
    os.chdir(original_dir)

##################################################################
def generate_paper(state: GraphState, config: RunnableConfig):
    
    paper = save_paper(state)
    compile_latex(state)
    #return{'paper': paper}


##################################################################
def image_to_base64(image_path):
    with open(image_path, "rb") as file:
        binary_data = file.read()
        image_data = base64.b64encode(binary_data).decode('utf-8')
        return image_data

def plots_node(state: GraphState, config: RunnableConfig):
    """
    This function deals with the plots generated
    """

    folder_path = Path(state['files']['Plots'])
    files = [f for f in folder_path.iterdir() if f.is_file()]

    # do a loop over all images
    images = {}
    #for i in tqdm(range(len(files)), desc="Processing figures"):
    for i in tqdm(range(10), desc="Processing figures"):
    
        image = image_to_base64(files[i])

        PROMPT = caption_prompt(state, image)
        result = llm.invoke(PROMPT).content

        # Extract caption
        pattern = r"\\begin{Caption}(.*?)\\end{Caption}"
        match = re.search(pattern, result, re.DOTALL)
        if match:  caption = match.group(1).strip()
        else:      raise ValueError(f"No valid caption found.")

        images[f"image{i}"] = {'name':files[i].name,
                               'caption':caption}

    print('Inserting figures...', end="", flush=True)
    PROMPT = plot_prompt(state, images)
    result = llm.invoke(PROMPT).content

    # Extract new section
    pattern = r"\\begin{Section}(.*?)\\end{Section}"
    match = re.search(pattern, result, re.DOTALL)
    if match:  results = match.group(1).strip()
    else:
        print('Failed to get Results section...')
        f = open(state['files']['Error'], 'w');  f.write(result);  f.close()
        results = fixer(state, 'Results')

    # --- Remove unwanted LaTeX wrappers ---
    results = clean_section(results, 'Results')
    
    # save paper
    state['paper']['Results'] = results
    _ = save_paper(state, state['files']['Paper'])
    print('done')
    
    return {'paper':{**state['paper'], 'Results': results}}


def refine_results(state: GraphState, config: RunnableConfig):
    """
    This agent takes the results section and improve it
    """

    print('Refining results...', end="")
    PROMPT = refine_results_prompt(state)
    result = llm.invoke(PROMPT).content

    # Extract caption
    pattern = r"\\begin{Results}(.*?)\\end{Results}"
    match = re.search(pattern, result, re.DOTALL)
    if match:  section_text = match.group(1).strip()
    else:
        print('Failed to get Results section...')
        f = open(state['files']['Error'], 'w');  f.write(result);  f.close()
        fixer(state, 'Results')

    # --- Remove unwanted LaTeX wrappers ---
    section_text = clean_section(section_text, 'Results')

    # check that all references are done properly
    section_text = check_references(section_text)

    # save paper
    state['paper']['Results'] = section_text
    _ = save_paper(state, state['files']['Paper2'])
    print('done')

    return {'paper':{**state['paper'],
                     'Results': section_text}}

def keywords_node(state: GraphState, config: RunnableConfig):
    """
    This agent is in charge of getting the keywords for the paper
    """

    PROMPT = keyword_prompt(state)
    result = llm.invoke(PROMPT).content

    # Extract caption
    pattern = r"\\begin{Keywords}(.*?)\\end{Keywords}"
    match = re.search(pattern, result, re.DOTALL)
    if match:  keywords = match.group(1).strip()
    else:
        print('Failed to get keywords...')
        raise ValueError("Failed to extract keywords")

    # Avoid adding \ to the end
    keywords = keywords.replace("\\", "")

    print(f'Selected keywords: {keywords}')
    
    return {'paper': {**state['paper'], 'Keywords': keywords}}


def LaTeX_checker(text):

    PROMPT = LaTeX_prompt(text)
    result = llm.invoke(PROMPT).content

    # Extract caption
    pattern = r"\\begin{Text}(.*?)\\end{Text}"
    match = re.search(pattern, result, re.DOTALL)
    if match:  text = match.group(1).strip()
    else:
        print('Failed to get LaTeX...')
        raise ValueError("Failed to extract LaTeX")

    return text
    

def LaTeX_node(state: GraphState, config: RunnableConfig):
    """
    This agent goes through all sections of the papers and checks if they are in LaTeX
    """

    """
    for section in ['Introduction', 'Methods', 'Results', 'Conclusions']:

        print(f'Refining {section}')
        
        PROMPT = LaTeX_prompt(state['paper'][section])
        result = llm.invoke(PROMPT).content

        # Extract caption
        pattern = r"\\begin{LaTeX}(.*?)\\end{LaTeX}"
        match = re.search(pattern, result, re.DOTALL)
        if match:  section_text = match.group(1).strip()
        else:
            f = open('Error.txt', 'w');  f.write(result);  f.close()
            raise ValueError(f"No valid results found.")
        
        state['paper'][section] = section_text

        # save paper
        save_paper(state)
    """

    return state


def check_references(text):
    """
    This function will check for wrong references to figures
    """

    PROMPT = references_prompt(text)
    result = llm.invoke(PROMPT).content

    # Extract text
    pattern = rf"\\begin{{Text}}(.*?)\\end{{Text}}"
    match = re.search(pattern, result, re.DOTALL)
    if match:  section_text = match.group(1).strip()
    else:
        f = open('Error.txt', 'w');  f.write(result);  f.close()
        raise ValueError(f"Failed to fix references")

    return section_text
    

    
#######################################################################################
#def citations_node(state: GraphState, config: RunnableConfig):
#    """
#    This agent adds citations to the paper
#    """
#
#    text = state['paper']['Introduction']
#
#    # add citations
#    print('Adding citations...', end="", flush=True)
#    text, references = process_tex_file_with_references(text)
#
#    # --- Remove unwanted LaTeX wrappers ---
#    text = clean_section(text, 'Introduction')
#    
#    state['paper']['Introduction'] = text
#    state['paper']['References']   = references
#    
#    save_paper(state, name=state['files']['Paper3'])
#    save_bib(state)
#    print('done')
#    
#    return {'paper': {**state['paper'], 'Introduction': text, 'References': references}}
    

async def add_citations_async(text, section_name):
    loop = asyncio.get_event_loop()
    func = partial(process_tex_file_with_references, text)
    new_text, references = await loop.run_in_executor(None, func)
    new_text = clean_section(new_text, section_name)
    print(f'    {section_name} done')
    #with open('borrar.bib', 'w') as f:
    #    f.write(references)
    return section_name, new_text, references

async def citations_node(state: GraphState, config: RunnableConfig):
    """
    This agent adds citations asynchronously to all main sections.
    """

    print("Adding citations...")

    sections = ['Introduction', 'Methods', 'Results', 'Conclusions']
    tasks = [add_citations_async(state['paper'][section], section) for section in sections]
    results = await asyncio.gather(*tasks)

    # Deduplicate full BibTeX entries
    bib_entries_set = set()
    bib_entries_list = []

    for section_name, updated_text, references in results:
        state['paper'][section_name] = updated_text

        # Break the full .bib string into entries by \n\n
        entries = references.strip().split('\n\n')
        for entry in entries:
            clean_entry = entry.strip()
            if clean_entry and clean_entry not in bib_entries_set:
                bib_entries_list.append(clean_entry)

    # Save all combined deduplicated BibTeX entries as a single string
    state['paper']['References'] = "\n\n".join(bib_entries_list)

    save_paper(state, name=state['files']['Paper3'])
    save_bib(state)
    print("✅ Citations added to all sections.")

    return {'paper': state['paper']}





def save_paper(state, name=None):
    """
    This function just saves the current state of the paper
    """

    paper = rf"""\documentclass[twocolumn]{{aastex631}}

\newcommand{{\vdag}}{{(v)^\dagger}}
\newcommand\aastex{{AAS\TeX}}
\newcommand\latex{{La\TeX}}
\usepackage{{amsmath}}

\begin{{document}}

\title{{{state['paper'].get('Title','')}}}

\author{{AstroPilot}}
\affiliation{{Anthropic, Gemini \& OpenAI servers. Planet Earth.}}

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
\bibliographystyle{{aasjournal}}

\end{{document}}
"""
    
    # put paper on a file and compile it
    if name is None:  fname = state['files']['Paper']
    else:             fname = name
    f_in = f"{state['files']['Paper_folder']}/{fname}"
    f = open(f_in, 'w');  f.write(paper);  f.close()    

    return paper


def save_bib(state):
    with open(f"{state['files']['Paper_folder']}/bibliography.bib", 'a', encoding='utf-8') as f:
        f.write(state['paper']['References'].strip() + "\n")    
    

def fixer(state: GraphState, section_name):
    """
    This function will try to fix the errors with automatic parsing
    """

    path = Path(state['files']['Error'])
    with path.open("r", encoding="utf-8") as f:
        Text = f.read()
    
    PROMPT = fixer_prompt(Text, section_name)
    result = llm.invoke(PROMPT).content

    # Extract caption
    pattern = rf"\\begin{{{section_name}}}(.*?)\\end{{{section_name}}}"
    match = re.search(pattern, result, re.DOTALL)
    if match:  section_text = match.group(1).strip()
    else:
        f = open('Error.txt', 'w');  f.write(result);  f.close()
        raise ValueError(f"Fixer failed as well")

    return section_text
