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

# Script to start all services in detached mode using Docker Compose.

# --- Main ---
echo "Message: Building and starting all services..."

# Start the services in detached mode and build if necessary
docker-compose up -d --build

echo "Message: Services started. Use './scripts/logs.sh' to see the logs."
