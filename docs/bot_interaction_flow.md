# Bot Interaction and Command Flow

This document outlines the user-bot interaction flow, including command handling and AI integration. The system is designed to support two primary interaction patterns: natural conversation driven by `@mentions` and specific actions triggered by `!`-prefix commands.

## Visual Flowchart

The following diagram illustrates the complete lifecycle of a user's message, from input to the bot's final response.

```mermaid
graph TD
    subgraph Legend
        direction LR
        L1[Input] -- L2[Process] -- L3[Output]
    end

    subgraph User Input
        A[User sends message]
    end

    subgraph Bot Core Logic
        B(SignalBot)
        A --> B
        B --> C{Parse: Command or Mention?}
    end

    subgraph Command Handling
        C -- Command --> D{Route Command}
        D -- '!help' --> Help[Generate & Send Help Text]
        D -- '!status' --> Status[Check AIClient & Send Model Name]
        D -- '!model' --> Model[Get/Set AI Model for Chat]
        D -- '!prompt' --> Prompt[Set System Persona for Chat]
        D -- '!history' --> History{summarize/clear}
        D -- '!new' --> New[Create New Group Chat]
        D -- '!mode' --> Mode[Get/Set Response Mode]
        D -- '!search' --> Search[AIClient: Web Search/URL Summary]
        D -- '!image' --> Image[AIClient: Generate Image]
        C -- Mention or Reply --> Conv[AIClient: Natural Conversation]
    end

    subgraph AI & Output
        subgraph AIClient
            direction LR
            Search --> AIC
            Image --> AIC
            Conv --> AIC
        end
        AIC(AI Model - Gemini) --> Res{Generate Text/Image}
        Res --> Format[Format Response with Markdown]
    end

    subgraph Final Output
      Format --> Out(Send Final Message/Image)
      Help --> Out
      Status --> Out
      Model --> Out
      Prompt --> Out
      New --> Out
      History --> Out
    end

    subgraph User Feedback System
        B -- On Receive --> T1[Show Typing Indicator]
        AIC -- On AI Call --> T2[React with ⏳]
        Out -- On Success/Fail --> T3[Replace ⏳ with ⚛️ or ❌]
    end

    Out --> A
```

## Core Logic

The `SignalBot` instance processes every incoming message to determine whether it is a command (prefixed with `!`) or a conversational mention (prefixed with `@`).

## Command Reference

The bot routes commands based on the `!` prefix. Here is a breakdown of each available command:

- **`!help`**

  - **Purpose:** Displays a help message with a list of available commands.
  - **Flow:** The bot generates and sends a formatted list of commands to the user.

- **`!status`**

  - **Purpose:** Provides a status report of the bot, including system information.
  - **Flow:** The bot gathers system information and sends a formatted status message.

- **`!model`**

  - **Purpose:** Allows the user to set the AI model for the current chat.
  - **Flow:** The user can specify an AI model, which will be used for all subsequent AI interactions in that chat.

- **`!prompt`**

  - **Purpose:** Sets a custom system prompt for the current chat, influencing the AI's personality and behavior.
  - **Flow:** The user-defined prompt is saved and used for subsequent AI interactions.

- **`!mode`**

  - **Purpose:** Sets the bot's response mode in group chats to either `all` or `mention`.
  - **Flow:** In `mention` mode (the default in group chats), the bot only responds when mentioned. In `all` mode, it responds to every message. In private chats, the bot always responds.

- **`!history`**

  - **Purpose:** Manages the conversation history.
  - **Flow:** Allows the user to either view or clear the conversation history for the current chat.

- **`!new`**

  - **Purpose:** Generates an introductory message for a new conversation topic.
  - **Flow:** The bot uses the Gemini AI API to create an engaging intro message based on the provided topic.

- **`!image`**

  - **Purpose:** Generates an image based on a user's prompt.
  - **Flow:** The bot uses the Gemini AI API to generate and send an image.

- **`!search`**
  - **Purpose:** Performs a web search or fetches and summarizes content from a URL.
  - **Flow:** The bot uses the Gemini AI API to perform the search or summarization and returns the result.

## AI-Powered Interactions

- **Natural Conversation:** When the bot is mentioned with `@BotName`, it engages in natural conversation.
- **AI Backend:** The bot utilizes the **Gemini AI API** to generate responses for `!search`, `!image`, and conversational interactions.
- **Input Processing:** The Gemini AI API takes the conversation history, a new prompt, and a system prompt as input to generate a context-aware response.
- **Output Formatting:** All AI-generated text is formatted with Markdown for better readability.

## User Feedback System

A three-stage feedback system provides real-time updates for any AI-related task:

1.  A **typing indicator** is shown when a message is received.
2.  A `⏳` reaction is added to the message when the AI call is initiated.
3.  The `⏳` reaction is replaced with `⚛️` on success or `❌` on failure.
