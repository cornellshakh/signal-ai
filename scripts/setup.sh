#!/bin/bash
set -euo pipefail

# Install the project dependencies using poetry.

poetry env use python3.13
poetry install --no-root