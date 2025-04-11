#!/bin/bash
# installer.sh
# This script sets up a Python virtual environment, upgrades pip,
# and clones & installs three Git repositories using specific branches.
# It also supports a "clean" option to remove the environment and clones.

# If the first argument is "clean", remove everything and exit.
if [ "$1" == "clean" ]; then
    echo "Cleaning up Python virtual environment and repositories..."
    rm -rf astrop_env AstroPilot ag2 cmbagent
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

# Create a Python 3.12 virtual environment named 'astrop_env'
echo "Creating Python virtual environment..."
python3.12 -m venv astrop_env

# Activate the virtual environment
echo "Activating virtual environment..."
source astrop_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

### Clone and install AstroPilot ###
ASTROPILOT_REPO="https://github.com/AstroPilot-AI/AstroPilot.git"
ASTROPILOT_DIR="AstroPilot"

clone_repo "$ASTROPILOT_REPO" "$ASTROPILOT_DIR"

echo "Switching to branch 'bbdev' and installing AstroPilot..."
cd "$ASTROPILOT_DIR"
git switch bbdev

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
cd ..

### Clone and install ag2 ###
AG2_REPO="https://github.com/CMBAgents/ag2.git"
AG2_DIR="ag2"

clone_repo "$AG2_REPO" "$AG2_DIR"

echo "Switching to branch 'ag2_v0.8.4_upgrade_astrop' and installing ag2..."
cd "$AG2_DIR"
git switch ag2_v0.8.4_upgrade_astrop
pip install -e .
cd ..

### Clone and install cmbagent ###
CMBAGENT_REPO="https://github.com/CMBAgents/cmbagent.git"
CMBAGENT_DIR="cmbagent"

clone_repo "$CMBAGENT_REPO" "$CMBAGENT_DIR"

echo "Switching to branch 'astrop' and installing cmbagent..."
cd "$CMBAGENT_DIR"
git switch astrop
pip install -e .
cd ..


# Install an IPython kernel for the virtual environment
echo "Installing IPython kernel for the virtual environment..."
python -m ipykernel install --user --name astrop_env --display-name "Python (astrop_env)"

echo "Installation complete!"

