# Repository Guidelines

## Project Structure & Module Organization
- Root: `Dockerfile`, `.gitattributes` (Git LFS), `README.md`.
- App code is not stored here. It is cloned at build time into the image as `DenarioApp/` and launched via Streamlit.
- Purpose: a minimal containerized entrypoint for the Denario GUI (for local Docker or Hugging Face Spaces).

## Images: Base vs Plus
- Base image (denario): slim. No TeX or heavy fonts to keep build size low.
- Plus image (denario-plus): adds TeX (texlive), fonts, Ghostscript and Poppler for Paper/PDF workflows.
- Build order matters: build `denario` first, then `denario-plus` (which is `FROM denario`).

## Build, Test, and Development Commands
- Build image: `docker build -t denario .` — builds the Python 3.13 image and clones `AstroPilot-AI/DenarioApp` inside.
- Run locally: `docker run --rm -p 7860:7860 -e PORT=7860 denario` — starts Streamlit on `http://localhost:7860`.
- Smoke test: `curl http://localhost:7860/_stcore/health` — returns 200 when healthy.
- Dev (direct app): `git clone https://github.com/AstroPilot-AI/DenarioApp.git && pip install -e DenarioApp && streamlit run DenarioApp/src/denario_app/app.py`.

### Build Pins (compose.yml)
- `DENARIO_REPO`/`DENARIO_REF`: which DenarioApp repo/ref to clone (default upstream on `master`).
- `DENARIO_PKG_REPO`/`DENARIO_PKG_REF`: which `denario` Python package fork/ref to install (e.g., a fork adding new models).
- Recommended: pin to a branch or commit SHA for reproducibility.

### Ports and Overrides
- Base: UI `7860`, proxy `8080`.
- Plus override (`compose.plus.override.yml`): maps to `7861` and `8081` to avoid conflicts when both run.

### PYTHONPATH
- Compose sets `PYTHONPATH=/home/user/app:$PYTHONPATH` to ensure runtime shims (e.g., `sitecustomize.py`) are importable from the repo root inside the container.

## Coding Style & Naming Conventions
- Dockerfile: keep layers minimal, use `&&` chains, and clean apt caches. Avoid root; use the existing `user` account.
- Dependencies: prefer pinning versions where possible; explain non‑pinned choices in PRs.
- Files: lowercase with hyphens; env vars in `UPPER_SNAKE_CASE` (e.g., `PORT`).

## Testing Guidelines
- This repo has no unit tests; validate via container smoke tests and manual UI checks.
- When modifying the Dockerfile, verify: image builds cleanly, app starts, healthcheck passes, and the UI loads.
- If adding scripts, name tests `test_*.py` and run with `pytest` (not currently included).

### Proxy Tests (curl)
- Health: `curl http://localhost:8080/healthz` (or `8081` for plus). Confirms budgets, upstream, and alias settings.
- Minimal chat: `curl -sS -X POST http://localhost:8080/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"gpt-4o","messages":[{"role":"user","content":"Say hi"}],"max_tokens":5}'`.
- Structured output: add `response_format` as needed; watch for upstream 4xx.
- Common pitfalls and fixes (proxy auto-handles):
  - `max_tokens` unsupported → normalized to `max_completion_tokens`.
  - `temperature: null` → removed.
  - `gpt-5*` explicit `temperature != 1` → removed (only default allowed).
  - `logprobs`/`top_logprobs` on disallowed models → removed.

## Commit & Pull Request Guidelines
- Commits: short, imperative summaries (e.g., “Add deploy flag”, “Rewrite CMD command”). Group related changes.
- PRs: include purpose, notable Dockerfile changes, steps to verify locally, and screenshots or logs when relevant. Link related issues.

## Security & Configuration Tips
- Do not commit secrets. Use runtime env vars or mount `.env` (a placeholder is created in the image).
- Large files: use Git LFS per `.gitattributes`.
- Network: build requires GitHub access to clone `DenarioApp`. Consider pinning to a tag/commit for reproducibility.

## Proxy Middleware
- Purpose: OpenAI‑compatible forward proxy enforcing RPM/TPM budgets, concurrency, retries, and caching.
- Env:
  - `PROXY_HOST`, `PROXY_PORT` bind settings.
  - `RPM_BUDGET`, `TPM_BUDGET`, `MAX_CONCURRENCY`, `CACHE_TTL_SECONDS`.
  - `UPSTREAM_OPENAI_BASE_URL` and (optional) `OPENAI_API_KEY` forwarder.
  - Model remapping: `FORCE_MODEL`, `MODEL_ALIASES` (exact), `MODEL_ALIAS_PREFIXES` (prefix; longest match wins).
- Normalization/Sanitization (request):
  - Convert `max_tokens` → `max_completion_tokens`.
  - Drop `temperature: null`; for `gpt-5*`, drop non‑default `temperature`.
  - Drop `logprobs`/`top_logprobs` where disallowed.
- Health: `/healthz` shows budgets, upstream_base_url, model alias settings.
- Streaming: extended timeout; returns 504 JSON on upstream timeouts instead of crashing.

## Disk Usage Tips
- Large TeX stack moved to `denario-plus`. Use `denario` for faster base rebuilds.
- Reclaim space:
  - `docker system prune -af` and `docker builder prune -af`.
  - Increase Docker Desktop disk image size if routinely building large images.

## Repo Hygiene
- `.dockerignore` excludes local clones `Denario/` and `DenarioApp/` from build context.
- `.gitignore` excludes them from VCS. Keep inner repos separate (outer: container; inner: Python package fork).
