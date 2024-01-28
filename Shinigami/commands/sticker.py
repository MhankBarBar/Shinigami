from Shinigami.commands import BaseCommand
from Shinigami.utils.message import SimplifiedMessage
from ..config import STICKER_NAME, STICKER_PACK


class Sticker(BaseCommand):
    command = "sticker"
    alias = ["s", "stiker"]

    @staticmethod
    def call(**opts):
        c = opts.get("c")
        m = opts.get("m")
        sm = opts.get("sm")
        if sm.message_type == "media":
            if sm.media_type in ("image", "video"):
                if sm.media_type == "video" and m.Message.videoMessage.seconds > 10:
                    return c.reply_message(SimplifiedMessage.string_to_jid(sm.chat), "video is too long", m)
                b = c.download_any(m.Message)
                c.send_sticker(
                    SimplifiedMessage.string_to_jid(sm.chat),
                    b,
                    m,
                    STICKER_NAME,
                    STICKER_PACK
                )
        elif x := sm.quoted_message():
            if x.is_media and x.media_type in ("image", "video"):
                if x.media_type == "video" and x.raw_message.videoMessage.seconds > 10:
                    return c.reply_message(SimplifiedMessage.string_to_jid(sm.chat), "video is too long", m)
                b = c.download_any(x.raw_message)
                c.send_sticker(
                    SimplifiedMessage.string_to_jid(sm.chat),
                    b,
                    m,
                    STICKER_NAME,
                    STICKER_PACK
                )
        else:
            c.reply_message(SimplifiedMessage.string_to_jid(sm.chat), "send/reply image/video", m)
