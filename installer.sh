#!/bin/bash
# installer.sh
# This script sets up a Python virtual environment, upgrades pip,
# and clones & installs three Git repositories using specific branches.
# It also supports a "clean" option to remove the environment and clones.

# If the first argument is "clean", remove everything and exit.
if [ "$1" == "clean" ]; then
    echo "Cleaning up Python virtual environment and repositories..."
    rm -rf astrop_env ag2 cmbagent
    echo "Clean operation completed."
    exit 0
fi

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to clone a repo if it doesn't exist
clone_repo() {
  local repo_url=$1
  local repo_dir=$2
  if [ ! -d "$repo_dir" ]; then
    echo "Cloning $repo_url into $repo_dir ..."
    git clone "$repo_url"
  else
    echo "Directory $repo_dir already exists. Skipping clone."
  fi
}

# Create a Python 3 virtual environment named 'astrop_env'
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

### Clone and install ag2 ###

AG2_REPO="https://github.com/CMBAgents/ag2.git"
AG2_DIR="ag2"
AG2_BRANCH="ag2_v0.8.4_upgrade_astrop"

echo "Cloning and installing ag2 from branch '$AG2_BRANCH'..."

GIT_LFS_SKIP_SMUDGE=1 pip install git+$AG2_REPO@$AG2_BRANCH

# Install an IPython kernel for the virtual environment
echo "Installing IPython kernel for the virtual environment..."
python -m ipykernel install --user --name astrop_env --display-name "Python (astrop_env)"

echo "Installation complete!"

