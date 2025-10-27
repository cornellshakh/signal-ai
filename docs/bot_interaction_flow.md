# Bot Interaction and Command Flow

This document outlines the user-bot interaction flow, command handling, and the strategy for managing conversational context. The system is designed around a single, unified interaction pattern: mentioning the bot by name.

## Visual Flowchart

The following diagram illustrates the lifecycle of a user's message, from input to the bot's final, aesthetically formatted response.

```mermaid
graph TD
    subgraph Legend
        direction LR
        L1[Input] --> L2[Process] --> L3[Output]
    end

    subgraph User Input
        A[User sends message]
    end

    subgraph Bot Core Logic
        B(SignalBot)
        A --> B
        B --> C{Parse: Is Bot Mentioned?}
    end

    subgraph Command Handling
        C -- Yes --> D{Route Command or Conversation}
        D -- 'help' --> Help[Generate & Send Help Text]
        D -- 'config' --> Config[Get/Set Chat Configuration]
        D -- 'todo' --> Todo[Manage To-Do List]
        D -- 'remind' --> Remind[Set a Reminder]
        D -- 'search' --> Search[AIClient: Web Search/URL Summary]
        D -- 'image' --> Image[AIClient: Generate Image]
        D -- Other (Natural Language) --> Conv[AIClient: Natural Conversation]
    end

    subgraph AI & Output
        subgraph AIClient
            direction LR
            Search --> AIC
            Image --> AIC
            Conv --> AIC
        end
        AIC(AI Model) --> Res{Generate Text/Image}
        Res --> Format[Format Response Aesthetically]
    end

    subgraph Final Output
      Format --> Out(Send Final Message/Image)
      Help --> Out
      Config --> Out
      Todo --> Out
      Remind --> Out
    end

    subgraph User Feedback System
        B -- On Receive --> T1[Show Typing Indicator]
        AIC -- On AI Call --> T2[React with ⏳]
        Out -- On Success/Fail --> T3[Replace ⏳ with ✅ or ❌]
    end

    Out --> A
```

## Core Logic & Context Management

The bot's intelligence is rooted in a simple yet robust context management system: the **"Simple Log" model**.

For each chat, the bot maintains a `Context` object containing:

- **`history`**: A rolling log of the last 20 messages.
- **`config`**: The specific settings for that chat (`model`, `mode`, `prompt`).

When a user mentions the bot, the entire `history` log is sent to the AI, ensuring the bot has the immediate short-term context of the conversation. This approach is simple, predictable, and effective for most interactions.

## Command Reference

All interactions begin by mentioning the bot (e.g., `@BotName`). The bot's responses are designed to be visually aesthetic, using Markdown and emojis to create a clean and readable Text UI.

- **`help`**

  - **Purpose:** Displays a help message with a list of available commands.
  - **Example:**
    > **User:** `@BotName help`
    >
    > **Bot:**
    >
    > > 🤖 **Signal AI Assistant**
    > >
    > > > I'm a bot designed to assist you. Interact with me by mentioning my name (`@BotName`) followed by a command or a question.
    > >
    > > **Available Commands:**
    > >
    > > ```
    > > ┌
    > > ├─ 📋 todo      - Manage a shared to-do list.
    > > ├─ ⏰ remind    - Set a reminder.
    > > ├─ ⚙️ config    - Configure my settings for this chat.
    > > ├─ 🔎 search    - Search the web or summarize a URL.
    > > └─ 🖼️ image     - Generate an image from a prompt.
    > > ```
    > >
    > > _For more details, type `@BotName help <command>`._

- **`config`**

  - **Purpose:** Manages the bot's settings for the current chat.
  - **Example:**
    > **User:** `@BotName config view`
    >
    > **Bot:**
    >
    > > ⚙️ **Chat Configuration**
    > >
    > > > ```
    > > > model:  gemini-1.5-pro
    > > > mode:   mention
    > > > prompt: You are a helpful assistant.
    > > > ```
    > > >
    > > > _Use `@BotName config set <key> <value>` to make changes._

- **`todo`**

  - **Purpose:** Manages a simple to-do list within the chat.
  - **Example:**
    > **User:** `@BotName todo add Finalize the Q3 report`
    >
    > **Bot:**
    >
    > > ✅ **Todo added:** `1. Finalize the Q3 report`

- **`remind`**

  - **Purpose:** Sets a reminder for a user or the group.
  - **Example:**
    > **User:** `@BotName remind me in 10 minutes to check the build`
    >
    > **Bot:**
    >
    > > ✅ **Got it.** I will remind you at `6:13 PM` to "check the build".

## Onboarding Flow

When first added to a group, the bot will introduce itself with a welcome message to ensure users understand its purpose and how to interact with it.

> **Bot (upon joining a group):**
>
> > Hello everyone. I am a helpful assistant.
> >
> > You can interact with me by mentioning my name, `@BotName`.
> >
> > To see a full list of what I can do, just type:
> > `@BotName help`

## User Feedback System

A three-stage feedback system provides real-time updates for any AI-related task:

1.  A **typing indicator** is shown when a message is received.
2.  A `⏳` reaction is added to the message when the AI call is initiated.
3.  The `⏳` reaction is replaced with `✅` on success or `❌` on failure, accompanied by a descriptive error message if applicable.

## Technical Implementation Blueprint

This section outlines the technical architecture for the bot, including the persistence layer and code structure, designed to be robust, scalable, and aligned with our development philosophy.

### 1. Persistence Layer: TinyDB

To ensure data is managed safely and efficiently, the bot will use the **TinyDB** library. This provides a lightweight, file-based database that is simple to manage while preventing common issues like data corruption from concurrent writes.

- **Database File:** All state information (configurations, to-do lists, summaries) for all chats will be stored in a single file: `data/db.json`.
- **Performance:** To ensure high performance under load, the database will be initialized with TinyDB's `CachingMiddleware`. This keeps a hot cache of the data in memory for near-instantaneous reads and handles writing to disk intelligently.
- **Data Integrity:** The `PersistenceManager` will implement a simple hourly backup of the `db.json` file to mitigate the risk of data loss in the event of a critical failure.

### 2. Application Structure

The codebase will be organized for modularity and clarity, following the "Single Responsibility" principle. This makes the bot easy to maintain and extend.

**Proposed Directory Structure:**

```
src/signal_ai/
├── bot.py             # Main application entry point.
|
├── core/
│   ├── context.py     # Defines the `Context` data model.
│   └── persistence.py # The `PersistenceManager` class, handling all DB logic.
|
└── commands/
    ├── help.py          # Logic for the `help` command.
    ├── config.py        # Logic for the `config` command.
    ├── todo.py          # Logic for the `todo` command.
    └── remind.py        # Logic for the `remind` command.
```

### 3. AI Cost Optimization: The "Intelligent Summarizer"

The bot's interaction with the Gemini API is designed to be cost-effective.

- **Context Management:** The bot maintains a short-term `conversation_log` and a long-term `conversation_summary` for each chat.
- **Summarization Task:** A background process will periodically use a cost-effective AI model (e.g., Gemini Flash) to summarize the `conversation_log`, save it to the `conversation_summary`, and then clear the log.
- **Optimized Prompts:** When generating responses, the bot sends a highly efficient prompt containing the long-term summary and only the most recent messages, dramatically reducing token usage.

## Future Evolution

The architecture is designed to be extensible. Future features will be added as new modules in the `commands/` directory, and the `Context` object can be expanded to store new types of data as needed.
