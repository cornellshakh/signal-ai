# Implementation Plan: The Hybrid Momentum Model (Refined)

**Core Principle:** Deliver tangible, user-facing value at every phase while incrementally building the robust, agentic foundation. This plan uses the "Strangler Fig" pattern to introduce new logic alongside the old, gradually replacing the original architecture.

---

### Phase 1: The Tool-Use Bridge

- **Objective:** Enable AI-driven tool use in the shortest possible time to deliver a high-impact "wow" feature and maintain project momentum.

* [x] **Modify `AIClient`:** Add a new method `generate_response_with_tools(history)` to `src/signal_ai/core/ai_client.py`.
* [x] **Rename `dispatcher.py`:** Rename `src/signal_ai/core/dispatcher.py` to `src/signal_ai/core/tool_manager.py`.
* [x] **Upgrade `CommandDispatcher`:** Rename the class `CommandDispatcher` to `ToolManager` within the new `tool_manager.py` file.
* [x] **Update Imports:** Change the relevant import in `src/signal_ai/core/message_handler.py` to use `ToolManager`.
* [x] **Define Tool Schemas with Pydantic:** Augment the `ToolManager` to generate JSON schemas from Pydantic models defined in each tool file.
* [x] **Create `tools` Directory:** Create a new directory at `src/signal_ai/tools/`.
* [x] **Implement `web_search` Tool:** Add a `web_search.py` file in the `tools` directory with a functional search tool using a Pydantic model for its arguments.
* [x] **Write Unit Tests:** Create `tests/core/test_tool_manager.py` and write tests to validate the new functionality in isolation.

---

### Phase 2: The Memory Façade

- **Objective:** Introduce a tangible improvement to the bot's memory without the complexity of a full vector database implementation.

* [x] **Create `memory_manager.py`:** Create the file `src/signal_ai/core/memory_manager.py`.
* [x] **Define `MemoryManager` Interface:** In the new file, define the `MemoryManager` class with a clean interface (`add_memory`, `retrieve_relevant_memories`).
* [x] **Create `ShortTermMemoryBackend`:** Implement a `ShortTermMemoryBackend` within `memory_manager.py` that wraps the existing `PersistenceManager` logic.
* [x] **Implement Keyword Search:** Add a simple, keyword-based search method to the `ShortTermMemoryBackend` for context retrieval.
* [x] **Integrate `MemoryManager`:** Initialize the `MemoryManager` in `bot.py` and pass it to the `AIClient`.
* [x] **Write Unit Tests:** Create `tests/core/test_memory_manager.py` and write tests to validate the new functionality in isolation.

---

### Phase 3: The Organic Reasoning Loop

- **Objective:** Introduce the full agentic reasoning loop, driven by the practical need to handle a complex, multi-step tool.

* [ ] **Design Multi-Step Tool:** Plan and design a tool that requires multiple interactions.
* [ ] **Implement Multi-Step Tool:** Create the file and class structure for the new tool in the `tools` directory.
* [ ] **Create `ReasoningEngine`:** Create a new file `src/signal_ai/core/reasoning_engine.py` and implement a `ReasoningEngine` class to manage the thought-action-observation cycle.
* [ ] **Integrate `ReasoningEngine`:** The `ReasoningEngine` will use the `AIClient` for LLM calls and the `ToolManager` for tool execution.
* [ ] **Ensure Coexistence:** Verify that the `ReasoningEngine` is only triggered for complex tool use, while simple conversations still use the original, direct response path.
* [ ] **Write Unit Tests:** Create `tests/core/test_reasoning_engine.py` and write tests to validate the new functionality in isolation.
