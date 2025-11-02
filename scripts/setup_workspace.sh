#!/bin/bash
# This script automates the setup of the development environment.

# This script is designed to be run from the 'signal-ai' directory.

# 1. Install dependencies
echo "Installing dependencies with Poetry..."
poetry install

echo ""
echo "Setup complete!"
echo "IMPORTANT: Close this folder and open the '../signal.code-workspace' file in VSCode to begin."