# Signal AI: Final Architecture & Refactoring Plan

## 1. Introduction

This document presents the definitive architectural blueprint for the `signal-ai` application. After a thorough analysis of the existing codebase and a careful consideration of the project's long-term goals, this plan has been designed to eliminate all existing technical debt, establish a robust and scalable foundation, and enable the rapid development of complex features in the future. This is not a set of options, but a prescriptive guide to building a future-proof application.

## 2. The Final Architecture: A Service-Oriented Approach

The new architecture is a pure service-oriented design. This model provides the highest degree of decoupling, testability, and maintainability, ensuring that the application can evolve without being constrained by its underlying structure.

### 2.1. Architecture Diagram

```mermaid
graph TD
    subgraph Application Layer
        A[Container & Entrypoint]
    end

    subgraph Service Layer
        B[MessageHandler]
        C[ReasoningEngine]
        D[StateManager]
        E[SchedulerService]
        F[ToolingService]
    end

    subgraph Infrastructure Layer
        G[AIClient]
        H[PersistenceManager]
        I[SignalTransport]
    end

    subgraph Domain Layer
        J[AppContext]
        K[BaseTool]
        L[Configuration]
    end

    A -- "Initializes & Wires All Services" --> B & C & D & E & F & G & H & I

    B -- "Receives Messages via" --> I
    B -- "Dispatches to" --> C

    C -- "Uses" --> G
    C -- "Uses" --> F
    C -- "Uses" --> D

    D -- "Manages State via" --> H

    E -- "Manages Scheduled Tasks"

    F -- "Discovers & Manages" --> K

    style A fill:#c9f,stroke:#333,stroke-width:2px
    style B,C,D,E,F fill:#9cf,stroke:#333,stroke-width:2px
    style G,H,I fill:#f96,stroke:#333,stroke-width:2px
    style J,K,L fill:#9c9,stroke:#333,stroke-width:2px
```

### 2.2. Component Specifications

- **Application Layer:**

  - **Container & Entrypoint:** A single, well-defined entry point to the application (e.g., `main.py`) that initializes a dependency injection container (e.g., `dependency-injector`). This container will be responsible for instantiating and wiring all services, ensuring that the application is assembled in a consistent and predictable manner.

- **Service Layer:**

  - **MessageHandler:** The central nervous system of the application, responsible for receiving messages from the `SignalTransport`, creating an `AppContext`, and dispatching it to the `ReasoningEngine`.
  - **ReasoningEngine:** The brain of the AI, responsible for orchestrating the interaction between the user, the AI model, and the available tools.
  - **StateManager:** The single source of truth for all application state, including chat history, pinned messages, and to-do lists. It will be responsible for loading and saving state via the `PersistenceManager`.
  - **SchedulerService:** A dedicated service for managing all scheduled tasks (e.g., reminders).
  - **ToolingService:** A dedicated service for discovering, managing, and dispatching all tools.

- **Infrastructure Layer:**

  - **AIClient:** A client for interacting with the AI model.
  - **PersistenceManager:** A client for interacting with the database.
  - **SignalTransport:** A client for interacting with the `signal-cli-rest-api`.

- **Domain Layer:**
  - **AppContext:** A rich domain object that encapsulates all the information about the current context, including the message, chat, user, and application state.
  - **BaseTool:** A base class for all tools, with a declarative schema for defining the tool's name, description, and arguments.
  - **Configuration:** A dedicated module for managing the application's configuration, with a clear separation between static and dynamic configuration.

## 3. Step-by-Step Refactoring Plan

The refactoring process will be executed in the following order to ensure a smooth and seamless transition to the new architecture:

1.  **Implement Core Services and Dependency Injection:**

    - Create the new directory structure for the service-oriented architecture.
    - Implement the dependency injection container and the application entry point.
    - Create the core services (`MessageHandler`, `ReasoningEngine`, `StateManager`, `SchedulerService`, `ToolingService`) with their basic interfaces and dependencies.

2.  **Abstract Infrastructure Layer (Transport & Persistence):**

    - Create the `SignalTransport` service to abstract all communication with the `signal-cli-rest-api`.
    - Refactor the `PersistenceManager` to be a pure infrastructure component, with no business logic.

3.  **Refactor Commands into Decoupled Tools:**

    - Consolidate the `commands` and `tools` directories into a single `tools` directory.
    - Refactor all existing commands into self-contained, declarative tools that inherit from `BaseTool`.
    - Implement the `ToolingService` to discover and manage the new tools.

4.  **Implement State Management and Business Logic Services:**

    - Implement the `StateManager` service to centralize all state management.
    - Refactor the business logic from the old commands into the new tools and services.

5.  **Wire Up and Test the New Application:**
    - Wire up the new services in the dependency injection container.
    - Write a comprehensive suite of unit and integration tests for the new services and tools.
    - Manually test the new application to ensure that it is working as expected.

## 4. Conclusion

This refactoring plan is a significant undertaking, but it is a necessary investment in the future of the `signal-ai` application. By following this plan, we will create a robust, scalable, and maintainable system that will be a pleasure to work with for years to come.
