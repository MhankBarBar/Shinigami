from io import BytesIO

from magic import from_buffer
from requests import post

from . import BaseCommand


def transcribe(buff):
    api = "https://api.mhankbarbar.tech/transcribe"
    file = {
        "file": (
            "title.mp3",
            BytesIO(buff),
            from_buffer(buff, mime=True),
        )
    }
    res = post(api, files=file)
    if res.status_code == 200:
        return res.json()["result"]
    else:
        raise Exception("Failed to transcribe")


class Transcribe(BaseCommand):
    command = "transcribe"

    @staticmethod
    def call(c, m, sm, i18n, **_):
        if sm.message_type == "text" or sm.is_media and "audio" in sm.media_type:
            media_message = x if (x := sm.quoted_message()) else sm
            if media_message.is_media and "audio" in media_message.media_type:
                c.reply_message("Transcribing...", m)
                try:
                    buff = c.download_any(media_message.raw_message)
                    res = transcribe(buff)
                    c.reply_message(res, m)
                except Exception as e:
                    c.reply_message(f"Failed to transcribe: {e}", m)
            else:
                c.reply_message(i18n["error"]["transcribe"]["no_media"], m)
