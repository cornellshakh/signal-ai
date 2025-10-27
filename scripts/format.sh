#!/bin/bash
set -euo pipefail

echo "🚀 Applying auto-fixes and formatting..."

echo " lint: Running ruff to auto-fix linting issues..."
poetry run ruff check . --fix

echo " format: Formatting code with ruff..."
poetry run ruff format .

echo "✅ Formatting and auto-fixing complete!"
