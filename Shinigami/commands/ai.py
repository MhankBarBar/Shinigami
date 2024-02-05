from characterai import PyCAI

from Shinigami.commands import BaseCommand
from Shinigami.config import Config
from Shinigami.utils.message import SimplifiedMessage


class AI(BaseCommand):
    @staticmethod
    def execute(c, m, sm, i18n, **_):
        me = SimplifiedMessage.jid_to_string(c.get_me().JID)
        if (x := sm.get_mention()) or sm.text.startswith("@ai "):
            is_me = list(filter(lambda i: i == me, x))
            if is_me or sm.text.startswith("@ai "):
                text = sm.text.replace(
                    f"@{is_me[0].split('@')[0]}" if is_me else "@ai ", ""
                ).strip()
                if not text:
                    c.reply_message(i18n["cmd"]["ai"], m)
                    return

                client = PyCAI(Config.CHARACTERAI_TOKEN)
                chat = client.chat.get_chat(Config.CHARACTERAI_CHARACTER)
                participants = chat["participants"]

                if not participants[0]["is_human"]:
                    tgt = participants[0]["user"]["username"]
                else:
                    tgt = participants[1]["user"]["username"]

                data = client.chat.send_message(chat["external_id"], tgt, text)
                res = data["replies"][0]["text"]
                c.reply_message(res, m)
