#!/bin/bash
set -euo pipefail

# Script to check the status of the signal-cli-rest-api container.

# --- Configuration ---
CONTAINER_NAME="signal-cli-rest-api"

# --- Main ---
echo "Checking status of ${CONTAINER_NAME}..."

if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    echo "Container is running."
    docker ps -f name=${CONTAINER_NAME}
    echo ""
    echo "You can view the logs with './scripts/logs.sh'"
    echo "You can stop the container with './scripts/stop.sh'"
else
    echo "Container is not running."
    if [ "$(docker ps -aq -f status=exited -f name=${CONTAINER_NAME})" ]; then
        echo "A stopped container exists. You can start it with './scripts/start.sh'"
    fi
fi
