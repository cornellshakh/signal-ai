# Persistence Configuration Audit

This document outlines the findings of a comprehensive audit of the persistence-related configurations in the `signal-ai` application.

## Summary of Findings

The overall persistence strategy is sound and correctly configured within the Docker Compose setup. However, two potential issues were identified:

1.  **Missing `SIGNAL_SERVICE` Environment Variable:** The `.env.example` file was missing the `SIGNAL_SERVICE` variable, which is critical for the bot to connect to the `signal-cli-rest-api`. This has been rectified.
2.  **Missing Host Volume Directories:** The `signal-cli-config` and `signal-ai-data` directories, which are used as host mounts for the `signal-cli-rest-api` and `bot` services respectively, do not exist in the project's root. Docker will create these directories automatically, but they will be owned by the `root` user, which could lead to permission issues.

## Recommendations

1.  **Create Host Directories:** It is recommended to create the `signal-cli-config` and `signal-ai-data` directories in the project's root before starting the application. This will ensure they have the correct ownership and permissions.
2.  **Update `.env` File:** Ensure that the `.env` file (not just the example) is updated with the correct `SIGNAL_SERVICE` value (`signal-cli-rest-api:8080`).

## Detailed Analysis

### `docker-compose.yml`

- **`signal-cli-rest-api`:** Correctly mounts `./signal-cli-config` to `/home/.local/share/signal-cli`.
- **`redis`:** Uses a named volume `redis-data`.
- **`postgres`:** Uses a named volume `postgres-data` and correctly sets database credentials.
- **`bot`:** Correctly mounts `./signal-ai-data` to `/root/.signal-ai` and loads the `.env` file.

### Application Configuration (`src/signal_ai/core/config.py`)

- The application correctly loads configuration from environment variables.
- The hardcoded hostnames for `postgres` and `redis` match the service names in `docker-compose.yml`.
- The `SIGNAL_SERVICE` variable is used to construct the connection URLs for the `signal-cli-rest-api`.
