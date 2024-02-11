import os
import re
import string
from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path

from Shinigami.config import Config
from Shinigami.utils import is_windows

if not is_windows():
    from Shinigami.ipc import sgiapi


@dataclass
class BaseCommand(ABC):
    command: str
    tags: str
    help: str
    alias: list = field(default_factory=list)
    is_owner: bool = False

    def get_help(self, c, m):
        return c.reply_message(self.help, m)


class CommandHandler:
    def __init__(self):
        self.prefix = Config.PREFIX if Config.PREFIX else re.escape(string.punctuation)
        self.command_pattern = re.compile(rf"^([{self.prefix}])\w+")
        self.commands = []

    def add_command(self, command):
        self.commands.append(command)

    def handle_command(self, message, **opts):
        for command in self.commands:
            if hasattr(command, "execute"):
                command.execute(**opts)
            elif match := self.command_pattern.match(message):
                command_name = match.group().lstrip(string.punctuation)
                if (
                    hasattr(command, "alias")
                    and command_name in command.alias
                    or hasattr(command, "command")
                    and command_name == command.command
                ):
                    command.call(**opts)
                    if not is_windows():
                        sgiapi.send_commmand("hit", {"name": command.command})

    # def match_command(self, message, command_pattern) -> bool:
    #     match = re.match(fr"^{re.escape(string.punctuation)}{command_pattern}$", message, re.IGNORECASE)
    #     return bool(match)


class CommandLoader:
    @staticmethod
    def load_commands(handler, path: Path = Path(__file__).parent.parent / "commands"):
        if not os.path.exists(path.parent.name):
            raise Exception(
                f"Error: The '{path.parent.name}' directory does not exist."
            )

        for filename in path.iterdir():
            if filename.name.endswith(".py"):
                module_name = filename.name[:-3]
                if module_name == "__init__":
                    continue
                module = getattr(
                    getattr(
                        __import__(f"{path.parent.name}.{path.name}.{module_name}"),
                        path.name,
                    ),
                    module_name,
                )
                for x in dir(module):
                    if (
                        hasattr(getattr(module, x), "__bases__")
                    ) and BaseCommand in getattr(module, x).__bases__:
                        cmd: BaseCommand = getattr(module, x)
                        handler.add_command(cmd)
