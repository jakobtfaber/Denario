import requests
import sys,os,re,json
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from src.prompts import fixer_prompt, LaTeX_prompt
from src.parameters import GraphState
from src.llm import llm


def json_parser(text):
    """
    This function extracts the text between ```json ```
    """
    
    json_pattern = r"```json(.*)```"
    match = re.findall(json_pattern, text, re.DOTALL)
    json_string = match[0].strip()
    try:
        parsed_json = json.loads(json_string)
    except json.decoder.JSONDecodeError:
        try:
            json_string = json_string.replace("'", "\"")
            parsed_json = json.loads(json_string)
        except:
            raise Exception('Failed to extract json from text')
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
    result = llm.invoke(PROMPT).content
    
    # Extract caption
    pattern = rf"\\begin{{{section_name}}}(.*?)\\end{{{section_name}}}"
    match = re.search(pattern, result, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        with open(state['files']['Error'], 'w', encoding='utf-8') as f:
            f.write(result)
        raise ValueError(f"Fixer failed as well")



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
    text = text.replace(fr"```latex", "")
    text = text.replace(fr"```", "")

    return text
