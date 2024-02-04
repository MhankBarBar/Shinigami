from Shinigami.commands import BaseCommand


class Help(BaseCommand):
    command = "help"
    alias = ["h"]

    @staticmethod
    def call(c, m, i18n, **_):
        c.reply_message(i18n["cmd"]["help"].strip(), m)
