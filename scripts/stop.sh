#!/bin/bash
set -euo pipefail

# Script to stop the signal-cli-rest-api container.

# --- Configuration ---
CONTAINER_NAME="signal-cli-rest-api"

# --- Main ---
echo "Stopping ${CONTAINER_NAME}..."

if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    docker stop "${CONTAINER_NAME}"
    echo "Container stopped."
else
    echo "Container is not running."
fi

if [ "$(docker ps -aq -f status=exited -f name=${CONTAINER_NAME})" ]; then
    echo "Removing stopped container."
    docker rm "${CONTAINER_NAME}"
fi
