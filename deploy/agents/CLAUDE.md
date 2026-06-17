# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Docker containerization project for the Denario GUI application. The repository builds Docker images that run the Denario Streamlit app along with an in-container OpenAI-compatible proxy middleware that enforces RPM/TPM budgets, retries, and caching.

## Architecture

- **App Source**: The actual Denario app code is NOT stored in this repo. It's cloned at build time from `AstroPilot-AI/DenarioApp` (configurable via build args)
- **Proxy Middleware**: Custom FastAPI proxy at `proxy/` that sits between the app and external API providers, providing rate limiting, token management, and model aliasing
- **Two Image Variants**: 
  - Base (`Dockerfile`): Slim Python image with core dependencies
  - Plus (`Dockerfile.addtools`): Extends base with full LaTeX stack for Paper/PDF workflows

## Common Development Commands

### Building Images
```bash
# Base image
docker build -t denario .

# Plus image with TeX/PDF tools  
docker build -f Dockerfile.addtools -t denario-plus .

# Build against custom fork/branch
docker build -t denario --build-arg DENARIO_REPO=https://github.com/yourname/DenarioApp.git --build-arg DENARIO_REF=my-branch .
```

### Running Containers
```bash
# Base image
docker run --rm -p 7860:7860 -p 8080:8080 --env-file .env -e PORT=7860 denario

# With persistent exports
docker run --rm -p 7860:7860 -p 8080:8080 --env-file .env -v $(pwd)/exports:/home/user/app/exports denario
```

### Docker Compose
```bash
# Base service
docker compose up -d denario

# Plus service on alternate ports
docker compose -f compose.yml -f compose.plus.override.yml up -d denario-plus
```

### Health Checks
```bash
# App health
curl http://localhost:7860/_stcore/health

# Proxy health  
curl http://localhost:8080/healthz
```

### Direct Development (without Docker)
```bash
git clone https://github.com/AstroPilot-AI/DenarioApp.git
pip install -e DenarioApp
streamlit run DenarioApp/src/denario_app/app.py
```

## Configuration

### Environment Variables (.env file required)
- API Keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `PPLX_API_KEY`
- Proxy settings: `RPM_BUDGET`, `TPM_BUDGET`, `MAX_CONCURRENCY`, `CACHE_TTL_SECONDS`
- Model overrides: `FORCE_MODEL`, `MODEL_ALIASES`, `MODEL_ALIAS_PREFIXES`

### Build Arguments
- `DENARIO_REPO`: Repository URL for DenarioApp source (default: AstroPilot-AI/DenarioApp)
- `DENARIO_REF`: Branch/tag/commit to checkout
- `DENARIO_PKG_REPO`/`DENARIO_PKG_REF`: Override the installed `denario` Python package

## Key Components

### Proxy Module (`proxy/`)
- `app.py`: FastAPI application with rate limiting and model aliasing
- `config.py`: Configuration management from environment variables
- `cache.py`: Simple TTL cache for API responses
- `tokenizer.py`: Token counting utilities

### Entry Point
- `start.sh`: Launches proxy in background, then starts Streamlit app

## Development Notes

- This repo has no unit tests - validate via container smoke tests and manual UI checks
- The user account in containers is `user` (ID 1000), not root
- App runs on port 7860 (Streamlit), proxy on port 8080
- Use `.env.example` as template for configuration
- Model overrides work through the proxy without modifying app code