import os
import sys

from neonize.client import JID

from Shinigami.commands import BaseCommand
from Shinigami.ipc import sgiapi


class Restart(BaseCommand):
    command = "restart"
    is_owner = True

    @staticmethod
    def call(**opts):
        opts.get("c").reply_message("Restarting...!", opts.get("m"))
        if not sgiapi.closed:
            chat: JID = opts.get("m").Info.MessageSource.Chat
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
        else:
            os.execl(sys.executable, sys.executable, *sys.argv)