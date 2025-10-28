from typing import Optional, TYPE_CHECKING
from collections import defaultdict
from signalbot import Command, Context, regex_triggered

if TYPE_CHECKING:
    from src.signal_ai.bot import SignalAIBot


class HelpCommand(Command):
    def __init__(self, bot: "SignalAIBot"):
        self.bot = bot

    def describe(self) -> str:
        return "Shows available commands and namespaces."

    @regex_triggered(r"^!help\s*(.*)$")
    async def handle(self, c: Context, query: Optional[str] = None) -> None:
        try:
            if query is None:
                query = ""
                
            namespace_descriptions = {
                "system": "Core bot operations.",
                "config": "Bot settings management.",
                "context": "Conversation context management.",
                "memory": "Long-term memory management.",
                "task": "Task and reminder management.",
                "ai": "Direct AI model interactions.",
                "utility": "Miscellaneous tools.",
            }

            commands_by_namespace = defaultdict(list)
            all_commands = {}
            for item in self.bot.commands:
                command = item[0]
                if isinstance(command, Command) and not isinstance(command, HelpCommand) and command.describe():
                    command_name = command.__class__.__name__.lower().replace('command', '')
                    all_commands[command_name] = command
                    
                    module_parts = command.__module__.split('.')
                    try:
                        commands_index = module_parts.index("commands")
                        if commands_index + 1 < len(module_parts):
                            namespace = module_parts[commands_index + 1]
                            commands_by_namespace[namespace].append(command)
                    except ValueError:
                        continue

            query = query.strip().lower() if query else ""

            if query:
                # Case 1: Query is a command
                if query in all_commands:
                    command = all_commands[query]
                    if hasattr(command, "help"):
                        help_text = command.help()
                    else:
                        help_text = command.describe()

                # Case 2: Query is a namespace
                elif query in commands_by_namespace:
                    help_text = f"*Commands in `{query}` namespace:*\n"
                    for command in sorted(commands_by_namespace[query], key=lambda cmd: cmd.__class__.__name__):
                        command_name = command.__class__.__name__.lower().replace('command', '')
                        help_text += f"- `{command_name}`: {command.describe()}\n"
                    help_text += f"\nRun `!help [command]` for more details on a specific command."
                
                # Case 3: Unknown query
                else:
                    help_text = f"Unknown command or namespace: `{query}`. Run `!help` to see all available namespaces."

            else:
                # Default help: list all namespaces
                help_text = "*Available Command Namespaces:*\n"
                for namespace in sorted(commands_by_namespace.keys()):
                    description = namespace_descriptions.get(namespace, "No description available.")
                    help_text += f"- `{namespace}`: {description}\n"
                help_text += "\nRun `!help [namespace]` or `!help [command]` for more information."

            await c.reply(help_text, text_mode="styled")
        except Exception as e:
            await c.reply(f"An error occurred in the help command: {e}", text_mode="styled")
