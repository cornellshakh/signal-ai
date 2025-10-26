#!/bin/bash
set -euo pipefail

# --- Dependency Checks ---
if ! command -v docker &> /dev/null
then
    echo "Error: docker is not installed. Please install docker."
    exit 1
fi

if ! command -v docker compose &> /dev/null
then
    echo "Error: docker compose is not installed. Please install docker compose."
    exit 1
fi

# Script to run signal-cli-rest-api in normal mode for linking a new device using Docker Compose.

# --- Configuration ---
CONFIG_DIR="$(pwd)/signal-cli-config"

# --- Main ---
echo "Message: Starting signal-cli-rest-api in 'normal' mode for linking..."
echo "Message: Config will be stored in: ${CONFIG_DIR}"

# Create config directory if it doesn't exist
mkdir -p "${CONFIG_DIR}"

# Stop and remove existing container if it exists
docker compose down

# Run the container in normal mode
docker compose run --rm signal-cli-rest-api MODE=normal

echo "Message: Container stopped."
