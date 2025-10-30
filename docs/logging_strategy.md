# Logging Strategy

This document outlines the standardized logging strategy for this Python application. The goal is to create a robust, production-ready, and permanent solution for logging that is consistent, structured, and easy to use.

## Philosophy

The logging philosophy is centered around three core principles:

1.  **Structured Logging**: All log entries must be structured as key-value pairs. This makes them machine-readable and easy to parse, query, and analyze.
2.  **Centralized Configuration**: The logging configuration is centralized in the `src/signal_ai/core/logging.py` module. This ensures that all logs are formatted consistently and that the logging behavior can be changed in one place.
3.  **Asynchronous and Performant**: The logging system is designed to be asynchronous and performant, so that it does not block the application's main thread.

## Implementation

The logging system is implemented using the `structlog` library. `structlog` is a powerful and flexible logging library that supports structured logging, context management, and a wide range of processors and renderers.

### Configuration

The logging configuration is defined in the `configure_logging` function in `src/signal_ai/core/logging.py`. The configuration is controlled by two environment variables:

- `LOG_LEVEL`: The minimum log level to output. Defaults to `INFO`.
- `LOG_RENDERER`: The log renderer to use. Can be `console` for human-readable, colorized output, or `json` for machine-readable output. Defaults to `console`.

### Correlation IDs

Every incoming request or message is assigned a unique `correlation_id`. This ID is automatically included in every log entry generated during the lifecycle of that request. This makes it easy to trace the flow of a request through the system and to correlate log entries from different services.

The correlation ID is managed by the `@with_correlation_id` decorator, which is defined in `src/signal_ai/core/decorators.py`. This decorator should be applied to the entry point of any request or message handler.

### Usage

To log a message, you should use the `structlog.get_logger()` function to get a logger instance. You can then use the `info`, `warning`, `error`, and `debug` methods to log messages.

**Good Example:**

```python
import structlog

log = structlog.get_logger()

log.info("user.login.success", user_id=123, username="testuser")
```

**Bad Example:**

```python
import logging

# Do not use the standard logging library directly.
logging.info("User logged in successfully: %s", "testuser")

# Do not use f-strings for log messages.
log.info(f"User {user_id} logged in successfully")
```

## Linting

To enforce the use of `structlog` and to prevent the use of the standard `logging` library, a linting rule has been added to the `pyproject.toml` file. This rule will cause the linter to fail if it detects any new imports of the `logging` library.
