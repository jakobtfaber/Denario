---
title: Denario
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: gpl
short_description: GUI for Denario
---

# Denario — Dockerized GUI

This repo builds Docker images that run the Denario app (Streamlit) plus an in-container OpenAI-compatible proxy that enforces RPM/TPM budgets, retries, and caching.

## Quick Start
- `cd /data/denario-docker`
- `cp -n .env.example .env 2>/dev/null || true`

# Edit `.env` and add your OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, etc

- Build (base, slim): `docker build -t denario .`
- Run (base): `docker run --rm -p 7870:7860 -p 8090:8080 --env-file .env -e PORT=7860 denario`
- Open UI: `http://localhost:7870`
- Proxy health: `http://localhost:8090/healthz` (the app routes to `http://localhost:8090/v1`).

Env file `.env` (not committed):

- `OPENAI_API_KEY=...` `ANTHROPIC_API_KEY=...` `GOOGLE_API_KEY=...` `PPLX_API_KEY=...`
- Optional tuning: `RPM_BUDGET=60` `TPM_BUDGET=80000` `MAX_CONCURRENCY=4` `CACHE_TTL_SECONDS=60`
- Model selection (proxy):
  - `FORCE_MODEL` to override any requested model (e.g., `FORCE_MODEL=gpt-4o-mini`).
  - `MODEL_ALIASES` to remap models without changing the app. Accepts JSON (e.g., `{"gpt-4.1":"gpt-4o-mini"}`) or comma pairs (e.g., `gpt-4.1=gpt-4o-mini,gpt-4o=gpt-4o-mini`).
  - `MODEL_ALIAS_PREFIXES` to remap entire model families using prefix matching (e.g., `gpt-4=gpt-5-mini,o3=gpt-5-mini`). Longest-prefix wins.

Exports (persistent):

- `mkdir -p exports`
- `docker run ... -v $(pwd)/exports:/home/user/app/exports denario`

## Base vs Plus images

- **Base (`denario`)**: Streamlit UI + proxy. Ports: UI `7870->7860`, proxy `8090->8080`.
- **Plus (`denario-plus`)**: Adds TeX/PDF toolchain (texlive, fonts, Ghostscript, Poppler). Default compose override maps UI to `7871->7860`. Paper/PDF features require this image.

## denario-plus (TeX + PDF tools)

- Build: `docker build -f Dockerfile.addtools -t denario-plus .`
- Run: `docker run --rm -p 7871:7860 -p 8091:8080 --env-file .env denario-plus`
- Includes: full LaTeX stack (texlive) + fonts + Ghostscript + Poppler.
- Verify tools: `docker run --rm --entrypoint bash denario-plus -lc "xelatex --version && gs --version && pdfinfo -v && pdftotext -v"`

## Docker Compose

- Start base: `docker compose up -d denario` (UI `http://localhost:7870`, proxy `http://localhost:8090`)
- Start plus on alternate ports: `docker compose -f compose.yml -f compose.plus.override.yml up -d denario-plus` (UI `http://localhost:7871`, proxy `http://localhost:8091`)
- Note: Paper/PDF features require `denario-plus` (base image is slim).

### Build Against Your DenarioApp Fork

- Docker build args:
  - `DENARIO_REPO` (default: AstroPilot-AI/DenarioApp)
  - `DENARIO_REF` (optional branch/tag/commit)
- Examples:
  - `docker build -t denario --build-arg DENARIO_REPO=https://github.com/yourname/DenarioApp.git --build-arg DENARIO_REF=my-branch .`
  - `docker compose build` with compose args (see commented `build.args` in `compose.yml`).
  - Then run as usual.

Note: For private forks, prefer SSH or a PAT in your URL. Be mindful that embedding tokens in build args may end up in image metadata; consider using BuildKit secrets if needed.

### Override the `denario` Python Package (advanced)

- Prefer proxy aliases first. Only override the package when you need the model to appear in the Python registry/UI.
- If you must, fork the `denario` package, add the model to its registry, then build this image against your fork using `DENARIO_PKG_REPO`/`DENARIO_PKG_REF` build args. Rebuild base (`denario`) before `denario-plus`.

## Troubleshooting

- Port conflict: use compose override or map different host ports (e.g., `-p 7861:7860 -p 8081:8080`).
- Health: `curl http://localhost:7870/_stcore/health` and `curl http://localhost:8090/healthz`.
- Base image is slim (no TeX). Use `denario-plus` for Paper/PDF workflows.

## Proxy Model Overrides

- Swap models globally without modifying DenarioApp using the proxy.
  - `.env` examples:
    - Remap families by prefix: `MODEL_ALIAS_PREFIXES=gpt-4=gpt-4o-mini,o3=gpt-4o-mini`
    - Accept experimental names by mapping them to known upstream models: `MODEL_ALIAS_PREFIXES=gpt-5=gpt-4o-mini` (so `gpt-5-mini` → `gpt-4o-mini`).
    - Force a single model: `FORCE_MODEL=gpt-4o-mini`.
- After updating `.env`, restart the container (and rebuild if build args changed) so the proxy picks up changes.

See `.env.example` for ready-to-copy configurations.

See `AGENTS.md` for contributor guidelines and details on the proxy middleware.

## Proxy smoke tests

- Quick verification script: `bash ./proxy_smoke_tests.sh [BASE_URL] [TOKEN_A] [TOKEN_B]`
- Defaults: BASE_URL `http://localhost:8090`. Provide two different tokens to validate cache namespacing.
- Checks performed:
  - `/healthz` responds with budgets, cache stats, and concurrency snapshot
  - CORS headers via OPTIONS preflight with `Origin: http://localhost:7870`
  - Cache behavior: HIT with same token, MISS with different token

### CORS

- Enable CORS on the proxy via env and restart:
  - `PROXY_ENABLE_CORS=1`
  - `PROXY_CORS_ORIGINS=http://localhost:7870` (comma-separated list; `*` allowed)
- The proxy includes an `OPTIONS /healthz` preflight handler; when enabled, responses include `access-control-allow-origin`.

## Testing

- Use the dedicated conda env:
  - `conda run -n denario-stable bash -lc "PYTHONPATH=. python -m pytest -q tests/test_healthz.py"`

### Proxy startup

- The proxy starts via the FastAPI factory:
  - `uvicorn --factory proxy.app:create_app`
- This ensures middleware (e.g., CORS) is attached at boot and that preflight requests succeed.

### Minimal .env template (copy/paste)

```dotenv
# Upstream API keys (fill any you use)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
PPLX_API_KEY=

# Proxy budgets and concurrency
RPM_BUDGET=60
TPM_BUDGET=80000
MAX_CONCURRENCY=4
CACHE_TTL_SECONDS=60
CACHE_MAXSIZE=1024

# Proxy base URL (OpenAI-compatible)
UPSTREAM_OPENAI_BASE_URL=https://api.openai.com/v1

# Optional model overrides/aliases
# FORCE_MODEL=gpt-4o-mini
# MODEL_ALIASES={"gpt-4.1":"gpt-4o-mini"}
# MODEL_ALIAS_PREFIXES=gpt-4=gpt-4o-mini,o3=gpt-4o-mini

# App/UI port (container)
PORT=7860
```

## Upstream Denario references
- **Original GUI application (DenarioApp)**: [AstroPilot-AI/DenarioApp](https://github.com/AstroPilot-AI/DenarioApp)
- **Core Python package (`denario`)**: [PyPI: denario](https://pypi.org/project/denario/)

This repository containerizes and extends the original Denario application with an in-container OpenAI-compatible proxy (model aliases/overrides, caching, RPM/TPM governance, retries) and an optional TeX/PDF toolchain image (`denario-plus`). Where behavior differs from upstream, the changes are documented in this README and `AUDIT.md`.
