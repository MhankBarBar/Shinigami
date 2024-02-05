import os
from pathlib import Path

from Shinigami.commands import BaseCommand
from Shinigami.config import Config


class SetLang(BaseCommand):
    command = "setlang"
    alias = ["lang"]

    @staticmethod
    def call(c, args, m, i18n, **_):
        if len(args) != 2:
            c.reply_message(i18n["helper"]["set_lang"], m)
            return
        dir_path = Path(__file__).parent.parent.resolve() / "locales"
        available_langs = []
        for filename in os.listdir(dir_path):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                available_langs.append(filename.split(".")[0])
        if args[1].lower() not in available_langs:
            c.reply_message(
                i18n["error"]["set_lang"]["invalid"] % "\n- ".join(available_langs), m
            )
            return
        Config.LANGUAGE = args[1].lower()
        c.reply_message(i18n["cmd"]["set_lang"]["success"] % args[1], m)
