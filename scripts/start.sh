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

# Script to start the signal-cli-rest-api container in json-rpc mode using Docker Compose.

# --- Configuration ---
CONFIG_DIR="$(pwd)/signal-cli-config"

# --- Main ---
echo "Message: Starting signal-cli-rest-api in 'json-rpc' mode..."

# Create config directory if it doesn't exist
mkdir -p "${CONFIG_DIR}"

# Start the container in detached mode
docker compose up -d

echo "Message: Container started. Use './scripts/logs.sh' to see the logs."
