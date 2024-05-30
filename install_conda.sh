#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Path to your Miniconda installation
CONDA_PATH="$SCRIPT_DIR/miniconda"

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

# Remove the existing environment if it exists
conda remove --name crewai --all -y

# Create a new environment
conda create -n crewai python=3.11 -y

# Ensure the environment is activated and install the necessary packages
conda run -n crewai conda install -y packaging
conda run -n crewai pip install -r requirements.txt

# Create the data folder if it doesn't exist
DATA_DIR="$SCRIPT_DIR/data"
mkdir -p "$DATA_DIR"

# Check if .env file exists, if not copy .env_example to .env
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo ".env file does not exist. Copying .env_example to .env..."
    cp "$SCRIPT_DIR/.env_example" "$SCRIPT_DIR/.env"
fi

# There is no datamodel.py file to patch in this project
echo "Installation completed successfully. Do not forget to update the .env file with your credentials. Then run run_conda.sh to start the app"