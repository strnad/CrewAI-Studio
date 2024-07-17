#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Path to your Miniconda installation
CONDA_PATH="$SCRIPT_DIR/miniconda"

# Function to prompt the user for yes/no response
prompt_yes_no() {
    while true; do
        read -p "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes (y) or no (n).";;
        esac
    done
}

# Check if Miniconda is already installed
if [ ! -d "$CONDA_PATH" ]; then
    # Download Miniconda installer
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh

    # Install Miniconda
    bash miniconda.sh -b -p "$CONDA_PATH"

    # Clean up installer
    rm miniconda.sh
else
    echo "Miniconda is already installed in $CONDA_PATH. Skipping installation."
fi

# Initialize Conda for this script session only
if [ -f "$CONDA_PATH/etc/profile.d/conda.sh" ]; then
    source "$CONDA_PATH/etc/profile.d/conda.sh"
else
    echo "ERROR: Miniconda installation not found at $CONDA_PATH"
    exit 1
fi

# Prompt to remove the existing environment if it exists
if conda info --envs | grep -q 'crewai'; then
    if prompt_yes_no "The Conda environment 'crewai' already exists. Do you want to reinstall it?"; then
        echo "Removing existing Conda environment..."
        conda remove --name crewai --all -y || { echo "Failed to remove existing Conda environment"; exit 1; }
    else
        echo "Installation canceled."
        exit 0
    fi
fi

# Create a new environment
conda create -n crewai python=3.11 -y || { echo "Failed to create Conda environment"; exit 1; }

# Prompt for cache usage
USE_CACHE="--no-cache"
if prompt_yes_no "Do you want to use the cache for pip installation?"; then
    USE_CACHE=""
fi

# Ensure the environment is activated and install the necessary packages
conda run -n crewai conda install -y packaging || { echo "Failed to install Conda packages"; exit 1; }
conda run -n crewai pip install -r requirements.txt $USE_CACHE || { echo "Failed to install requirements"; exit 1; }

# Agentops
echo "Do you want to install agentops? (y/n)"
read agentops
if [ "$agentops" == "y" ]; then
    echo "Installing agentops..."
    conda run -n crewai pip install agentops || { echo "Failed to install agentops"; }
fi

# Check if .env file exists, if not copy .env_example to .env
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo ".env file does not exist. Copying .env_example to .env..."
    cp "$SCRIPT_DIR/.env_example" "$SCRIPT_DIR/.env"
fi

echo "Installation completed successfully. Do not forget to update the .env file with your credentials. Then run run_conda.sh to start the app."
