# Implementation Plan: Centralized Prompt Management System

**Goal:** To refactor the codebase to use a centralized, configuration-based prompt management system. This will decouple prompts from the application logic, enabling easier management, iteration, and contribution by prompt engineers.

---

### Phase 1: Setup and Dependencies

- **Objective:** Prepare the environment by adding the necessary libraries and creating the core files for the new system.
- **Actions:**
  1.  **Add Dependencies:** Add `PyYAML` and `Jinja2` to the project's `pyproject.toml` file to handle YAML parsing and prompt templating.
  2.  **Create `prompts.yaml`:** Create a new file at `src/signal_ai/prompts.yaml`. This file will store all the prompts for the application.
  3.  **Create `prompt_manager.py`:** Create a new file at `src/signal_ai/core/prompt_manager.py`. This will house the `PromptManager` class.

---

### Phase 2: Building the `PromptManager`

- **Objective:** Implement the `PromptManager` class, which will be responsible for loading, managing, and rendering prompts.
- **File to Create:** `src/signal_ai/core/prompt_manager.py`
- **Implementation Details:**
  - The class will be initialized with the path to the `prompts.yaml` file.
  - It will use `PyYAML` to load and parse the YAML file into a Python dictionary upon initialization.
  - It will have a `get(key, **kwargs)` method that:
    - Retrieves the raw prompt string from the dictionary using its `key`.
    - Uses a `jinja2.Template` to render the prompt, passing in any provided keyword arguments as template variables.
    - Returns the final, formatted prompt string.

---

### Phase 3: Populating the Prompts

- **Objective:** Move all existing hardcoded prompts into the new `prompts.yaml` file.
- **File to Create:** `src/signal_ai/prompts.yaml`
- **Initial Content:**

  ```yaml
  system_instruction: |
    You are an AI assistant. Your primary goal is to provide clear, concise, and helpful answers.

    **Core Rules:**
    1. **Use Simple Language:** Your top priority is to be understood. Avoid all jargon, academic language, and overly complex phrasing. Explain things in the simplest possible terms.
    2. **Be Thorough:** Provide comprehensive answers. You can use multiple paragraphs if it helps to structure the information clearly.
    3. **Answer the Question Directly:** Get straight to the point. Do not ramble or provide unnecessary background information.
    4. **Handle Greetings Simply:** If the user says hello or asks how you are, respond with a simple, direct, and friendly greeting. Do not analyze the question.
    5. **Use Supported Formatting Only:** You can use `**bold**`, `*italic*`, `~strikethrough~`, `||spoilers||`, and `` `monospaced text` ``.

  generate_group_name: "Generate a short, descriptive group name (max 5 words) for the following prompt: {{ prompt }}"
  ```

---

### Phase 4: Integration into the Application

- **Objective:** Refactor the existing codebase to use the new `PromptManager` instead of hardcoded strings.
- **Files to Modify:**
  - `src/signal_ai/bot.py`
  - `src/signal_ai/core/ai_client.py`
  - `src/signal_ai/commands/context/new.py`
- **Implementation Steps:**
  1.  **In `bot.py`:**
      - Import `PromptManager`.
      - Initialize an instance of `PromptManager` in the `SignalAIBot`'s `__init__` method and store it as `self.prompt_manager`.
  2.  **In `ai_client.py`:**
      - Modify the `AIClient`'s `__init__` method to accept the `prompt_manager` instance.
      - Replace the hardcoded `system_instruction` string with a call to `prompt_manager.get("system_instruction")`.
  3.  **In `new.py`:**
      - Access the bot's `prompt_manager` instance.
      - Replace the hardcoded group name generation prompt with a call to `bot.prompt_manager.get("generate_group_name", prompt=prompt)`.

---

### Phase 5: Testing

- **Objective:** Ensure the refactored system works correctly and that prompts are being loaded and rendered as expected.
- **Test Plan:**
  - Run the `!new <prompt>` command to verify the end-to-end flow.
  - Check that the group is created with a correctly generated name.
  - Confirm that the initial AI response is generated correctly, using the new system prompt.
  - Temporarily modify a prompt in `prompts.yaml` and restart the bot to ensure changes are loaded without requiring a code change.
