> **LEGACY DOCUMENT:** This plan is outdated and has been superseded by the new modular architecture. It is kept for historical purposes only.

---

# Adapter Enhancement Plan: A Future-Proof Foundation

## 1. The Goal

This document outlines the definitive plan to refactor our application and its forked `signalbot` library to create a truly "future-proof" foundation. The goal is to establish a clean, robust, and complete adapter layer, ensuring our core application logic is 100% decoupled from the underlying Signal platform.

## 2. The Core Principle: A Fortified Adapter

Our Hexagonal Architecture requires that our core application be completely isolated from external systems. The forked `signalbot` library is our "adapter" for the Signal platform. To achieve a truly future-proof design, this adapter must be the _only_ component that interacts directly with the `signal-cli-rest-api`.

Currently, components like our `GroupManager` bypass this adapter and make direct HTTP calls. This violates our architecture and creates technical debt. This plan will rectify that.

## 3. The Plan: A Three-Phase Approach

### Phase 1: `signal-cli-rest-api` Audit

Before we write any code, we must have a complete understanding of the API surface we need to support.

- **Action:** Perform a comprehensive audit of the `signal-cli-rest-api` documentation (or source code, if necessary).
- **Action:** Create a definitive list of all API endpoints and their corresponding functionalities (e.g., `GET /v1/groups`, `POST /v1/groups/{group_id}/members`, etc.).
- **Action:** Identify all endpoints that are currently used by our application _outside_ of the `signalbot` library (e.g., in `GroupManager`).

### Phase 2: `signalbot` Fork Implementation Roadmap

With a complete API map, we will enhance our `signalbot` fork to be a complete and high-level client.

- **Action:** For each identified API endpoint, create a corresponding high-level method in the appropriate class within the `signalbot` library (e.g., `signalbot.SignalBot.create_group(...)`, `signalbot.SignalBot.add_group_members(...)`).
- **Action:** These methods will encapsulate all the underlying HTTP requests, error handling, and data parsing. The goal is to create a simple, intuitive, and robust Python API for interacting with the Signal service.
- **Action:** All new methods must be fully type-hinted and documented.

### Phase 3: Core Application Refactoring

Once the `signalbot` adapter is complete, we will refactor our core application to use it exclusively.

- **Action:** Delete the `src/signal_ai/core/group_manager.py` file entirely.
- **Action:** Refactor any component that currently uses the `GroupManager` to instead call the new, high-level methods directly on the main `bot` instance (e.g., `self._bot.create_group(...)`).
- **Action:** Perform a codebase-wide search for any other instances of direct API calls or `signalbot` library "leaks" and refactor them to use the fortified adapter.

## 4. The Outcome

Upon completion of this plan, our foundation will be truly complete and future-proof. The `signalbot` fork will be a robust and comprehensive adapter, and our core application logic will be pure, platform-agnostic, and free of any implementation details of the underlying Signal service. This will allow us to focus exclusively on feature development with the highest degree of confidence in our architecture.
