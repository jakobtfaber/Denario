import os
from pathlib import Path

# Using pathlib (modern approach) to define the base directory as the directory that contains this file.
BASE_DIR = Path(__file__).resolve().parent
# REPO_DIR is defined as one directory above the package
REPO_DIR = BASE_DIR.parent

## in colab we need REPO_DIR = "/content/AstroPilot/"