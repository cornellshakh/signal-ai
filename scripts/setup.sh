:!/usr/bin/env bash

set -eu

# This script sets up the development environment.

# Create a virtual environment.
if [ ! -d .venv ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
  echo "Virtual environment created."
fi

# Activate the virtual environment.
source .venv/bin/activate


echo "Activating virtual environment..."
source .venv/bin/activate
echo "Virtual environment activated."

# Install dependencies from requirements.txt.
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo "Dependencies installed."


# Display the contents of the virtual environment's bin directory.
echo "Listing contents of .venv/bin directory..."
ls -l .venv/bin

echo "Setup complete!"