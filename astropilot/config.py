from pathlib import Path

# Using pathlib (modern approach) to define the base directory as the directory that contains this file.
BASE_DIR = Path(__file__).resolve().parent

# REPO_DIR is defined as one directory above the package
REPO_DIR = BASE_DIR.parent
## in colab we need REPO_DIR = "/content/AstroPilot/"

LaTeX_DIR = BASE_DIR / ".." / "LaTeX"

DEFAUL_PROJECT_NAME = "project"
"""Default name of the project"""

# Constants for defining .md files and folder names
INPUT_FILES = "input_files"
PLOTS_FOLDER = "plots"

DESCRIPTION_FILE = "data_description.md"
IDEA_FILE = "idea.md"
METHOD_FILE = "methods.md"
RESULTS_FILE = "results.md"

