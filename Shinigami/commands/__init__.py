import os
import re
import string
from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BaseCommand(ABC):
    command: str
    tags: str
    help: str
    alias: list = field(default_factory=list)


class CommandHandler:
    def __init__(self):
        self.command_pattern = re.compile(r'^([{}])\w+'.format(re.escape(string.punctuation)))
        self.commands = []

    def add_command(self, command):
        # self.commands[command.command] = command
        # if getattr(command, "alias", None):
        #     for alias in command.alias:
        #         self.commands[alias] = command
        self.commands.append(command)

    def handle_command(self, message, **opts):
        for command in self.commands:
            if hasattr(command, "execute"):
                command.execute(**opts)
            else:
                match = self.command_pattern.match(message)
                if match:
                    command_name = match.group().lstrip(string.punctuation)
                    if (
                        hasattr(command, "alias") and command_name in command.alias
                        or hasattr(command, "command") and command_name == command.command
                    ):
                        command.call(**opts)
            # if command_name in self.commands:
            #     command = self.commands[command_name]
            #     command.callback(**opts)

    # def match_command(self, message, command_pattern) -> bool:
    #     match = re.match(fr"^{re.escape(string.punctuation)}{command_pattern}$", message, re.IGNORECASE)
    #     return bool(match)


class CommandLoader:
    @staticmethod
    def load_commands(handler, path: Path = Path(__file__).parent.parent / "commands"):
        if not os.path.exists(path.parent.name):
            print(f"Error: The '{path.parent.name}' directory does not exist.")
            return

        for filename in path.iterdir():
            if filename.name.endswith('.py'):
                module_name = filename.name[:-3]
                if module_name == "__init__":
                    continue
                module = getattr(
                    getattr(
                        __import__(f'{path.parent.name}.{path.name}.{module_name}'), path.name
                    ),
                    module_name
                )
                for x in dir(module):
                    if (hasattr(
                            getattr(module, x),
                            '__bases__'
                    )) and BaseCommand in getattr(module, x).__bases__:
                        cmd: BaseCommand = getattr(module, x)
                        handler.add_command(cmd)
