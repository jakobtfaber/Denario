# Running Denario in a clean environment

Denario needs Python 3.12+ and specific dependency versions (e.g. `openai` 1.x for LangChain). If you use the same conda env as other tools (e.g. casa6), you can hit conflicts.

## Option 1: Dedicated conda env (recommended)

Creates an isolated env with only Denario’s dependencies:

```bash
conda create -n denario python=3.12 -y
conda activate denario
pip install "denario[app]"
denario run
```

Use this env only for Denario so `openai` and other versions stay correct.

## Option 2: venv from conda’s Python (what went wrong)

If you run:

```bash
conda activate casa6
python -m venv .venv-denario
source .venv-denario/bin/activate
pip install "denario[app]"
```

the venv’s `python` is a symlink to casa6’s Python, so you still use casa6’s site-packages and get the same conflicts. The prompt may show `(.venv-denario)` but `sys.prefix` stays casa6.

So: **don’t create a venv while a conda env is active** if you want an isolated env. Use a **new conda env** (Option 1) or a venv created with a **non-conda** Python 3.12 (if you have one).

## Option 3: Keep using casa6

If you’re okay with dependency warnings and only need Denario to run:

- Install the app: `pip install "denario[app]"` (or `pip install denario-app`).
- If you upgraded `openai` to 2.x, downgrade for Denario:  
  `pip install "openai>=1.99.9,<2.0.0"`

Then run: `denario run`.

## Quick reference

| Goal                         | Command |
|-----------------------------|---------|
| Clean env, run GUI          | `conda create -n denario python=3.12 -y` → `conda activate denario` → `pip install "denario[app]"` → `denario run` |
| Run in current env (casa6)  | `pip install "denario[app]"` and `openai>=1.99.9,<2.0.0` if needed → `denario run` |
