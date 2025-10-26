#!/bin/bash
set -euo pipefail

# Script to run linting, formatting checks, and static analysis.
# It uses 'ruff' for high-speed linting/formatting and 'mypy' for static type checking.

# --- Main ---
echo "Running comprehensive Python code checks..."

echo -e "\n--- Running ruff (linter and import sorter) ---"
# Check for any linting or import sorting issues.
poetry run ruff check .

echo -e "\n--- Running ruff (formatter check) ---"
# Check if any files need reformatting.
poetry run ruff format --check .

echo -e "\n--- Running mypy (static type checker) ---"
# Perform strict static type analysis.
poetry run mypy signalbot/ tests/ example/

echo -e "\n✅ All checks passed!"
