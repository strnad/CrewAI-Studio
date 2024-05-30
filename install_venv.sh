#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR
# Create a virtual environment
python -m venv venv || { echo "Failed to create venv"; exit 1; }

# Activate the virtual environment
source venv/bin/activate || { echo "Failed to activate venv"; exit 1; }

# Install requirements
pip install -r requirements.txt --no-cache|| { echo "Failed to install requirements"; exit 1; }

# Check if .env file exists, if not copy .env_example to .env
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo ".env file does not exist. Copying .env_example to .env..."
    cp "$SCRIPT_DIR/.env_example" "$SCRIPT_DIR/.env"
fi

echo "Installation completed successfully. Do not forget to update the .env file with your credentials. Then run run_venv.sh to start the app""
