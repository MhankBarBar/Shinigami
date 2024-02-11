import json
import os
from os import PathLike
from pathlib import Path
from typing import Optional

from Shinigami.utils import is_windows

if not is_windows():
    from Shinigami.ipc import sgiapi

SHINIGAMI = Path(__file__).parent

CHILD = bool(os.environ.get("debug"))


class ShinigamiConfig:
    SESSION_DIR = SHINIGAMI / "session"
    CONFIG_FILE = SHINIGAMI / "config.json"

    def __init__(
        self,
        session_name: str,
        sticker_name: str,
        sticker_pack: str,
        bot_name: str,
        prefix: str,
        owner: str,
        characterai_token: str,
        characterai_character: str,
        language: str,
        config_file: Optional[PathLike],
    ) -> None:
        self.__SESSION_NAME = session_name
        self.__STICKER_NAME = sticker_name
        self.__STICKER_PACK = sticker_pack
        self.__OWNER = owner
        self.__PREFIX = prefix
        self.__BOT_NAME = bot_name
        self.__CHARACTERAI_TOKEN = characterai_token
        self.__CHARACTERAI_CHARACTER = characterai_character
        self.__LANGUAGE = language
        if config_file:
            self.CONFIG_FILE = config_file

    @classmethod
    def load_config(cls, config_file: Optional[PathLike] = None):
        file_path = cls.CONFIG_FILE if config_file is None else config_file
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                file.write("{}")
        with open(file_path) as file:
            config = json.load(file)
            return cls(
                config.get("session_name", "Shinigami.session"),
                config.get("sticker_name", "Shinigami"),
                config.get("sticker_pack", "Bot"),
                config.get("bot_name", "Shinigami"),
                config.get("prefix", "/"),
                config.get("owner", "6281234567890"),
                config.get("characterai_token", ""),
                config.get("characterai_character", ""),
                config.get("language", "en"),
                config_file,
            )

    def send_update_config(self):
        sgiapi.send_commmand(
            "update_config",
            {
                "session_name": self.SESSION_NAME,
                "sticker_name": self.STICKER_NAME,
                "sticker_pack": self.STICKER_PACK,
                "bot_name": self.BOT_NAME,
                "prefix": self.PREFIX,
                "owner": self.OWNER,
                "characterai_token": self.CHARACTERAI_TOKEN,
                "characterai_character": self.CHARACTERAI_CHARACTER,
                "language": self.LANGUAGE,
            },
        )

    def update_config(
        self,
        session_name: Optional[str] = None,
        sticker_name: Optional[str] = None,
        sticker_pack: Optional[str] = None,
        bot_name: Optional[str] = None,
        prefix: Optional[str] = None,
        owner: Optional[str] = None,
        characterai_token: Optional[str] = None,
        characterai_character: Optional[str] = None,
        language: Optional[str] = None,
    ):
        with open(self.CONFIG_FILE, "w") as file:
            if sticker_pack:
                self.__SESSION_NAME = sticker_name
            if session_name:
                self.__SESSION_NAME = session_name
            if sticker_pack:
                self.__STICKER_PACK = sticker_pack
            if bot_name:
                self.__BOT_NAME = bot_name
            if prefix:
                self.__PREFIX = prefix
            if owner:
                self.__OWNER = owner
            if characterai_token:
                self.__CHARACTERAI_TOKEN = characterai_token
            if characterai_character:
                self.__CHARACTERAI_CHARACTER = characterai_character
            if language:
                self.__LANGUAGE = language
            file.write(
                json.dumps(
                    {
                        "session_name": self.SESSION_NAME,
                        "sticker_name": self.STICKER_NAME,
                        "sticker_pack": self.STICKER_PACK,
                        "bot_name": self.BOT_NAME,
                        "prefix": self.PREFIX,
                        "owner": self.OWNER,
                        "characterai_token": self.CHARACTERAI_TOKEN,
                        "characterai_character": self.CHARACTERAI_CHARACTER,
                        "language": self.LANGUAGE,
                    },
                    indent=4,
                )
            )
            file.close()

    @property
    def SESSION_NAME(self):
        return self.__SESSION_NAME

    @SESSION_NAME.setter
    def SESSION_NAME(self, value: str):
        self.__SESSION_NAME = value
        self.update_config()

    @property
    def STICKER_NAME(self):
        return self.__STICKER_NAME

    @STICKER_NAME.setter
    def STICKER_NAME(self, value: str):
        self.__STICKER_NAME = value
        self.update_config()

    @property
    def STICKER_PACK(self):
        return self.__STICKER_PACK

    @STICKER_PACK.setter
    def STICKER_PACK(self, value: str):
        self.__STICKER_PACK = value
        self.update_config()

    @property
    def OWNER(self):
        return self.__OWNER

    @OWNER.setter
    def OWNER(self, value: str):
        self.__OWNER = value
        self.update_config()

    @property
    def PREFIX(self):
        return self.__PREFIX

    @PREFIX.setter
    def PREFIX(self, value: str):
        self.__PREFIX = value
        self.update_config()

    @property
    def BOT_NAME(self):
        return self.__BOT_NAME

    @BOT_NAME.setter
    def BOT_NAME(self, value: str):
        self.__BOT_NAME = value
        self.update_config()

    @property
    def CHARACTERAI_TOKEN(self):
        return self.__CHARACTERAI_TOKEN

    @CHARACTERAI_TOKEN.setter
    def CHARACTERAI_TOKEN(self, value: str):
        self.__CHARACTERAI_TOKEN = value
        self.update_config()

    @property
    def CHARACTERAI_CHARACTER(self):
        return self.__CHARACTERAI_CHARACTER

    @CHARACTERAI_CHARACTER.setter
    def CHARACTERAI_CHARACTER(self, value: str):
        self.__CHARACTERAI_CHARACTER = value
        self.update_config()

    @property
    def LANGUAGE(self):
        return self.__LANGUAGE

    @LANGUAGE.setter
    def LANGUAGE(self, value: str):
        self.__LANGUAGE = value
        self.update_config()


Config = ShinigamiConfig.load_config()
