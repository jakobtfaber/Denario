import requests
import sys,os,re,json
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Set your API key here
load_dotenv()
API_KEY = os.getenv("SEMANTIC_SCHOLAR_KEY")

# Base URL for Semantic Scholar API
BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


def SSAPI(query, limit=10):
    """
    Search for papers similar to the given query using Semantic Scholar API.

    Args:
        query (str): The search query (e.g., keywords or paper title).
        limit (int): Number of papers to retrieve (default is 10).

    Returns:
        list: A list of dictionaries containing paper details.
    """
    
    params = {"query": query,
              "limit": limit,
              "fields": "title,authors,year,abstract,url"}

    # Conditionally include headers if API_KEY is available
    if API_KEY:
        response = requests.get(BASE_URL, headers={"x-api-key": API_KEY}, params=params)
    else:
        response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

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
            #print('And this...')
            #print(json_string)
            #json_string = llm.invoke([HumanMessage(content='''Your task is to fix the errors in the text below and return the correct JSON format. Please revise the text below and return the correct JSON text.
#
#Original text: 
#%s
#
#Please respond with this format:
#
#<JSON>
#
#where <JSON> is the corrected JSON text
#'''%json_string)])
#            parsed_json = json.loads(json_string)
    return parsed_json


def dump_2_file(f_in, string):
    f = open(f_in, 'a')
    f.write('%s\n\n'%string)
    f.close()
    

# Example usage
if __name__ == "__main__":
    #query = "Transformer models in natural language processing"
    query = "CAMELS, cosmology and astrophysics"
    results = search_similar_papers(query)

    total_papers = results.get("total", [])
    token        = results.get("token", [])
    papers       = results.get("data", [])

    if papers:
        print("Found papers %d potentially relevant papers. Listing the first 10:"%total_papers)
        for idx, paper in enumerate(papers, start=1):
            title = paper.get("title", "No Title")
            authors = ", ".join([author.get("name", "Unknown") for author in paper.get("authors", [])])
            year = paper.get("year", "Unknown Year")
            abstract = paper.get("abstract", "No Abstract")
            url = paper.get("url", "No URL")
            print(f"\n{idx}. {title} ({year})")
            print(f"   Authors: {authors}")
            print(f"   Abstract: {abstract}")
            print(f"   URL: {url}")
    else:
        print("No papers found.")
