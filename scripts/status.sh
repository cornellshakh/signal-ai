#!/bin/bash
set -euo pipefail

# Script to check the status of all services.

# --- Main ---
echo "Message: Checking status of all services..."
docker compose ps
