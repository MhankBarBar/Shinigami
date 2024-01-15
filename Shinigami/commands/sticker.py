from Shinigami.commands import BaseCommand
from Shinigami.utils.message import SimplifiedMessage


class Sticker(BaseCommand):
    command = "sticker"
    alias = ["s", "stiker"]

    @staticmethod
    def callback(**opts):
        c = opts.get("c")
        m = opts.get("m")
        sm = opts.get("sm")
        if sm.message_type == "media":
            if "image" or "video" in sm.media_type:
                x = c.download_any(m.Message)
                c.send_sticker(SimplifiedMessage.string_to_jid(sm.chat), x, m)
        else:
            c.reply_message(SimplifiedMessage.string_to_jid(sm.chat), "send image/video", m)
