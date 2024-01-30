from Shinigami.commands import BaseCommand
from Shinigami.config import STICKER_NAME, STICKER_PACK
from Shinigami.utils.message import SimplifiedMessage


class Sticker(BaseCommand):
    command = "sticker"
    alias = ["s", "stiker"]

    @staticmethod
    def call(**opts):
        message = opts.get("sm")
        media_type = message.media_type

        if (
            message.message_type == "text"
            or message.is_media
            and media_type in ("image", "video")
        ):
            media_message = x if (x := message.quoted_message()) else message
            if (
                media_message.media_type == "video"
                and media_message.raw_message.videoMessage.seconds > 10
            ):
                opts.get("c").reply_message("video too long", opts.get("m"))
                return
            if media_message.is_media and media_message.media_type in (
                "image",
                "video",
            ):
                b = opts.get("c").download_any(media_message.raw_message)
                opts.get("c").send_sticker(
                    SimplifiedMessage.string_to_jid(message.chat),
                    b,
                    opts.get("m"),
                    STICKER_NAME,
                    STICKER_PACK,
                )
        else:
            opts.get("c").reply_message("send/reply image/video", opts.get("m"))
