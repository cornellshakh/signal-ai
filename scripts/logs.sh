#!/bin/bash
set -euo pipefail

# Script to view the logs of the signal-cli-rest-api container.

# --- Configuration ---
CONTAINER_NAME="signal-cli-rest-api"

# --- Main ---
echo "Showing logs for ${CONTAINER_NAME}..."
echo "Press Ctrl+C to exit."

if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    docker logs -f "${CONTAINER_NAME}"
else
    echo "Container is not running."
    # Check if there are logs from a stopped container
    if [ "$(docker ps -aq -f status=exited -f name=${CONTAINER_NAME})" ]; then
        echo "Showing logs from the last run:"
        docker logs "${CONTAINER_NAME}"
    fi
fi
