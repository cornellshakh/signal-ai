# Signal Bot

[![CI](https://github.com/cornellshakh/signal-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/cornellshakh/signal-ai/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Signal bot that uses the `signal-cli-rest-api` for messaging. It is extensible, allowing for custom commands.

## Features

- **Easy Setup:** Managed with simple helper scripts.
- **Extensible:** Add new commands by creating Python files.
- **Dockerized:** Runs with Docker Compose.
- **Code Quality:** Enforced with `ruff` and `mypy`.

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Configure

Clone the repository and create your `.env` file:

```bash
git clone https://github.com/cornellshakh/signal-ai.git
cd signal-ai
cp .env.example .env
```

Edit `.env` and add your Signal phone number:

```plaintext
# .env
PHONE_NUMBER=+1234567890
```

### 2. Link to Signal

Run the linking script once to connect to your Signal account. This will start the service and generate a QR code.

```bash
./scripts/link.sh
```

Scan the QR code with your Signal app. Once linked, stop the script with `Ctrl+C`.

### 3. Run the Bot

Build and start the bot and all services:

```bash
./scripts/start.sh
```

The bot will now be running in the background.

## Usage

The bot responds to the following commands:

- `ping`: Responds with "Pong!".
- `reply`: Replies to the previous message.
- `attachment`: Sends an attachment.
- `typing`: Simulates typing.
- `triggered`: Responds to a specific trigger.
- `regex_triggered`: Responds to a regex trigger.
- `edit`: Edits the previous message.
- `delete`: Deletes the previous message.
- `receive_delete`: Receives a delete message.
- `styles`: Demonstrates text styles.

## Management Scripts

- `./scripts/start.sh`: Build and start all services.
- `./scripts/stop.sh`: Stop all services.
- `./scripts/restart.sh`: Restart all services.
- `./scripts/logs.sh`: View logs from all services.
- `./scripts/status.sh`: Check the status of Docker containers.
- `./scripts/link.sh`: Link your bot to a Signal account.
- `./scripts/setup.sh`: Set up a local Python development environment (without Docker).

## Local Development (Without Docker)

For developers who prefer to work without Docker, a local setup script is provided.

1.  **Set up the Environment**:

    Run the setup script to create a Python virtual environment and install the required dependencies.

    ```bash
    ./scripts/setup.sh
    ```

2.  **Configure**:

    Follow the same configuration steps as the Docker setup by creating and editing your `.env` file.

3.  **Run the Bot**:

    Activate the virtual environment and run the bot directly:

    ```bash
    source .venv/bin/activate
    python -m src.signal_ai.bot
    ```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Code Quality

- `./scripts/check.sh`: Run all linting, formatting, and type checks.
- `./scripts/format.sh`: Auto-format the code.

## Troubleshooting

- **Check logs:** `./scripts/logs.sh`.
- **Verify `.env`:** Ensure `PHONE_NUMBER` is correct.
- **Re-link:** Run `./scripts/link.sh` again if needed.

## Documentation

- [Development Philosophy](docs/development_philosophy.md)
- [Bot Interaction Flow](docs/bot_interaction_flow.md)
