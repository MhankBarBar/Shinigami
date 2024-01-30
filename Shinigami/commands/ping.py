from Shinigami.commands import BaseCommand


class Ping(BaseCommand):
    command = "ping"

    @staticmethod
    def call(**opts):
        opts.get("c").reply_message("PonG!", opts.get("m"))
