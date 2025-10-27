# Signal Bot

A bot that uses the `signal-cli-rest-api` container to interact with the Signal service.

## Setup

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  Run the setup script to create a virtual environment and install the required dependencies:

    ```bash
    ./scripts/setup.sh
    ```

3.  Link the bot to a Signal account:

    ```bash
    ./scripts/link.sh
    ```

4.  Open <http://127.0.0.1:8080/v1/qrcodelink?device_name=local> in your browser to link your account with the `signal-cli-rest-api` server.

5.  Configure VS Code to use the project's virtual environment

6.  Copy the `.env.example` file to `.env` and rename it to `.env`. Configure the environment variables in the `.env` file:

    ```bash
    cp .env.example .env
    # Edit .env with your configuration
    ```

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
