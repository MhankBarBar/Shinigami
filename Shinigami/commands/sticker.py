from Shinigami.commands import BaseCommand
from Shinigami.utils.message import SimplifiedMessage


class Sticker(BaseCommand):
    command = "sticker"
    alias = ["s", "stiker"]

    @staticmethod
    def call(**opts):
        c = opts.get("c")
        m = opts.get("m")
        sm = opts.get("sm")
        if sm.message_type == "media":
            if "image" or "video" in sm.media_type:
                b = c.download_any(m.Message)
                c.send_sticker(SimplifiedMessage.string_to_jid(sm.chat), b, m)
        elif x := sm.quoted_message():
            if x.is_media and "image" or "video" in x.media_type:
                b = c.download_any(x.raw_message)
                c.send_sticker(SimplifiedMessage.string_to_jid(sm.chat), b, m)
        else:
            c.reply_message(SimplifiedMessage.string_to_jid(sm.chat), "send/reply image/video", m)
