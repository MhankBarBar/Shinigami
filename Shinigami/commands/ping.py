from Shinigami.commands import BaseCommand
from Shinigami.utils.message import SimplifiedMessage


class Ping(BaseCommand):
    command = "ping"

    @staticmethod
    def callback(**opts):
        opts.get("c").reply_message(
            SimplifiedMessage.string_to_jid(
                opts.get("sm").chat,
            ),
            "PonG!",
            opts.get("m")
        )
