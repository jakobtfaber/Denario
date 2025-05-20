# AstroPilot

AstroPilot is a multiagent system designed to automatize scientific research

## Installation

NOT AVAILABLE YET

To install Astropilot, just run

```bash
pip install astropilot
```

## Get started

Initialize an `AstroPilot` instance and describe the data and tools to be employed.

```python
from astropilot import AstroPilot, Journal

# Initiate AstroPilot by setting the working directory
astro_pilot = AstroPilot(project_dir="project_dir")

# Set the input text
input_text = """
Analyze the experimental data stored in /path/to/data.csv using sklearn and pandas.
This data includes time-series measurements from a particle detector.
"""
astro_pilot.set_data_description(input_text)

# Generate a research idea from the input text
astro_pilot.get_idea()

# Generate a research plan to carry out the idea
astro_pilot.get_method()

# Follow the research plan, write and execute code, make plots, and summarize the results
astro_pilot.get_results()

# Write a paper with [APS (Physical Review Journals)](https://journals.aps.org/) style
astro_pilot.get_paper(journal=Journal.APS)
```

You can also manually provide any info as a string or markdown file in an intermediate step, using the `set_idea`, `set_method` or `set_results` methods. For instance, for providing a file with the methodology developed by the user:

```python
astro_pilot.set_method(path_to_the_method_file.md)
```

## Build from source

### pip

You will need python 3.12 installed.

Create a virtual environment

```bash
python3 -m venv .venv
```

Activate the virtual environment

```bash
source .venv/bin/activate
```

And install the project
```bash
pip install -e .
```

### uv

You can also install the project using [uv](https://docs.astral.sh/uv/), just running:

```bash
uv sync
```

which will create the virtual environment and install the dependencies and project. Activate the virtual environment if needed with

```bash
source .venv/bin/activate
```
