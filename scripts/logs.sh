#!/bin/bash
set -euo pipefail

# Script to view the logs of a service. Defaults to the 'bot' service.
# Usage: ./scripts/logs.sh [service_name]
# Example: ./scripts/logs.sh signal-cli-rest-api

# --- Configuration ---
SERVICE_NAME=${1:-bot}

# --- Main ---
echo "Message: Showing logs for '${SERVICE_NAME}' service..."
echo "Message: Press Ctrl+C to exit."

docker compose logs -f "${SERVICE_NAME}"
