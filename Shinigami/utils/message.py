from dataclasses import dataclass

from neonize.proto.Neonize_pb2 import JID
from neonize.utils.jid import Jid2String, JIDToNonAD


@dataclass
class QuotedMessage:
    _from: int
    pushname: str
    message: str
    sender: str
    timestamp: int
    message_id: str
    message_type: str
    is_media: bool
    is_group: bool
    is_edit: bool
    media_type: str


@dataclass
class Message:
    chat: int
    pushname: str
    message: str
    sender: str
    timestamp: int
    message_id: str
    message_type: str
    is_media: bool
    is_group: bool
    is_edit: bool
    media_type: str = None


class SimplifiedMessage:

    def __init__(self, message):
        self.message = message

    def simplified(self) -> Message:
        info = self.message.Info
        return Message(
            self.__jid_to_string(info.MessageSource.Chat),
            info.Pushname,
            self.extract_text(),
            self.__jid_to_string(info.MessageSource.Sender),
            info.Timestamp,
            info.ID,
            info.Type,
            info.Type == "media",
            info.MessageSource.IsGroup,
            self.message.IsEdit,
            info.MediaType if info.Type == "media" else None,
        )

    def __jid_to_string(self, jid):
        return Jid2String(JIDToNonAD(jid))

    @staticmethod
    def string_to_jid(jid) -> JID:
        return JID(
            User=jid.split("@")[0],
            Server=jid.split("@")[1],
            RawAgent=0,
            Device=0,
            Integrator=0,
            IsEmpty=False,
        )

    def extract_text(self) -> str:
        message_type = self.message.Info.Type
        media_type = self.message.Info.MediaType if message_type == "media" else None
        text = ""
        if message_type == "text":
            text = (
                self.message.Message.conversation
                or self.message.Message.extendedTextMessage.text
                or ""
            )
        elif message_type == "media" and media_type != "sticker":
            match media_type:
                case "image":
                    text = self.message.Message.imageMessage.caption
                case "video":
                    text = self.message.Message.videoMessage.caption
                case "document":
                    text = self.message.Message.documentMessage.caption
        return text
