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

## Phase 2: The Persistence Layer (Completed)

_Goal: Implement the TinyDB-based persistence manager to give the bot a memory._

- [x] **Dependencies:**
  - [x] Add `tinydb` and `pydantic` to the project's dependencies in `pyproject.toml`.
- [x] **Data Model:**
  - [x] Create `src/signal_ai/core/context.py` and define the `Context` data class using Pydantic.
- [x] **Persistence Manager:**
  - [x] Create `src/signal_ai/core/persistence.py`.
  - [x] Implement the `PersistenceManager` class using TinyDB with `CachingMiddleware`.
  - [x] Implement `load_context(chat_id)` and `save_context(chat_id, context)` methods.
  - [x] Add the hourly backup logic.

## Phase 3: Command Framework Refinement (Completed)

_Goal: Adapt the existing command system to support the unified `@BotName` interaction model and our new features._

- [x] **Unified Interaction Model:**
  - [x] Modify the core bot logic to handle all commands and conversations through a single entry point when the bot is mentioned. The existing `signalbot` registration might need a custom wrapper or a new base command class to achieve this.
- [x] **Argument Parsing:**
  - [x] Implement a robust parser that can handle sub-commands (e.g., `config set mode all`) and arguments.
- [x] **Cleanup Existing Commands:**
  - [x] Review the commands currently registered from the `example/` directory in `bot.py`.
  - [x] Remove the ones that are not part of our final design (e.g., `PingCommand`, `ReplyCommand`, etc.).

## Phase 4: Feature Implementation

_Goal: Build out the logic for each of the user-facing commands, following the design in `docs/bot_interaction_flow.md`._

- [x] **`help` command:** Refactor `src/signal_ai/commands/help.py` to implement the full, aesthetically pleasing help message as defined in the interaction flow.
- [x] **`config` command:** Create `src/signal_ai/commands/config.py` and implement the `view` and `set` sub-commands, following the interaction flow.
- [x] **`todo` command:** Create `src/signal_ai/commands/todo.py` and implement the `add`, `list`, and `done` sub-commands, following the interaction flow.
- [x] **`remind` command:** Create `src/signal_ai/commands/remind.py` and implement the scheduling logic, following the interaction flow.
- [x] **User Feedback System:** Implement the three-stage feedback system (typing indicator, `⏳`, `✅`/`❌` reactions) as described in the interaction flow.
- [x] **Onboarding Flow:** Implement the welcome message for when the bot is first added to a group.

## Phase 5: AI Integration

_Goal: Connect the bot to the Gemini API and implement the AI-powered features as defined in `docs/bot_interaction_flow.md`._

- [ ] **AI Client:**
  - [ ] Create `src/signal_ai/core/ai_client.py` to handle all interactions with the Gemini API.
- [ ] **Natural Conversation:**
  - [ ] In the main message handler, if a message is not a recognized command, treat it as a conversational prompt.
  - [ ] Implement the "Simple Log" model: send the conversation history to the `AIClient` and get a response.
- [ ] **AI-Powered Commands:**
  - [ ] Create `src/signal_ai/commands/search.py` for the web search/URL summary command.
  - [ ] Create `src/signal_ai/commands/image.py` for the image generation command.
- [ ] **Summarization Service:**
  - [ ] Implement the "Intelligent Summarizer" background task that periodically summarizes the `conversation_log` for each chat to optimize token usage.
