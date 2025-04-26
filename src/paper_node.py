from langchain_core.runnables import RunnableConfig
import sys,os,re,random,base64,json
from pathlib import Path
from tqdm import tqdm
import asyncio
from functools import partial
import fitz  # PyMuPDF

from src.parameters import GraphState
from src.prompts import *
from src.llm import llm
from src.tools import json_parser, fixer, LaTeX_checker, clean_section, extract_latex_block
from src.literature import process_tex_file_with_references
from src.latex import compile_latex, save_paper, save_bib, process_bib_file


def temp_file(fin, action, text=None, json_file=False):
    """
    This function reads or writes the content of a temporary file
    fin:  the name of the file
    action: either 'read' of 'write'
    text: when action is 'write', the text to write
    json: whether the file is json or not
    """

    if action=='read':
        with open(fin, 'r', encoding='utf-8') as f:
            if json_file:
                return json.load(f)
            else:
                return f.read()
    elif action=='write':
        with open(fin, 'w', encoding='utf-8') as f:
            if json_file:
                json.dump(text, f, indent=2)
            else:
                f.write(text)
    else:
        raise Exception("wrong action chosen!")
    

def keywords_node(state: GraphState, config: RunnableConfig):
    """
    This agent is in charge of getting the keywords for the paper
    """

    # temporary file with the selected keywords
    f_temp = Path(f"{state['files']['Temp']}/Keywords.tex")

    if f_temp.exists():
        keywords = temp_file(f_temp, 'read')

    else:

        # Extract keywords
        PROMPT = keyword_prompt(state)
        result = llm.invoke(PROMPT).content
        keywords = extract_latex_block(state, result, "Keywords")
    
        # Avoid adding \ to the end
        keywords = keywords.replace("\\", "")

        # write results to temporary file
        temp_file(f_temp, 'write', keywords)
        print(f'Selected keywords: {keywords}')
    
    return {'paper': {**state['paper'], 'Keywords': keywords}}


def abstract_node(state: GraphState, config: RunnableConfig):
    """
    This node gets the title and the abstract of the paper
    """

    # temporary file with the selected keywords
    print(f"Writing Abstract...", end="", flush=True)
    f_temp1 = Path(f"{state['files']['Temp']}/Abstract.tex")
    f_temp2 = Path(f"{state['files']['Temp']}/Title.tex")

    # check if abstract already exists
    if f_temp1.exists():
        abstract                = temp_file(f_temp1, 'read')
        state['paper']['Title'] = temp_file(f_temp2, 'read')

    else:
        PROMPT = abstract_prompt(state)
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

        # save temporary file
        temp_file(f_temp2, 'write', state['paper']['Title'])
        temp_file(f_temp1, 'write', abstract)

        # summarize text
        #PROMPT = summary_prompt("", abstract)
        #result = llm.invoke(PROMPT).content
        #summary = extract_latex_block(state, result, "Summary")

    # Save paper and temporary file
    state['paper']['Abstract'] = abstract
    save_paper(state, state['files']['Paper_v1'])
    print('done')

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

    # temporary file with the selected keywords
    print(f'Writing {section_name}...', end="", flush=True)
    f_temp = Path(f"{state['files']['Temp']}/{section_name}.tex")

    # check if abstract already exists
    if f_temp.exists():
        section_text = temp_file(f_temp, 'read')

    else:
        
        # --- Step 1: Prompt and parse section ---
        prompt = prompt_fn(state)
        result = llm.invoke(prompt).content
        section_text = extract_latex_block(state, result, section_name)

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

        # save temporary file
        temp_file(f_temp, 'write', section_text)

        # --- Step 6: Summarize ---
        #prompt = summary_prompt(state['paper']['summary'], section_text)
        #result = llm.invoke(prompt).content
        #summary = extract_latex_block(state, result, "Summary")
        
    # --- Step 5: Save paper ---
    state['paper'][section_name] = section_text
    save_paper(state, state['files']['Paper_v1'])
    print('done')

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
    ext = image_path.suffix.lower() #get the file extension
    if ext == '.pdf':
        # Convert first page of PDF to PNG bytes using PyMuPDF
        with fitz.open(str(image_path)) as doc:
            img_bytes = doc.load_page(0).get_pixmap().tobytes("png")
        data = img_bytes
    elif ext in {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}:
        with open(image_path, "rb") as file:
            data = file.read()
    else:
        raise ValueError(f"Unsupported image file: {image_path}")
    return base64.b64encode(data).decode('utf-8')


def plots_node(state: GraphState, config: RunnableConfig):
    """
    This function deals with the plots generated, processing all files in batches of 10.
    """

    batch_size = 7 #number of images to process per LLM call
    folder_path = Path(f"{state['files']['Folder']}/{state['files']['Plots']}")
    files = [f for f in folder_path.iterdir()
         if f.is_file() and f.name != '.DS_Store']
    num_images = len(files)

    # If more than 25, randomly select 25
    if num_images > 25:
        random.seed(1)  # for reproducibility
        files = random.sample(files, 25)
        num_images = 25

    # Process in batches
    all_results = []
    for start in range(0, num_images, batch_size):

        batch_files = files[start:start + batch_size]
        
        # temporary file with the images
        f_temp = Path(f"{state['files']['Temp']}/plots_{start+1}_{min(start+batch_size, num_images)}.json")

        if f_temp.exists():
            images = temp_file(f_temp, 'read', json_file=True)

        else:

            images = {}
            for i, file in enumerate(tqdm(batch_files, desc=f"Processing figures {start+1}-{min(start+batch_size, num_images)}")):
                image = image_to_base64(file)

                PROMPT = caption_prompt(state, image)
                result = llm.invoke(PROMPT).content
                caption = extract_latex_block(state, result, "Caption")
                caption = LaTeX_checker(state, caption)  #make sure is written in LaTeX
                images[f"image{i}"] = {'name': file.name, 'caption': caption}

            # save temporary file
            temp_file(f_temp, 'write', images, json_file=True)

        # temporary file with the images
        print(f'   Inserting figures {start+1}-{min(start+batch_size, num_images)}...', flush=True)
        f_temp = Path(f"{state['files']['Temp']}/Results_{start+1}_{min(start+batch_size, num_images)}.tex")
        if f_temp.exists():
            state['paper']['Results'] = temp_file(f_temp, 'read')
        else:
            PROMPT = plot_prompt(state, images)
            result = llm.invoke(PROMPT).content
            results = extract_latex_block(state, result, "Section")

            # Check LaTeX
            results = LaTeX_checker(state, results)

            # --- Remove unwanted LaTeX wrappers ---
            state['paper']['Results'] = clean_section(results, 'Results')

            # save temporary file
            temp_file(f_temp, 'write', state['paper']['Results'])

        # save paper
        save_paper(state, state['files']['Paper_v1'])

    # compile paper
    compile_latex(state, state['files']['Paper_v1'])

    return {'paper':{**state['paper'], 'Results': state['paper']['Results']}}



#######################################################################################
def refine_results(state: GraphState, config: RunnableConfig):
    """
    This agent takes the results section with plots and improves it
    """

    # temporary file with the selected keywords
    print('Refining results...', end="", flush=True)
    f_temp = Path(f"{state['files']['Temp']}/Results_refined.tex")

    # check if this has already been done
    if f_temp.exists():
        section_text = temp_file(f_temp, 'read')
    else:
        PROMPT = refine_results_prompt(state)
        result = llm.invoke(PROMPT).content
        results = extract_latex_block(state, result, "Results")

        # Check LaTeX
        results = LaTeX_checker(state, results)
    
        # --- Remove unwanted LaTeX wrappers ---
        section_text = clean_section(results, 'Results')

        # check that all references are done properly
        section_text = check_references(state, section_text)

        # save temporary file
        temp_file(f_temp, 'write', section_text)

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

    PROMPT = references_prompt(state, text)
    result = llm.invoke(PROMPT).content
    section_text = extract_latex_block(state, result, "Text")

    return section_text
        
#######################################################################################
async def add_citations_async(state, text, section_name):
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

    #sections = ['Introduction', 'Methods', 'Results', 'Conclusions']
    sections = ['Introduction', 'Methods']
    tasks = [add_citations_async(state, state['paper'][section], section) for section in sections]
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

    # save paper and bibliography
    save_paper(state, state['files']['Paper_v3'])
    save_bib(state)

    # sanitize bibliography
    process_bib_file(f"{state['files']['Folder']}/bibliography_temp.bib",
                     f"{state['files']['Folder']}/bibliography.bib")
    print("✅ Citations added to all sections.")

    # compile latex
    compile_latex(state, state['files']['Paper_v3'])

    # make a last clean up of the sections
    print("Making a final check to the sections...")
    for section_name in sections:
        PROMPT = clean_section_prompt(state, state['paper'][section_name])
        result = llm.invoke(PROMPT).content
        section_text = extract_latex_block(state, result, "Text")
        section_text = LaTeX_checker(state, section_text)          #check LaTeX
        section_text = clean_section(section_text, section_name)   #remove unwanted LaTeX text
        state['paper'][section_name] = section_text
    save_paper(state, state['files']['Paper_v4'])
    compile_latex(state, state['files']['Paper_v4'])

    return {'paper': state['paper']}
#######################################################################################

