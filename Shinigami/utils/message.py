from dataclasses import dataclass
from typing import Callable

from neonize.proto import Neonize_pb2
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
    get_mention: Callable
    media_type: str = None


class SimplifiedMessage:

    def __init__(self, c, message):
        self.c = c
        self.message = message

    def simplified(self) -> Message:
        info = self.message.Info
        return Message(
            chat=self.jid_to_string(info.MessageSource.Chat),
            pushname=info.Pushname,
            message=self.extract_text(),
            sender=self.jid_to_string(info.MessageSource.Sender),
            timestamp=info.Timestamp,
            message_id=info.ID,
            message_type=info.Type,
            is_media=info.Type == "media",
            is_group=info.MessageSource.IsGroup,
            is_edit=self.message.IsEdit,
            quoted_message=self.extract_quoted_message,
            get_mention=self.__extract_mention,
            media_type=info.MediaType if info.Type == "media" else None,
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

    def __extract_quoted_from_context_info(self, msg):
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
                    chat=cont_info.participant,
                    pushname=pushname,
                    message=text_or_cap,
                    sender=cont_info.participant,
                    message_id=cont_info.stanzaId,
                    message_type=_type,
                    is_media=_type is not None and _type != "text",
                    media_type=_type,
                    raw_message=qmsg
                )
        else:
            return None

    def extract_quoted_message(self) -> QuotedMessage | None:
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
            else:
                return None
        return None

    def __extract_mention(self) -> list[str]:
        smsg = self.simplified()
        mentions = []
        if smsg.message_type == "text":
            if self.message.Message.HasField("extendedTextMessage"):
                if not self.message.Message.extendedTextMessage.HasField("contextInfo"):
                    return mentions
                if x := getattr(self.message.Message.extendedTextMessage.contextInfo, "mentionedJid", []):
                    mentions = x
        elif smsg.message_type == "media" and smsg.media_type != "sticker":
            if self.message.Message.HasField("imageMessage"):
                if not self.message.Message.imageMessage.HasField("contextInfo"):
                    return mentions
                if x := getattr(self.message.Message.imageMessage.contextInfo, "mentionedJid", []):
                    mentions = x
            elif self.message.Message.HasField("videoMessage"):
                if not self.message.Message.videoMessage.HasField("contextInfo"):
                    return mentions
                if x := getattr(self.message.Message.videoMessage.contextInfo, "mentionedJid", []):
                    mentions = x
            elif self.message.Message.HasField("documentMessage"):
                if not self.message.Message.documentMessage.HasField("contextInfo"):
                    return mentions
                if x := getattr(self.message.Message.documentMessage.contextInfo, "mentionedJid", []):
                    mentions = x
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
                    filter(lambda x: not x.message.messageStubType, conversation.messages)
                )
            )
