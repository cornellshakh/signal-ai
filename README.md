# Signal Bot

A bot that uses the `signal-cli-rest-api` container to interact with the Signal service.

## Quick Start (Recommended)

This project is designed to be run with Docker Compose, using simple helper scripts to manage the application.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Step 1: Clone and Configure

First, clone the repository and set up your environment configuration.

```bash
git clone https://github.com/cornellshakh/signal-ai.git
cd signal-ai
cp .env.example .env
```

Next, you **must** edit the `.env` file and add the phone number of the Signal account you will be using for the bot.

```plaintext
# .env
PHONE_NUMBER=+1234567890
```

### Step 2: Link to Signal

You only need to do this once. This script will start the Signal service, allow you to scan a QR code to link your device, and then shut down.

```bash
./scripts/link.sh
```

This will prompt you to open a URL in your browser (e.g., `http://127.0.0.1:8080/v1/qrcodelink...`). Scan the QR code with the Signal app on your phone. Once it's linked, you can stop the script by pressing `Ctrl+C` in the terminal.

### Step 3: Run the Bot

Now you can build and start the bot and the Signal API service.

```bash
./scripts/start.sh
```

This command will start all services in the background. You can now send commands to your bot's phone number via Signal.

## Available Commands

The bot supports the following commands:

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

## Managing the Bot

A collection of scripts are available in the `scripts/` directory to manage the application lifecycle.

- `./scripts/start.sh`: Builds and starts the bot and all related services.
- `./scripts/stop.sh`: Stops all running services.
- `./scripts/restart.sh`: A convenient way to stop and then immediately start the services again.
- `./scripts/logs.sh`: Tails the logs from all running services. Use `Ctrl+C` to exit.
- `./scripts/status.sh`: Checks the current status of the Docker containers.
- `./scripts/link.sh`: The one-time setup script to link your bot to a Signal account.

<details>
<summary><h3>Advanced: Running with a Local Python Environment</h3></summary>

While Docker is the recommended method, you can also run the bot in a local Python virtual environment. This is useful for development or if you cannot use Docker for the bot itself.

**Note:** This method still requires Docker to run the `signal-cli-rest-api` service.

1.  **Setup Virtual Environment:**
    Run the setup script to create a virtual environment and install dependencies.

    ```bash
    ./scripts/setup.sh
    ```

2.  **Link to Signal:**
    The linking process is the same. Use the script, which will handle the Docker container for you.

    ```bash
    ./scripts/link.sh
    ```

3.  **Run the Services:**
First, start the Signal API service using the script:
`bash
    ./scripts/start.sh
    `
Then, in a separate terminal, activate the virtual environment and run the Python bot:
`bash
    poetry run python src/bot.py
    `
</details>

## Troubleshooting

- **Check the logs:** The first step is always to check the logs using `./scripts/logs.sh`.
- **Verify `.env`:** Ensure the `PHONE_NUMBER` is set correctly in your `.env` file.
- **Re-link:** If you have issues with your connection to Signal, you can try running `./scripts/link.sh` again.
