from Shinigami.commands import BaseCommand
from Shinigami.utils.message import SimplifiedMessage


class Help(BaseCommand):
    command = "help"
    alias = ["h"]

    @staticmethod
    def call(**opts):
        c = opts.get("c")
        c.reply_message(SimplifiedMessage.string_to_jid(opts.get("sm").chat), "Help", opts.get("m"))