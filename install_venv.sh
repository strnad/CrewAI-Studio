#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR" || exit

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

# Check if venv exists
if [ -d "venv" ]; then
    if prompt_yes_no "The virtual environment 'venv' already exists. Do you want to reinstall it?"; then
        echo "Removing existing virtual environment..."
        rm -rf venv || { echo "Failed to remove existing venv"; exit 1; }
    else
        echo "Installation canceled."
        exit 0
    fi
fi

# Create a virtual environment
python -m venv venv || { echo "Failed to create venv"; exit 1; }

# Activate the virtual environment
source venv/bin/activate || { echo "Failed to activate venv"; exit 1; }

# Prompt for cache usage
USE_CACHE="--no-cache"
if prompt_yes_no "Do you want to use the cache for pip installation?"; then
    USE_CACHE=""
fi

# Install requirements
pip install -r requirements.txt $USE_CACHE || { echo "Failed to install requirements"; exit 1; }

#agentops
echo "Do you want to install agentops? (y/n)"
read agentops
if [ "$agentops" == "y" ]; then
    echo "Installing agentops..."
    pip install agentops || { echo "Failed to install agentops"; }
fi
# Check if .env file exists, if not copy .env_example to .env
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo ".env file does not exist. Copying .env_example to .env..."
    cp "$SCRIPT_DIR/.env_example" "$SCRIPT_DIR/.env"
fi

echo "Installation completed successfully. Do not forget to update the .env file with your credentials. Then run run_venv.sh to start the app."
