#!/bin/bash
set -euo pipefail

# --- Dependency Checks ---
if ! command -v docker &> /dev/null
then
    echo "Error: docker is not installed. Please install docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null
then
    echo "Error: docker-compose is not installed. Please install docker-compose."
    exit 1
fi

# Script to run signal-cli-rest-api in normal mode for linking a new device.

# --- Configuration ---
CONFIG_DIR="$(pwd)/signal-cli-config"
SERVICE_NAME="signal-cli-rest-api"

# --- Main ---
echo "Message: Starting ${SERVICE_NAME} in 'normal' mode for linking..."
echo "Message: Config will be stored in: ${CONFIG_DIR}"

# Create config directory if it doesn't exist
mkdir -p "${CONFIG_DIR}"

# Ensure all services are stopped before linking
echo "Message: Stopping any running services..."
docker-compose down

# Start the signal service in linking mode with the port exposed
echo "Message: Running linking container. Press Ctrl+C to stop."
echo "Message: Open http://127.0.0.1:8080/v1/qrcodelink?device_name=signal-bot in your browser."
docker-compose run --rm --service-ports ${SERVICE_NAME} /entrypoint.sh normal

echo "Message: Linking process finished."
