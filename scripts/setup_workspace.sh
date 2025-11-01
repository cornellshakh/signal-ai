#!/bin/bash
# This script automates the setup of the development environment.

# This script is designed to be run from the 'signal-ai' directory.

# 1. Move signalbot directory if it exists
if [ -d "vendor/signalbot" ]; then
    echo "Moving signalbot to a side-by-side directory..."
    mv vendor/signalbot ../signalbot
else
    echo "signalbot directory already moved."
fi

# 2. Install dependencies
echo "Installing dependencies with Poetry..."
poetry install

echo ""
echo "Setup complete!"
echo "IMPORTANT: Close this folder and open the '../signal-ai.code-workspace' file in VSCode to begin."