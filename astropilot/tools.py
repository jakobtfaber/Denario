import requests
import sys,os,re,json
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# this function extract the json part of a text
def json_parser(text, llm):
    
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
