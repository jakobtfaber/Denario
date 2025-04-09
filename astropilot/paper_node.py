from langchain_core.runnables import RunnableConfig
from pdflatex import PDFLaTeX
import sys,os,json,re,time, base64
from pathlib import Path
from tqdm import tqdm
import subprocess

from .parameters import GraphState
from .prompts import *
from .llm import llm
from .tools import json_parser

from cmbagent import CMBAgent








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

    # --- Step 3: Remove unwanted LaTeX wrappers ---
    section_text = section_text.replace(r"\documentclass{article}", "")
    section_text = section_text.replace(r"\begin{document}", "")
    section_text = section_text.replace(r"\end{document}", "")
    section_text = section_text.replace(fr"\section{{{section_name}}}", "")
    section_text = section_text.replace(fr"\begin{{{section_name}}}", "")
    section_text = section_text.replace(fr"\end{{{section_name}}}", "")
    section_text = section_text.replace(fr"\maketitle", "")
    print(f'{section_name} written...')

    # --- Step 4: Save paper ---
    state['paper'][section_name] = section_text
    _ = save_paper(state)

    # --- Step 5: Summarize ---
    prompt = summary_prompt(state['paper']['summary'], section_text)
    result = llm.invoke(prompt).content
    match = re.search(r"\\begin{Summary}(.*?)\\end{Summary}", result, re.DOTALL)
    if match:
        state['paper']['summary'] = match.group(1).strip()
    else:
        raise ValueError("No valid summary found.")

    # --- Step 6: Update state ---
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
        
    print('Abstract written...')

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
    pdfl = PDFLaTeX.from_texfile(state['files']['Paper'])

    # try to compile twice for citations and links
    for i in range(2):  # compile twice to resolve references
        try:
            result = subprocess.run(["pdflatex", "paper.tex"],
                                    capture_output=True,
                                    text=True, check=True)
            print(f"LaTeX compiled successfully: iteration {i+1}")

            # Write stdout to log
            with open(state['files']['LaTeX_log'], 'a') as f:
                f.write(f"\n==== LaTeX Compilation Pass {i + 1} ====\n")
                f.write(result.stdout)
            
        except subprocess.CalledProcessError as e:
            print(f"LaTeX compilation failed: iteration {i+1}")
            with open(state['files']['LaTeX_log'], 'a') as f:
                f.write(f"\n==== ERROR on Pass {i + 1} ====\n")
                f.write(e.stdout or "")
                f.write(e.stderr or "")
            
            #pdf, log, completed_process = pdfl.create_pdf(keep_pdf_file=True,
            #                                              keep_log_file=True)
            #f = open(state['files']['LaTeX_log'], 'w')
            #f.write(log.decode("utf-8"));  f.close()
            #if completed_process.returncode != 0:
            #    print(f"❌ LaTeX compilation failed on pass {i+1}")
            #    raise RuntimeError("LaTeX compilation failed.")
            #time.sleep(10)
        #except:
        #    print(f"LaTeX failed to compile on pass {i+1}")
        #    raise RuntimeError(f"LaTeX compilation failed")
            
    os.chdir(original_dir)

##################################################################
def generate_paper(state: GraphState, config: RunnableConfig):
    
    paper = save_paper(state)
    compile_latex(state)
    return{'paper': paper}


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
    for i in tqdm(range(len(files)), desc="Processing figures"):
    
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

    PROMPT = plot_prompt(state, images)
    result = llm.invoke(PROMPT).content
    print('Plots added...')

    # Extract new section
    pattern = r"\\begin{Section}(.*?)\\end{Section}"
    match = re.search(pattern, result, re.DOTALL)
    if match:  results = match.group(1).strip()
    else:
        print('Failed to get Results section...')
        f = open(state['files']['Error'], 'w');  f.write(result);  f.close()
        results = fixer(state, 'Results')

    # --- Remove unwanted LaTeX wrappers ---
    results = results.replace(r"\documentclass{article}", "")
    results = results.replace(r"\begin{document}", "")
    results = results.replace(r"\end{document}", "")
    results = results.replace(r"\section{Results}", "")
    results = results.replace(r"\begin{Results}", "")
    results = results.replace(r"\end{Results}", "")

    # save paper
    state['paper']['Results'] = results
    _ = save_paper(state, state['files']['Paper2'])
    
    return {'paper':{**state['paper'], 'Results': results}}

def refine_results(state: GraphState, config: RunnableConfig):
    """
    This agent takes the results section and improve it
    """

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
    section_text = section_text.replace(r"\documentclass{article}", "")
    section_text = section_text.replace(r"\begin{document}", "")
    section_text = section_text.replace(r"\end{document}", "")
    section_text = section_text.replace(r"\section{Results}", "")
    section_text = section_text.replace(r"\begin{Results}", "")
    section_text = section_text.replace(r"\end{Results}", "")

    # save paper
    state['paper']['Results'] = section_text
    _ = save_paper(state)

    print('Results refined...')

    return {'paper':{**state['paper'],
                     'Results': section_text}}

def keywords_node(state: GraphState, config: RunnableConfig):
    """
    This agent is in charge of getting the keywords for the paper
    """

    # PROMPT = keyword_prompt(state)
    # result = llm.invoke(PROMPT).content
    # print(result)
    cmbagent = CMBAgent()
    PROMPT = f"""
Idea:
{state['idea']['Idea']}

Methods:
{state['idea']['Methods']}
"""
    cmbagent.solve(task="Find the relevant AAS keywords",
               max_rounds=50,
               initial_agent='aas_keyword_finder',
               mode = "one_shot",
               shared_context={
               'text_input_for_AAS_keyword_finder': PROMPT,
               'N_AAS_keywords': 10,
                              }
              )
    aas_keywords = cmbagent.final_context['aas_keywords'] ## here you get the dict with urls
    # Extract keys and join them with a comma.
    aas_keywords_str = ", ".join(aas_keywords.keys())
    # print(aas_keywords)
    # import sys; sys.exit()

    # Extract caption
    # pattern = r"\\begin{keywords}(.*?)\\end{keywords}"
    # match = re.search(pattern, result, re.DOTALL)
    # if match:  keywords = match.group(1).strip()
    # else:
    #     print('Failed to get keywords...')
    #     raise ValueError("Failed to extract keywords")

    # print(keywords)
    # print(aas_keywords_str)
    # print(f'Selected keywords: {aas_keywords_str}')
    # import sys; sys.exit()
    
    return {'paper': {**state['paper'], 'Keywords': aas_keywords_str, 'Keywords_dict_with_urls': aas_keywords}}


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
\affiliation{{Gemini \& OpenAI servers. Planet Earth.}}



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
