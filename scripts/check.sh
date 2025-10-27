#!/bin/bash
#
# This script runs a series of checks to ensure code quality before committing.
# It includes linting, formatting checks, and static type analysis.
# It is designed to be run from the root of the repository.

set -euo pipefail

echo "🚀 Starting code quality checks..."

echo " lint: Running ruff linter..."
poetry run ruff check src/signal_ai/

echo " format: Checking code formatting with ruff..."
poetry run ruff format --check src/signal_ai/

echo " types: Running mypy for static type checking..."
poetry run mypy src/signal_ai/

echo "✅ All checks passed successfully!"
