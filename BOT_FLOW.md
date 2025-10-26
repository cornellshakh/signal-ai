### Detailed User-Bot Interaction & Command Flow

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

### Detailed Explanation of User-Bot Interaction & Command Flow

This document details the user-bot interaction flow, including command handling and AI integration. The diagram illustrates the two primary interaction patterns: `@mention`-driven conversation and `!`-prefix commands.

1. **Core Logic**: The `SignalBot` instance ingests every message and first determines if it's a command or a conversational mention.

2. **Command Routing**: The bot routes commands based on the `!` prefix. Here's a breakdown of each command:

   - **`!help`**:

     - _Purpose_: Displays a help message with available commands to the user.
     - _Flow_: The bot generates a list of available commands and sends it to the user.

   - **`!status`**:

     - _Purpose_: Provides a status report of the bot, including system information.
     - _Flow_: The bot gathers system information and sends a formatted status message to the user.

   - **`!model`**:

     - _Purpose_: Allows the user to set the AI model for the current chat.
     - _Flow_: The bot allows the user to specify an AI model, which is then used for subsequent AI interactions.

   - **`!prompt`**:

     - _Purpose_: Allows the user to set a custom system prompt for the current chat, influencing the AI's behavior.
     - _Flow_: The bot allows the user to set a custom system prompt, which is then used for subsequent AI interactions.

   - **`!mode`**:

     - _Purpose_: Sets the bot's response mode in group chats (either `all` or `mention`).
     - _Flow_: The bot allows the user to specify the response mode, determining whether the bot responds to all messages or only when mentioned.
     - _Default Behavior_: In group chats, the default mode is `mention`, meaning the bot only responds when mentioned. When talking to the bot directly in a private chat (no group chat), the bot always responds to every message.

   - **`!history`**:

     - _Purpose_: Manages the conversation history, allowing the user to view or clear it.
     - _Flow_: The bot allows the user to view the conversation history or clear it.

   - **`!new`**:

     - _Purpose_: Generates an intro message for a new conversation.
     - _Flow_: The bot uses the Gemini AI API to generate an engaging intro message based on the provided topic.

   - **`!image`**:

     - _Purpose_: Generates an image based on a prompt using the Gemini AI API.
     - _Flow_: The bot uses the Gemini AI API to generate an image based on the provided prompt.

   - **`!search`**:
     - _Purpose_: Performs a web search or fetches content from a URL and summarizes it.
     - _Flow_: The bot uses the Gemini AI API to search the web or fetch content from a URL and summarizes it.

3. **AI-Powered Commands and Conversation**:

   - `@BotName`: Natural conversation.
   - The bot uses the **Gemini AI API** to generate responses for `!search`, `!image`, and natural conversations.
   - The AI's output is formatted with markdown styling before being sent back to the user.

4. **AI Interaction**:

   - The bot uses the Gemini AI API to generate responses, search the web, and generate images.
   - The Gemini AI API takes the conversation history, a new prompt, and a system prompt as input. It then sends the information to the Gemini AI model and returns the response.

5. **Feedback Loop**: The three-stage feedback system (`typing`, `⏳`, `⚛️/❌`) runs in parallel, providing the user with constant status updates for any AI-related task.
