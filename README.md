# Signal Bot

A bot that uses the `signal-cli-rest-api` container to interact with the Signal service.

## Setup

This project can be run in two ways: using local Python with helper scripts, or fully containerized with Docker Compose.

### Option 1: Local Setup (with Scripts)

This method uses a local Python virtual environment for the bot and a Docker container for the Signal API.

1.  **Clone the repository and configure your environment:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    cp .env.example .env
    # Edit .env with your phone number
    ```

2.  **Create Virtual Environment:**
    Run the setup script to create a virtual environment and install the required dependencies:

    ```bash
    ./scripts/setup.sh
    ```

3.  **Link to Signal:**
    Follow the instructions in the **"Linking to Signal"** section below. You will use the `./scripts/link.sh` command.

4.  **Run the Bot:**
    Once linked, start the Signal API service in the correct mode:
    ```bash
    ./scripts/start.sh
    ```
    Then, in a separate terminal, run the Python bot:
    ```bash
    poetry run python src/bot.py
    ```

### Option 2: Docker Compose Setup

This method runs both the bot and the Signal API in Docker containers. It's the recommended method for simplicity and portability.

1.  **Clone the repository and configure your environment:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    cp .env.example .env
    # Edit .env with your phone number
    ```

2.  **Build and Start Services:**

    ```bash
    docker-compose up --build
    ```

    This command will build and start both the `signal-cli-rest-api` and the `bot` services.

3.  **Link to Signal:**
    With the services running, follow the instructions in the **"Linking to Signal"** section below.

## Linking to Signal

To use the bot, you must first link it to a Signal account. This is a one-time process.

### For Local Setup

1.  Run the `link.sh` script. This will start the Signal API in `normal` mode.
    ```bash
    ./scripts/link.sh
    ```
2.  Open <http://127.0.0.1:8080/v1/qrcodelink?device_name=local> in your browser and scan the QR code with your Signal app.
3.  Once linked, stop the script with `Ctrl+C`.

### For Docker Compose Setup

1.  In a separate terminal (while your `docker-compose up` command is **not** running), start the linking process:
    ```bash
    docker-compose run --rm --service-ports signal-cli-rest-api
    ```
    This command starts a temporary container in `normal` mode and exposes the necessary port.
2.  Open <http://127.0.0.1:8080/v1/qrcodelink?device_name=local> in your browser and scan the QR code.
3.  Once linked, stop the container with `Ctrl+C`. You can now start your services normally with `docker-compose up`.

## Usage Instructions

### Prerequisites

- A linked Signal device. See the [Setup](#setup) for details.
- The `signal-cli-rest-api` container running in json-rpc mode.

### Running the bot

1.  Start the `signal-cli-rest-api` container:

    ```bash
    ./scripts/start.sh
    ```

2.  Send commands to the bot via Signal.

### Available Commands

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

## Configuration

The bot can be configured using environment variables. See `.env` file.

## Scripts

The `scripts/` directory contains the following scripts:

- `check.sh`: Checks the status of the bot.
- `link.sh`: Links the bot to a Signal account.
- `logs.sh`: Shows the logs of the bot.
- `setup.sh`: Sets up the bot, creating a virtual environment and installing dependencies.
- `start.sh`: Starts the bot.
- `status.sh`: Shows the status of the bot.
- `stop.sh`: Stops the bot.

## Troubleshooting Tips

- Check the bot's logs for errors.
- Verify that the `signal-cli-rest-api` container is running correctly.
- Ensure that the environment variables are configured correctly.
