# Bot Implementation Plan

This document outlines the technical implementation plan for the Signal AI bot. It is structured to directly correspond with the features and flows defined in `docs/bot_interaction_flow.md`.

## Development Approach

**It is critical that this plan is executed in a step-by-step, iterative manner.** Each task or feature should be implemented and thoroughly tested to ensure it is working correctly before moving on to the next. This approach minimizes complexity, makes debugging easier, and ensures a stable foundation for subsequent features. Do not proceed to a new task until the previous one is complete and verified.

## Completed Foundational Work

The following core components are already in place and considered complete:

- **Project Scaffolding:** The `src/signal_ai/` directory structure, `pyproject.toml` dependencies, and main `bot.py` entry point are functional.
- **Basic Bot:** The bot successfully initializes `signalbot`, connects to the Signal service, and can receive messages.
- **Docker Integration:** The `Dockerfile` and `docker-compose.yml` are configured, and the bot can be managed via the `./scripts/` shell scripts.

## 1. Rebuild Core Infrastructure (From Scratch)

_Goal: Implement the core components based on the new specification, removing the outdated legacy code._

- [x] **Implement New Persistence Layer:**
  - Create `src/signal_ai/core/persistence.py`.
  - Implement the `PersistenceManager` class using TinyDB with `CachingMiddleware`.
  - Implement `load_context` and `save_context` methods.
  - Add the hourly backup logic.
- [x] **Implement New Context Model:**
  - Create `src/signal_ai/core/context.py`.
  - Define the `Context` data class using Pydantic, ensuring it includes fields for `config`, `history`, `todos`, etc., as required by the specification.
- [x] **Implement New Message Handler:**
  - Create `src/signal_ai/core/message_handler.py`.
  - Implement the **Interaction Logic Gate** as the first step in the handler, checking for chat type and `mode` before any other processing.
  - Implement the **Message Parsing and Routing** logic to direct `!` commands and conversational messages appropriately.

## 2. Implement Core Features

_Goal: Build out the essential, non-AI user-facing features._

- [x] **Reply Strategy:**
  - Implement the logic for mention-replies in group chats vs. standard replies in direct chats.
- [x] **`!help` command:**
  - Create `src/signal_ai/commands/help.py` and implement the help message.
- [x] **`!config` command:**
  - Create `src/signal_ai/commands/config.py` and implement the `view` and `set mode` sub-commands.
- [x] **`!todo` command:**
  - Create `src/signal_ai/commands/todo.py` and implement `add`, `list`, and `done`.
- [x] **`!remind` command:**
  - Create `src/signal_ai/commands/remind.py` and implement scheduling logic.
- [x] **Onboarding Flow:**
  - Implement the welcome message for when the bot joins a group.

## 3. AI Integration

_Goal: Connect the bot to the AI backend and implement AI-powered features._

- [x] **AI Client:**
  - Create `src/signal_ai/core/ai_client.py` to handle all interactions with the Gemini API.
- [x] **AI-Powered Commands:**
  - Create `src/signal_ai/commands/search.py` for web search/URL summary.
  - Create `src/signal_ai/commands/image.py` for image generation.
- [x] **User Feedback System:**
  - Implement the three-stage feedback system (typing, `⏳`, `✅`/`❌`).
- [x] **Summarization Service:**
  - Implement the "Intelligent Summarizer" background task.
