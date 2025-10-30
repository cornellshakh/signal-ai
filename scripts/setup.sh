#!/usr/bin/env bash
set -eu

# This script sets up the development environment using Poetry.

# --- Dependency Checks ---
if ! command -v python3 &> /dev/null
then
    echo "Error: python3 is not installed. Please install Python 3."
    exit 1
fi

if ! command -v poetry &> /dev/null
then
    echo "Error: poetry is not installed. Please install poetry."
    exit 1
fi

# --- Main ---
echo "Message: Creating virtual environment..."

# Create the virtual environment
python3 -m venv .venv

# Configure poetry to use the virtualenv in the project's root
poetry config virtualenvs.in-project true --local

echo "Message: Installing dependencies..."

# Install dependencies using the virtual environment's python
poetry run pip install --upgrade pip
poetry install

echo "Message: Setup complete. To activate the virtual environment, run 'poetry shell'."