import os
import re
import urllib.request
import urllib.parse
import json
import warnings
import hashlib

# ... other imports ...
from pathlib import Path
from .llm import LLM, models
from .key_manager import KeyManager


def input_check(str_input: str) -> str:
    """Check if input is a string or a markdown file path and return content.

    If a file path ending with ".md" is provided, read and return its content.
    Otherwise, return the string as-is.
    """

    if str_input.endswith(".md"):
        with open(str_input, "r") as f:
            content = f.read()
    elif isinstance(str_input, str):
        content = str_input
    else:
        raise ValueError("Input must be a string or a path to a markdown file.")
    return content


def llm_parser(llm: LLM | str) -> LLM:
    """Get the LLM instance from a string."""

    if isinstance(llm, str):
        # [BATCH FIX] Force all Gemini models to gemini-3-flash-preview
        if "gemini" in llm:
            llm = "gemini-3-flash-preview"
        try:
            llm = models[llm]
        except KeyError:
            warnings.warn(
                f"LLM '{llm}' not available in predefined models. "
                f"Creating a generic wrapper for it. "
                f"Available keys: {list(models.keys())}"
            )
            # Create a generic LLM instance for the unknown model string
            llm = LLM(name=llm, max_output_tokens=16384, temperature=0.5)
    return llm


def extract_file_paths(markdown_text):
    """
    Extract the bulleted file paths from markdown text
    and check if they exist and are absolute paths.

    Args:
        markdown_text (str): The markdown text containing file paths

    Returns:
        tuple: (existing_paths, missing_paths)
    """

    # Pattern to match file paths in markdown bullet points
    pattern = r"-\s*([^\n]+\.(?:csv|txt|md|py|json|yaml|yml|xml|html|css|js|ts|tsx|jsx|java|cpp|c|h|hpp|go|rs|php|rb|pl|sh|bat|sql|log))"

    # Find all matches
    matches = re.findall(pattern, markdown_text, re.IGNORECASE)

    # Clean up paths and check existence
    existing_paths = []
    missing_paths = []

    for match in matches:
        path = match.strip()
        if os.path.exists(path) and os.path.isabs(path):
            existing_paths.append(path)
        else:
            missing_paths.append(path)

    return existing_paths, missing_paths


def check_file_paths(content: str) -> None:
    """Check that file paths indicated in content text have the proper format"""

    existing_paths, missing_paths = extract_file_paths(content)

    if len(missing_paths) > 0:
        warnings.warn(
            f"The following data files paths in the data description are not in the right format or do not exist:\n"
            f"{missing_paths}\n"
            f"Please fix them according to the convention '- /absolute/path/to/file.ext'\n"
            f"otherwise this may cause hallucinations in the LLMs."
        )

    if len(existing_paths) == 0:
        warnings.warn(
            "No data files paths were found in the data description. If you want to provide input data, ensure that you indicate their path, otherwise this may cause hallucinations in the LLM in the get_results() workflow later on."
        )


def create_work_dir(work_dir: str | Path, name: str) -> Path:
    """Create working directory"""

    work_dir = os.path.join(work_dir, f"{name}_generation_output")
    os.makedirs(work_dir, exist_ok=True)
    return Path(work_dir)


def get_task_result(chat_history, name: str):
    """Get task result from chat history"""

    for obj in chat_history[::-1]:
        if obj["name"] == name:
            result = obj["content"]
            break
    task_result = result
    return task_result


def in_notebook():
    """Check whether the code is run from a Jupyter Notebook or not, to use different display options"""

    try:
        from IPython import get_ipython  # type: ignore

        if "IPKernelApp" not in get_ipython().config:  # type: ignore # pragma: no cover
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True


class WolframAlphaClient:
    def __init__(self, app_id=None, enable_hitl=False, cache_dir=None):
        self.app_id = app_id
        if not self.app_id:
            try:
                keys = KeyManager()
                keys.get_keys_from_env()
                self.app_id = keys.WOLFRAM_APP_ID
            except Exception as e:
                print(f"Failed to load Wolfram App ID from KeyManager: {e}")

        self.enable_hitl = enable_hitl
        self.base_url = "http://api.wolframalpha.com/v2/query"
        self.cache_dir = cache_dir
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)

    def query(self, query, use_cache=True):
        if use_cache and self.cache_dir:
            try:
                query_hash = hashlib.md5(query.encode()).hexdigest()
                cache_file = os.path.join(self.cache_dir, f"{query_hash}.json")
                if os.path.exists(cache_file):
                    with open(cache_file, "r") as f:
                        return json.load(f)
            except Exception as e:
                print(f"Cache read error: {e}")

        if not self.app_id:
            return {"queryresult": {"success": False, "error": "No App ID provided"}}

        params = {
            "appid": self.app_id,
            "input": query,
            "output": "json",
            "format": "plaintext,latex,mathml,image",
        }
        url = f"{self.base_url}?{urllib.parse.urlencode(params)}"

        try:
            with urllib.request.urlopen(url) as response:
                if response.status != 200:
                    return {
                        "queryresult": {
                            "success": False,
                            "error": f"HTTP {response.status}",
                        }
                    }
                data = response.read()
                result = json.loads(data)

                if use_cache and self.cache_dir and result.get("queryresult", {}).get("success"):
                    try:
                        query_hash = hashlib.md5(query.encode()).hexdigest()
                        cache_file = os.path.join(self.cache_dir, f"{query_hash}.json")
                        with open(cache_file, "w") as f:
                            json.dump(result, f)
                    except Exception as e:
                        print(f"Cache write error: {e}")
                
                return result
        except Exception as e:
            return {"queryresult": {"success": False, "error": str(e)}}

    def needs_hitl_review(self, result):
        # Basic logic: if success is false but no specific error, or low confidence
        # For now, keep it simple
        return False

    def get_hitl_prompt(self, query, result):
        return (
            f"Wolfram Alpha query '{query}' returned ambiguous results. Please review."
        )

    @staticmethod
    def extract_structured_results(result):
        # Default empty structure
        structured = {
            "latex": [],
            "assumptions": [],
            "sources": [],
            "plaintext": "",
            "mathml": "",
            "images": [],
        }

        if not result or "queryresult" not in result:
            return structured

        query_result = result["queryresult"]
        if not query_result.get("success"):
            return structured

        pods = query_result.get("pods", [])

        # Extract content from pods
        for pod in pods:
            subpods = pod.get("subpods", [])
            for subpod in subpods:
                if "plaintext" in subpod and subpod["plaintext"]:
                    if not structured["plaintext"]:  # Keep first/primary result mostly
                        structured["plaintext"] = subpod["plaintext"]
                    else:
                        structured["plaintext"] += "\n" + subpod["plaintext"]

                # Check for other formats if available in subpod (depends on API response structure)
                # Wolfram JSON often puts them in 'img', 'plaintext' keys directly
                # If latex was requested, it might be in a specific structure

        # Simulating latex extraction if plaintext looks like math or if specific pods exist
        # Real Wolfram JSON for latex is specific.
        # For robustness, we will try to find any latex-like content or just return plaintext as primary.

        return structured

    @staticmethod
    def extract_primary_text(result):
        if not result or "queryresult" not in result:
            return None

        query_result = result["queryresult"]
        if not query_result.get("success"):
            return None

        # Try to find 'Result' pod
        pods = query_result.get("pods", [])
        for pod in pods:
            if pod.get("primary", False) or pod.get("title") == "Result":
                subpods = pod.get("subpods", [])
                for subpod in subpods:
                    if "plaintext" in subpod and subpod["plaintext"]:
                        return subpod["plaintext"]

        # Fallback to first pod
        if pods:
            subpods = pods[0].get("subpods", [])
            if subpods and "plaintext" in subpods[0]:
                return subpods[0]["plaintext"]

        return None
