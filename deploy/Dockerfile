# Use an official Python image as base
FROM python:3.13-slim

# Set environment variables to avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal system dependencies (TeX and heavy fonts moved to denario-plus)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      git \
      curl \
      ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Install the project into `/app`
WORKDIR $HOME/app

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
# Copy all the app code to the docker
COPY --chown=user . $HOME/app

RUN pip uninstall -y langgraph || true

# Select DenarioApp source (fork/branch/tag/commit)
ARG DENARIO_REPO=https://github.com/AstroPilot-AI/DenarioApp.git
ARG DENARIO_REF=

# Install DenarioApp (prefer local repo if present; otherwise clone)
RUN if [ -d "DenarioApp" ] && [ -f "DenarioApp/pyproject.toml" ]; then \
      echo "Installing local DenarioApp from workspace"; \
      pip install DenarioApp/.; \
    else \
      echo "Cloning DenarioApp from $DENARIO_REPO into /tmp"; \
      rm -rf /tmp/DenarioApp && \
      git clone "$DENARIO_REPO" /tmp/DenarioApp && \
      if [ -n "$DENARIO_REF" ]; then \
        echo "Checking out DenarioApp ref: $DENARIO_REF" && \
        cd /tmp/DenarioApp && git fetch --all && git checkout "$DENARIO_REF" && cd - >/dev/null; \
      fi && \
      pip install /tmp/DenarioApp/.; \
    fi

# Optionally override the installed 'denario' Python package from a fork
# Example: --build-arg DENARIO_PKG_REPO=https://github.com/yourname/denario.git --build-arg DENARIO_PKG_REF=my-branch
ARG DENARIO_PKG_REPO=
ARG DENARIO_PKG_REF=
RUN if [ -n "$DENARIO_PKG_REPO" ]; then \
      echo "Installing custom denario package from: $DENARIO_PKG_REPO @ ${DENARIO_PKG_REF:-<default>}"; \
      if [ -n "$DENARIO_PKG_REF" ]; then \
        python -m pip install -U "git+${DENARIO_PKG_REPO}@${DENARIO_PKG_REF}#egg=denario"; \
      else \
        python -m pip install -U "git+${DENARIO_PKG_REPO}#egg=denario"; \
      fi; \
    fi

# Install local denario package from workspace (overrides PyPI version).
# This ensures UI<->package compatibility and allows local fixes.
RUN if [ -d "Denario" ]; then \
      echo "Installing local denario package from workspace"; \
      pip install -U ./Denario; \
    fi

# Install proxy/runtime dependencies
RUN pip install \
    fastapi \
    "uvicorn[standard]" \
    httpx \
    aiolimiter \
    tiktoken \
    cachetools

# This informs Docker that the container will listen on a given port at runtime.
EXPOSE 7860 8080

# Ensure entrypoint is executable
RUN chmod +x ./start.sh

# Command to run the app
# Default PORT to 7860 if unset so healthcheck does not fail
HEALTHCHECK CMD sh -lc 'curl --fail http://localhost:${PORT:-7860}/_stcore/health'

# Route OpenAI-compatible clients through the local proxy
ENV OPENAI_BASE_URL=http://localhost:8080/v1 \
    OPENAI_API_BASE=http://localhost:8080/v1 \
    PROXY_HOST=0.0.0.0 \
    PROXY_PORT=8080 \
    RPM_BUDGET=60 \
    TPM_BUDGET=80000 \
    MAX_CONCURRENCY=4 \
    CACHE_TTL_SECONDS=60

CMD ["./start.sh"]
