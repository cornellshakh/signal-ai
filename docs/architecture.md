# Proposed Architecture

This diagram illustrates the clean separation between the core application and the `signalbot` adapter.

```mermaid
graph TD
    subgraph Core Application (signal_ai)
        A[Your Application Logic]
    end

    subgraph Adapter Layer
        B(SignalBot)
        subgraph API Clients
            C[GroupsClient]
            D[MessagesClient]
            E[...]
        end
    end

    subgraph External Service
        F[signal-cli-rest-api]
    end

    A -->|Uses| B
    B -->|Delegates to| C
    B -->|Delegates to| D
    B -->|Delegates to| E
    C -->|Handles all communication| F
    D -->|Handles all communication| F
    E -->|Handles all communication| F
```

## Components

### SignalBot

The `SignalBot` class is the main entry point for interacting with the Signal service. It provides a high-level interface for sending and receiving messages, managing groups, and other core functionalities. It also manages the underlying API clients and handles the connection to the `signal-cli-rest-api` service.

### API Clients

The API clients are responsible for communicating with the `signal-cli-rest-api` service. Each client is responsible for a specific set of endpoints (e.g., `GroupsClient` for group-related endpoints, `MessagesClient` for message-related endpoints). This modular design makes the codebase easier to maintain and extend.
