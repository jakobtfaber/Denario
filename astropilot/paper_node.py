from langchain_core.runnables import RunnableConfig
import sys,os,re,base64
from pathlib import Path
from tqdm import tqdm
import asyncio
from functools import partial
import random

from .parameters import GraphState
from .prompts import *
from .llm import llm
from .tools import json_parser, fixer, LaTeX_checker, clean_section, extract_latex_block
from .literature import process_tex_file_with_references
from .latex import compile_latex, save_paper, save_bib

from cmbagent import CMBAgent





def keywords_node(state: GraphState, config: RunnableConfig):
    """
    This agent is in charge of getting the keywords for the paper
    """

    # Extract keywords
    PROMPT = keyword_prompt(state)
    result = llm.invoke(PROMPT).content
    keywords = extract_latex_block(state, result, "Keywords")
    
    # Avoid adding \ to the end
    keywords = keywords.replace("\\", "")

    print(f'Selected keywords: {keywords}')
    
    return {'paper': {**state['paper'], 'Keywords': keywords}}


def abstract_node(state: GraphState, config: RunnableConfig):
    """
    This node gets the title and the abstract of the paper
    """

    print(f"Writing Abstract...", end="", flush=True)
    PROMPT = abstract_prompt(state['idea']['idea'])
    result = llm.invoke(PROMPT).content
    
    # Get the abstract
    parsed_json = json_parser(result)
    state['paper']['Title']    = parsed_json["Title"]
    state['paper']['Abstract'] = parsed_json["Abstract"]
    
    # several self-reflection rounds
    for i in range(1):

        # improve abstract
        PROMPT = abstract_reflection(state)
        result = (llm.invoke(PROMPT)).content
        abstract = extract_latex_block(state, result, "Abstract")
        
    print('done')

    # --- Save paper ---
    state['paper']['Abstract'] = abstract
    save_paper(state, state['files']['Paper_v1'])

    # summarize text
    #PROMPT = summary_prompt("", abstract)
    #result = llm.invoke(PROMPT).content
    #summary = extract_latex_block(state, result, "Summary")

    return {'paper':{**state['paper'],
                     'Title': state['paper']['Title'],
                     'Abstract': abstract}}
                     #'summary': summary}}


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
    section_text = LaTeX_checker(state, section_text)

    # --- Step 4: Remove unwanted LaTeX wrappers ---
    section_text = clean_section(section_text, section_name)

    # --- Step 5: Save paper ---
    state['paper'][section_name] = section_text
    save_paper(state, state['files']['Paper_v1'])
    print('done')

    # --- Step 6: Summarize ---
    #prompt = summary_prompt(state['paper']['summary'], section_text)
    #result = llm.invoke(prompt).content
    #summary = extract_latex_block(state, result, "Summary")

    # --- Step 7: Update state ---
    return {"paper": {**state["paper"],
                      section_name: section_text}}
                      #"summary": summary}}


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

#######################################################################################
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
    num_images = len(files)

    # Select a random subset of up to 10 images
    selected_files = random.sample(files, min(num_images, 10))

    # do a loop over all images
    images = {}
    for i, file in enumerate(tqdm(selected_files, desc="Processing figures")):

        image = image_to_base64(file)

        PROMPT = caption_prompt(state, image)
        result = llm.invoke(PROMPT).content
        caption = extract_latex_block(state, result, "Caption")
        caption = LaTeX_checker(state, caption)  #make sure is written in LaTeX
        images[f"image{i}"] = {'name': file.name, 'caption': caption}

    print('Inserting figures...', end="", flush=True)
    PROMPT = plot_prompt(state, images)
    result = llm.invoke(PROMPT).content
    results = extract_latex_block(state, result, "Section")

    # --- Remove unwanted LaTeX wrappers ---
    results = clean_section(results, 'Results')
    
    # save paper and compile it
    state['paper']['Results'] = results
    save_paper(state, state['files']['Paper_v1'])
    print('done')
    compile_latex(state, state['files']['Paper_v1'])
    
    return {'paper':{**state['paper'], 'Results': results}}
#######################################################################################


def refine_results(state: GraphState, config: RunnableConfig):
    """
    This agent takes the results section with plots and improves it
    """

    print('Refining results...', end="")
    PROMPT = refine_results_prompt(state)
    result = llm.invoke(PROMPT).content
    results = extract_latex_block(state, result, "Results")
    
    # --- Remove unwanted LaTeX wrappers ---
    section_text = clean_section(results, 'Results')

    # check that all references are done properly
    section_text = check_references(state, section_text)

    # save paper and compile it
    state['paper']['Results'] = section_text
    save_paper(state, state['files']['Paper_v2'])
    print('done')
    compile_latex(state, state['files']['Paper_v2'])

    return {'paper':{**state['paper'], 'Results': section_text}}
    

def check_references(state: GraphState, text: str)-> str:
    """
    This function will check for wrong references to figures
    """

    PROMPT = references_prompt(text)
    result = llm.invoke(PROMPT).content
    section_text = extract_latex_block(state, result, "Text")

    return section_text
        
#######################################################################################
async def add_citations_async(text, section_name):
    loop = asyncio.get_event_loop()
    func = partial(process_tex_file_with_references, text)
    new_text, references = await loop.run_in_executor(None, func)
    new_text = clean_section(new_text, section_name)
    print(f'    {section_name} done')
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

    save_paper(state, state['files']['Paper_v3'])
    save_bib(state)
    print("✅ Citations added to all sections.")

    # compile latex
    compile_latex(state, state['files']['Paper_v3'])

    return {'paper': state['paper']}
#######################################################################################

