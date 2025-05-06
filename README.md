# AstroPilot

AstroPilot is a multiagent system designed to automatize scientific research

## Installation

### Install from PyPI

NOT AVAILABLE YET

To install Astropilot, just run

```bash
pip install astropilot
```

### Install from source

#### Pip

You will need python 3.12 installed.

Create a virtual environment

```bash
python3 -m venv astrop_env
```

Activate the virtual environment

```bash
source astrop_env/bin/activate
```

And install the project
```bash
pip install -e .
```

You can also use the `installer.sh` script, which does the above code for you.

```bash
chmod +x installer.sh
source installer.sh
```

To delete the virtual environment, do:

```bash
./installer.sh clean
```

#### uv

You can also install the project using [uv](https://docs.astral.sh/uv/), just running:

```bash
uv sync
```

which will create the virtual environment and install the dependencies and project. Activate the virtual environment with

```bash
source .venv/bin/activate
```
