from Shinigami.commands import BaseCommand


class Help(BaseCommand):
    command = "help"
    alias = ["h"]

    @staticmethod
    def call(**opts):
        c = opts.get("c")
        c.reply_message("Help", opts.get("m"))
