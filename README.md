# AstroPilot

AstroPilot is a multi-agent system designed to automatize scientific research in astrophysics and cosmology

## Installation

Download [installer.sh](https://github.com/AstroPilot-AI/AstroPilot/blob/bbdev/installer.sh) file

```bash
chmod +x installer.sh, then:
./installer.sh
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/gemini.json ## is this needed? maybe not...
source astrop_env/bin/activate
jupyter-lab
```
To delete, do:

```bash
./installer.sh clean
```
