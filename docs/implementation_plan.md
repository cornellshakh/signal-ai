# Bot Implementation Plan

This document outlines the step-by-step process for implementing the Signal AI bot as defined in `docs/bot_interaction_flow.md`. It has been updated to reflect the existing codebase.

## Phase 1: The Core Foundation (Completed)

_Goal: Set up the basic project structure and a minimal, running bot that can receive and log messages._

- [x] **Project Scaffolding:**
  - [x] The `src/signal_ai/` directory structure is in place.
  - [x] The main `src/signal_ai/bot.py` file exists and is functional.
- [x] **Basic Bot:**
  - [x] `bot.py` successfully initializes `signalbot` and connects to the Signal service.
- [x] **Docker Integration:**
  - [x] The `Dockerfile` is set up to build and run the bot.
  - [x] The bot can be started with `./scripts/start.sh`.

## Phase 2: The Persistence Layer

_Goal: Implement the TinyDB-based persistence manager to give the bot a memory._

- [ ] **Dependencies:**
  - [ ] Add `tinydb` and `pydantic` to the project's dependencies in `pyproject.toml`.
- [ ] **Data Model:**
  - [ ] Create `src/signal_ai/core/context.py` and define the `Context` data class using Pydantic.
- [ ] **Persistence Manager:**
  - [ ] Create `src/signal_ai/core/persistence.py`.
  - [ ] Implement the `PersistenceManager` class using TinyDB with `CachingMiddleware`.
  - [ ] Implement `load_context(chat_id)` and `save_context(chat_id, context)` methods.
  - [ ] Add the hourly backup logic.

## Phase 3: Command Framework Refinement

_Goal: Adapt the existing command system to support the unified `@BotName` interaction model and our new features._

- [ ] **Unified Interaction Model:**
  - [ ] Modify the core bot logic to handle all commands and conversations through a single entry point when the bot is mentioned. The existing `signalbot` registration might need a custom wrapper or a new base command class to achieve this.
- [ ] **Argument Parsing:**
  - [ ] Implement a robust parser that can handle sub-commands (e.g., `config set mode all`) and arguments.
- [ ] **Cleanup Existing Commands:**
  - [ ] Review the commands currently registered from the `example/` directory in `bot.py`.
  - [ ] Remove the ones that are not part of our final design (e.g., `PingCommand`, `ReplyCommand`, etc.).

## Phase 4: Feature Implementation

_Goal: Build out the logic for each of the user-facing commands, following the new aesthetic and functional design._

- [ ] **`help` command:** Refactor `src/signal_ai/commands/help.py` to implement the full, aesthetically pleasing help message.
- [ ] **`config` command:** Create `src/signal_ai/commands/config.py` and implement the `view` and `set` sub-commands, using the `PersistenceManager`.
- [ ] **`todo` command:** Create `src/signal_ai/commands/todo.py` and implement the `add`, `list`, and `done` sub-commands.
- [ ] **`remind` command:** Create `src/signal_ai/commands/remind.py` and implement the scheduling logic (likely using `apscheduler`).

## Phase 5: AI Integration

_Goal: Connect the bot to the Gemini API and implement the AI-powered features._

- [ ] **AI Client:**
  - [ ] Create `src/signal_ai/core/ai_client.py` to handle all interactions with the Gemini API.
- [ ] **Natural Conversation:**
  - [ ] In the main message handler, if a message is a mention but not a recognized command, treat it as a conversational prompt.
  - [ ] Implement the flow: get context from `PersistenceManager`, send it to `AIClient`, and get a response.
- [ ] **AI-Powered Commands:**
  - [ ] Refactor `src/signal_ai/commands/search_web.py` to align with the new design.
  - [ ] Create `src/signal_ai/commands/image.py` for the image generation command.
- [ ] **Summarization Service:**
  - [ ] Implement the background task that periodically summarizes the `conversation_log` for each chat.
