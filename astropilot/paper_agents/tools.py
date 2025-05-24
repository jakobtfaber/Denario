import re
import json
from pathlib import Path

from .prompts import fixer_prompt, LaTeX_prompt
from .parameters import GraphState


def LLM_call(prompt, state):
    """
    This function calls the LLM and update tokens
    """

    message = state['llm']['llm'].invoke(prompt)
    input_tokens  = message.usage_metadata['input_tokens']
    output_tokens = message.usage_metadata['output_tokens']
    if output_tokens>state['llm']['max_output_tokens']:
        print('WARNING!! Max output tokens reach!')
    state['tokens']['ti'] += input_tokens
    state['tokens']['to'] += output_tokens
    state['tokens']['i'] = input_tokens
    state['tokens']['o'] = output_tokens
    with open(state['files']['LLM_calls'], 'a') as f:
        f.write(f"{state['tokens']['i']} {state['tokens']['o']} {state['tokens']['ti']} {state['tokens']['to']}\n")
    
    return state, message.content


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
                latex_text = f.read()
                
                # Extract content between \begin{document} and \end{document}
                match = re.search(r'\\begin{document}(.*?)\\end{document}',
                                  latex_text, re.DOTALL)

                if match:
                    extracted_text = match.group(1).strip()
                    return extracted_text
                else:
                    raise Exception("Text not found on file!")

    elif action=='write':
        with open(fin, 'w', encoding='utf-8') as f:
            if json_file:
                json.dump(text, f, indent=2)
            else:
                latex_text = rf"""\documentclass[twocolumn]{{aastex631}}

\usepackage{{amsmath}}
\usepackage{{multirow}}
\begin{{document}}

{text}

\end{{document}}
                """
                f.write(latex_text)
    else:
        raise Exception("wrong action chosen!")


def json_parser(text):
    """
    This function extracts the text between ```json ```
    """
    
    json_pattern = r"```json(.*)```"
    match = re.findall(json_pattern, text, re.DOTALL)
    json_string = match[0].strip()
    json_string = json_string.replace("\\", "\\\\") #deal with unescaped backslashes
    try:
        parsed_json = json.loads(json_string)
    except json.decoder.JSONDecodeError:
        try:
            json_string = json_string.replace("'", "\"")
            parsed_json = json.loads(json_string)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON: {e}")
    return parsed_json


def extract_latex_block(state: GraphState, text: str, block: str) -> str:
    r"""
    This function takes some text and extracts the TEXT located between
    \begin{block}
    TEXT
    \end{block}
    """
    
    pattern = rf"\\begin{{{block}}}(.*?)\\end{{{block}}}"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        return match.group(1).strip()    

    # in case it fails
    with open(state['files']['Error'], 'w', encoding='utf-8') as f:
        f.write(text)

    # try to fix it using fixed
    try:
        return fixer(state, block)
    except ValueError:
        raise ValueError(f"Failed to extract {block}")
    

def fixer(state: GraphState, section_name):
    """
    This function will try to fix the errors with automatic parsing
    """

    path = Path(state['files']['Error'])
    with path.open("r", encoding="utf-8") as f:
        Text = f.read()
    
    PROMPT = fixer_prompt(Text, section_name)
    state, result = LLM_call(PROMPT, state)
    #result = llm.invoke(PROMPT).content
    
    # Extract caption
    pattern = rf"\\begin{{{section_name}}}(.*?)\\end{{{section_name}}}"
    match = re.search(pattern, result, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        with open(state['files']['Error'], 'w', encoding='utf-8') as f:
            f.write(result)
        raise ValueError("Fixer failed as well")



def LaTeX_checker(state, text):

    PROMPT = LaTeX_prompt(text)
    state, result = LLM_call(PROMPT, state)
    #result = llm.invoke(PROMPT).content
    text = extract_latex_block(state, result, "Text")
    return text


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
    text = text.replace(r"\maketitle", "")
    text = text.replace(r"<PARAGRAPH>", "")
    text = text.replace(r"</PARAGRAPH>", "")
    text = text.replace(r"</{section}>", "")
    text = text.replace(r"<{section}>", "")
    text = text.replace(r"```latex", "")
    text = text.replace(r"```", "")
    text = text.replace(r"\usepackage{amsmath}", "")

    return text


def check_images_in_text(state, images):
    """
    This function checks whether the LLM has put the images in the text or not
    """

    # Check that the images are in the text
    for key, value in images.items():
        if value["name"] not in state['paper']['Results']:
            return False
    return True

            
