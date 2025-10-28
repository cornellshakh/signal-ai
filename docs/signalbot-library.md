# SignalBot Usage Reference

This document provides a concise, technical reference for using the `signalbot` library, focusing on its public API and practical application, with detailed signatures and type hints.

---

## 1. `SignalBot` - The Core Class

### Initialization

```python
bot = SignalBot({
    "signal_service": "127.0.0.1:8080",
    "phone_number": "+49123456789",
    "storage": {"type": "sqlite", "sqlite_db": "mydb.db"}
})
```

### Public Attributes

- `storage`: `SQLiteStorage | RedisStorage`
- `scheduler`: `AsyncIOScheduler`

### Methods

#### `register`

- **Signature:** `register(self, command: Command, contacts: list[str] | bool = True, groups: list[str] | bool = True, f: Callable[[Message], bool] | None = None) -> None`
- **Description:** Registers a command with optional scoping.

#### `start`

- **Signature:** `start(self, run_forever: bool = True) -> None`
- **Description:** Starts the bot's event loop.

#### `send`

- **Signature:** `async def send(self, receiver: str, text: str, *, base64_attachments: list | None = None, link_preview: LinkPreview | None = None, quote_author: str | None = None, quote_mentions: list | None = None, quote_message: str | None = None, quote_timestamp: int | None = None, mentions: list[dict[str, Any]] | None = None, edit_timestamp: int | None = None, text_mode: str | None = None, view_once: bool = False) -> int`
- **Description:** Sends a message and returns its timestamp.

#### `react`

- **Signature:** `async def react(self, message: Message, emoji: str) -> None`
- **Description:** Reacts to a specific message.

#### `remote_delete`

- **Signature:** `async def remote_delete(self, receiver: str, timestamp: int) -> int`
- **Description:** Deletes a message for everyone.

#### `update_group`

- **Signature:** `async def update_group(self, group_id: str, base64_avatar: str | None = None, description: str | None = None, expiration_in_seconds: int | None = None, name: str | None = None) -> None`
- **Description:** Updates a group's properties.

---

## 2. `Command` - Creating Bot Logic

A `Command` is a class that encapsulates the logic for a bot command. It must implement the `handle` method.

```python
from signalbot import Command, Context

class HelloWorld(Command):
    def handle(self, context: Context) -> None:
        # Your command logic here
        context.send("Hello, world!")
```

---

## 3. `Context` - Interacting with the Chat

### Interaction Methods

#### `send`

- **Signature:** `async def send(self, text: str, *, base64_attachments: list[str] | None = None, link_preview: LinkPreview | None = None, mentions: list[dict[str, Any]] | None = None, text_mode: str | None = None, view_once: bool = False) -> int`

#### `reply`

- **Signature:** `async def reply(self, text: str, *, base64_attachments: list[str] | None = None, ...)`

#### `react`

- **Signature:** `async def react(self, emoji: str) -> None`

#### `edit`

- **Signature:** `async def edit(self, text: str, edit_timestamp: int, *, ...)`

#### `remote_delete`

- **Signature:** `async def remote_delete(self, timestamp: int) -> int`

#### `receipt`

- **Signature:** `async def receipt(self, receipt_type: Literal["read", "viewed"]) -> None`

---

## 4. `Message` - The Data Object

### Key Attributes

| Attribute                     | Type          |
| ----------------------------- | ------------- | ----- |
| `text`                        | `str`         |
| `source`                      | `str`         |
| `source_number`               | `str          | None` |
| `source_uuid`                 | `str`         |
| `timestamp`                   | `int`         |
| `group`                       | `str          | None` |
| `type`                        | `MessageType` |
| `reaction`                    | `str          | None` |
| `quote`                       | `Quote        | None` |
| `mentions`                    | `list`        |
| `base64_attachments`          | `list[str]`   |
| `attachments_local_filenames` | `list[str]`   |
| `view_once`                   | `bool`        |

---

## 5. Practical Examples

### Replying to a Message

```python
from signalbot import Command, Context

class ReplyCommand(Command):
    def handle(self, context: Context) -> None:
        # Replies directly to the message that triggered the command
        context.reply("I received your message!")
```

### Reacting to a Message

```python
from signalbot import Command, Context

class ReactCommand(Command):
    def handle(self, context: Context) -> None:
        # Reacts to the original message with an emoji
        context.react("👍")
```
