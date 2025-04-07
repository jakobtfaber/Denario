# AstroPilot

AstroPilot is a multiagent system designed to automatize scientific research in astrophysics and cosmology

## Installation

```bash
git clone https://github.com/AstroPilot-AI/AstroPilot
cd AstroPilot
python -m venv AP_env
source AP_env/bin/activate
pip install .
```

At this point, the library should be installed together with all its dependencies. Next we need to create a `.env` file with this content:

```
# Gemini parameters (needed if using Gemini. Default)
GOOGLE_API_KEY=your_google_api_key

# OpenAI parameters (needed if using ChatGPT)
#OPENAI_API_KEY=your_openai_api_key

# Anthropic parameters (needed if using Sonnet-3.7)
#ANTHROPIC_API_KEY=your_anthropic_api_key

# LangChain parameters (optional)
#LANGCHAIN_TRACING_V2=true
#LANGCHAIN_API_KEY=your_langchain_api_key
#LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
#LANGCHAIN_PROJECT=Tools
```

## Setup

The code assumes the existence of 2 folders in the main directory:

- **Input_Files**. This file should contain:

  - idea.md: This file contains a summary of the paper idea
  - methods.md: This file contains the methods of the paper
  - results.md: This file contains the results of the analysis
  - plots: This is a folder and contains all the plots of the paper

- **LaTeX**. This folder contains the files `aasjournal.bst`, `aastex631.cls`, `bibliography.bib` needed to compile the paper. The paper, called `paper.tex` and `paper.pdf` will be place in this folder

For new ideas/project, modify the files in the Input_Files folder accordingly.

## Run

To run the code just type:

```python
python main.py
```

This will write the paper, section by section, save the .tex file and compile the code.