from collections.abc import Callable
from dataclasses import dataclass

from neonize.client import NewClient
from neonize.proto import Neonize_pb2
from neonize.proto.def_pb2 import Message as RawMessage
from neonize.utils.jid import Jid2String, JIDToNonAD


@dataclass
class QuotedMessage:
    chat: str
    pushname: str
    text: str
    sender: str
    message_id: str
    message_type: str
    is_media: bool
    media_type: str
    raw_message: RawMessage


@dataclass
class Message:
    chat: str
    pushname: str
    text: str
    sender: str
    timestamp: int
    message_id: str
    message_type: str
    is_media: bool
    is_group: bool
    is_edit: bool
    quoted_message: Callable
    get_mention: Callable
    raw_message: RawMessage
    media_type: str = None


class SimplifiedMessage:
    def __init__(self, c: NewClient, message: Neonize_pb2.Message):
        self.c = c
        self.message = message

    def simplified(self) -> Message:
        info = self.message.Info
        return Message(
            chat=self.jid_to_string(info.MessageSource.Chat),
            pushname=info.Pushname,
            text=self.extract_text(),
            sender=self.jid_to_string(info.MessageSource.Sender),
            timestamp=info.Timestamp,
            message_id=info.ID,
            message_type=info.Type,
            is_media=info.Type == "media"
            and info.MediaType not in ("location", "livelocation"),
            is_group=info.MessageSource.IsGroup,
            is_edit=self.message.IsEdit,
            quoted_message=self.extract_quoted_message,
            get_mention=self.__extract_mention,
            media_type=info.MediaType if info.Type == "media" else None,
            raw_message=self.message.Message,
        )

    @staticmethod
    def jid_to_string(jid):
        return Jid2String(JIDToNonAD(jid))

    @staticmethod
    def string_to_jid(jid) -> Neonize_pb2.JID:
        return Neonize_pb2.JID(
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
        if message_type == "text" or media_type == "url":
            return (
                self.message.Message.conversation
                or self.message.Message.extendedTextMessage.text
                or ""
            )
        elif message_type == "poll":
            if self.message.Message.HasField("pollCreationMessage"):
                return self.message.Message.pollCreationMessage.name
        elif message_type == "media" and media_type != "sticker":
            match media_type:
                case "image":
                    return self.message.Message.imageMessage.caption
                case "video":
                    return self.message.Message.videoMessage.caption
                case "document":
                    return self.message.Message.documentMessage.caption
                case "livelocation":
                    return self.message.Message.liveLocationMessage.caption
        return ""

    def __extract_quoted_from_context_info(self, msg):
        if not msg.HasField("contextInfo"):
            return None
        cont_info = msg.contextInfo
        if not cont_info.HasField("quotedMessage"):
            return None
        qmsg = (
            cont_info.quotedMessage.viewOnceMessage.message
            if cont_info.quotedMessage.HasField("viewOnceMessage")
            else cont_info.quotedMessage
        )
        _type, text_or_cap, pushname = None, None, None
        if contact := self.c.contact.get_contact(
            self.string_to_jid(cont_info.participant)
        ):
            pushname = contact.PushName
        if qmsg.HasField("extendedTextMessage") or qmsg.HasField("conversation"):
            _type, text_or_cap = (
                "text",
                qmsg.conversation or qmsg.extendedTextMessage.text,
            )
        elif qmsg.HasField("imageMessage"):
            _type, text_or_cap = "image", qmsg.imageMessage.caption
        elif qmsg.HasField("videoMessage"):
            _type, text_or_cap = "video", qmsg.videoMessage.caption
        elif qmsg.HasField("documentMessage"):
            _type, text_or_cap = "document", qmsg.documentMessage.caption
        elif qmsg.HasField("liveLocationMessage"):
            _type, text_or_cap = "livelocation", qmsg.liveLocationMessage.caption
        elif qmsg.HasField("locationMessage"):
            _type = "location"
        elif qmsg.HasField("stickerMessage"):
            _type = "sticker"
        elif qmsg.HasField("audioMessage"):
            _type = "audio"
        return QuotedMessage(
            chat=cont_info.participant,
            pushname=pushname,
            text=text_or_cap,
            sender=cont_info.participant,
            message_id=cont_info.stanzaId,
            message_type=_type,
            is_media=_type not in ("text", "location", "livelocation"),
            media_type=_type,
            raw_message=qmsg,
        )

    def extract_quoted_message(self) -> QuotedMessage | None:
        smsg = self.simplified()
        if smsg.message_type == "text" or smsg.media_type == "url":
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
            elif self.message.Message.HasField("audioMessage"):
                return self.__extract_quoted_from_context_info(
                    self.message.Message.audioMessage
                )
            elif self.message.Message.HasField("locationMessage"):
                return self.__extract_quoted_from_context_info(
                    self.message.Message.locationMessage
                )
            elif self.message.Message.HasField("liveLocationMessage"):
                return self.__extract_quoted_from_context_info(
                    self.message.Message.liveLocationMessage
                )
        return None

    def __extract_mention(self) -> list[str]:
        smsg = self.simplified()
        msg = self.message.Message
        mentions = []
        if smsg.message_type == "text" or smsg.media_type == "url":
            if msg.HasField("extendedTextMessage") and msg.extendedTextMessage.HasField(
                "contextInfo"
            ):
                mentions = getattr(
                    msg.extendedTextMessage.contextInfo, "mentionedJid", []
                )
        elif smsg.message_type == "media" and smsg.media_type not in (
            "sticker",
            "location",
        ):
            if msg.HasField("imageMessage") and msg.imageMessage.HasField(
                "contextInfo"
            ):
                mentions = getattr(msg.imageMessage.contextInfo, "mentionedJid", [])
            elif msg.HasField("videoMessage") and msg.videoMessage.HasField(
                "contextInfo"
            ):
                mentions = getattr(msg.videoMessage.contextInfo, "mentionedJid", [])
            elif msg.HasField("documentMessage") and msg.documentMessage.HasField(
                "contextInfo"
            ):
                mentions = getattr(msg.documentMessage.contextInfo, "mentionedJid", [])
            elif msg.HasField(
                "liveLocationMessage"
            ) and msg.liveLocationMessage.HasField("contextInfo"):
                mentions = getattr(
                    msg.liveLocationMessage.contextInfo, "mentionedJid", []
                )
        return mentions


class HistoryMessage:
    def __init__(self, history: Neonize_pb2.HistorySync):
        self.history = history
        self.conversations = history.Data.conversations
        self.messages = []

    def _all_messages(self):
        for conversation in self.conversations:
            self.messages.extend(
                list(
                    filter(
                        lambda x: not x.message.messageStubType, conversation.messages
                    )
                )
            )
