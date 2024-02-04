from Shinigami.commands import BaseCommand
from Shinigami.config import Config
from Shinigami.utils.message import SimplifiedMessage


class Sticker(BaseCommand):
    command = "sticker"
    alias = ["s", "stiker"]

    @staticmethod
    def call(c, sm, m, i18n, **_):
        media_type = sm.media_type

        if (
            sm.message_type == "text"
            or sm.is_media
            and media_type in ("image", "video")
        ):
            media_message = x if (x := sm.quoted_message()) else sm
            if (
                media_message.media_type == "video"
                and media_message.raw_message.videoMessage.seconds > 10
            ):
                c.reply_message(i18n["error"]["sticker"]["too_long"], m)
                return
            if media_message.is_media and media_message.media_type in (
                "image",
                "video",
            ):
                b = c.download_any(media_message.raw_message)
                c.send_sticker(
                    SimplifiedMessage.string_to_jid(sm.chat),
                    b,
                    m,
                    Config.STICKER_NAME,
                    Config.STICKER_PACK,
                )
            else:
                c.reply_message(i18n["error"]["sticker"]["no_media"], m)
