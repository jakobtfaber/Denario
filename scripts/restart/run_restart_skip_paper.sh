#!/usr/bin/env bash
# Wrapper to run restart_denario_gpt5_reasoning.py but skip paper generation
export SKIP_PAPER=1
export OPENAI_API_KEY=${OPENAI_API_KEY:-sk-test-placeholder}

# Navigate to project root and run the script
cd "$(dirname "$0")/../.."
python -u scripts/restart/restart_denario_gpt5_reasoning.py
