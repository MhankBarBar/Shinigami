from neonize.client import JID
from . import BaseCommand
from ..ipc import sgiapi


class Restart(BaseCommand):
    command = "restart"

    @staticmethod
    def call(**opts):
        chat: JID = opts.get("m").Info.MessageSource.Chat
        opts.get("c").reply_message("Restarting...!", opts.get("m"))
        sgiapi.send_commmand(
            "restart",
            {
                "chat": {
                    "User": chat.User,
                    "Server": chat.Server,
                    "RawAgent": chat.RawAgent,
                    "Device": chat.Device,
                    "Integrator": chat.Integrator,
                    "IsEmpty": chat.IsEmpty,
                }
            },
        )
