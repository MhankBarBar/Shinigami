from Shinigami.commands import BaseCommand


class Ping(BaseCommand):
    command = "ping"

    @staticmethod
    def call(c, m, **_):
        c.reply_message("PonG!", m)
