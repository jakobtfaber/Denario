#!/bin/bash
# installer.sh
# This script sets up a Python virtual environment, upgrades pip,
# and clones & installs three Git repositories using specific branches.
# It also supports a "clean" option to remove the environment and clones.

# If the first argument is "clean", remove everything and exit.
if [ "$1" == "clean" ]; then
    echo "Cleaning up Python virtual environment and repositories..."
    rm -rf astrop_env
    echo "Clean operation completed."
    exit 0
fi

# Exit immediately if a command exits with a non-zero status.
set -e

TARGET_BRANCH="bbdev"

# Switch this repo to the desired branch if needed
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "$TARGET_BRANCH" ]; then
    echo "Checking out $TARGET_BRANCH branch ..."
    git fetch origin "$TARGET_BRANCH"
    git checkout "$TARGET_BRANCH"
fi

# Create a Python 3 virtual environment named 'astrop_env'
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3" >&2
    exit 1
fi

echo "Creating Python virtual environment..."
python3 -m venv astrop_env


# Activate the virtual environment
echo "Activating virtual environment..."
source astrop_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

### Install AstroPilot ###

echo "Installing AstroPilot..."

# Create the .env file from environment variables
echo "Creating .env file in AstroPilot with API keys..."
cat <<EOF > .env
OPENAI_API_KEY="${OPENAI_API_KEY}"
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"
GEMINI_API_KEY="${GEMINI_API_KEY}"
GOOGLE_API_KEY="${GOOGLE_API_KEY}"
LANGCHAIN_API_KEY="${LANGCHAIN_API_KEY}"
PERPLEXITY_API_KEY="${PERPLEXITY_API_KEY}"
EOF
echo ".env file created."

pip install -e .

# Install an IPython kernel for the virtual environment
echo "Installing IPython kernel for the virtual environment..."
python -m ipykernel install --user --name astrop_env --display-name "Python (astrop_env)"

echo "Installation complete!"

