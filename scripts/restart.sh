#!/bin/bash
set -euo pipefail

# Script to rebuild and restart all services.

# --- Main ---
echo "Message: Rebuilding and restarting all services..."
docker compose up -d --build
echo "Message: All services have been restarted."
