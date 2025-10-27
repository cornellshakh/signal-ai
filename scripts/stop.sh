#!/bin/bash
set -euo pipefail

# Script to stop all services defined in docker-compose.yml.

# --- Main ---
echo "Message: Stopping all services..."
docker compose down
echo "Message: All services have been stopped."
