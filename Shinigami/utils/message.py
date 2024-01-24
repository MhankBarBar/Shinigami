from typing import Callable
from dataclasses import dataclass

from neonize.proto.Neonize_pb2 import JID
from neonize.utils.jid import Jid2String, JIDToNonAD


@dataclass
class QuotedMessage:
    chat: str
    pushname: str
    message: str
    sender: str
    message_id: str
    message_type: str
    is_media: bool
    media_type: str
    raw_message: any


@dataclass
class Message:
    chat: str
    pushname: str
    message: str
    sender: str
    timestamp: int
    message_id: str
    message_type: str
    is_media: bool
    is_group: bool
    is_edit: bool
    quoted_message: Callable
    media_type: str = None


class SimplifiedMessage:

    def __init__(self, c, message):
        self.c = c
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
            self.extract_quoted_message,
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

    def __extract_quoted_from_context_info(self, msg) -> QuotedMessage | None:
        if msg.HasField("contextInfo"):
            cont_info = msg.contextInfo
            if cont_info.HasField("quotedMessage"):
                qmsg = cont_info.quotedMessage
                _type = None
                text_or_cap = None
                pushname = None
                if f := self.c.contact.get_contact(self.string_to_jid(cont_info.participant)):
                    pushname = f.PushName if f.Found else None
                if qmsg.HasField("extendedTextMessage") or qmsg.HasField("conversation"):
                    _type = "text"
                    text_or_cap = qmsg.conversation or qmsg.extendedTextMessage.text
                elif qmsg.HasField("imageMessage"):
                    _type = "image"
                    text_or_cap = qmsg.imageMessage.caption
                elif qmsg.HasField("videoMessage"):
                    _type = "video"
                    text_or_cap = qmsg.videoMessage.caption
                elif qmsg.HasField("documentMessage"):
                    _type = "document"
                    text_or_cap = qmsg.documentMessage.caption
                elif qmsg.HasField("stickerMessage"):
                    _type = "sticker"
                return QuotedMessage(
                    cont_info.participant,
                    pushname,
                    text_or_cap,
                    cont_info.participant,
                    cont_info.stanzaId,
                    _type,
                    _type is not None and _type != "text",
                    _type,
                    raw_message=qmsg
                )
            else:
                return None

    def extract_quoted_message(self):
        smsg = self.simplified()
        if smsg.message_type == "text":
            if self.message.Message.HasField("extendedTextMessage"):
                return self.__extract_quoted_from_context_info(
                    self.message.Message.extendedTextMessage
                )
        elif smsg.message_type == "media":
            if self.message.Message.HasField("imageMessage"):
                return self.__extract_quoted_from_context_info(
                    self.message.Message.imageMessage
                )
            elif self.message.Message.HasField("videoMessage"):
                return self.__extract_quoted_from_context_info(
                    self.message.Message.videoMessage
                )
            elif self.message.Message.HasField("documentMessage"):
                return self.__extract_quoted_from_context_info(
                    self.message.Message.documentMessage
                )
            elif self.message.Message.HasField("stickerMessage"):
                return self.__extract_quoted_from_context_info(
                    self.message.Message.stickerMessage
                )
        return None
