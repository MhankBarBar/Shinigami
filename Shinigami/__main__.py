import logging
import signal
from datetime import datetime

from neonize.client import JID, NewClient
from neonize.events import (
    CallOfferEv,
    ConnectedEv,
    HistorySyncEv,
    MessageEv,
    PairStatusEv,
    ReceiptEv,
    event,
)
from neonize.proto.def_pb2 import DeviceProps
from neonize.utils import log  # , enum

from Shinigami.commands import CommandHandler, CommandLoader
from Shinigami.config import Config
from Shinigami.locales import i18n
from Shinigami.utils import is_windows
from Shinigami.utils.message import SimplifiedMessage  # HistoryMessage

if not is_windows():
    from Shinigami.ipc import sgiapi

command_handler = CommandHandler()
CommandLoader.load_commands(command_handler)


def interrupted(*_):
    event.set()


log.setLevel(logging.INFO)
signal.signal(signal.SIGINT, interrupted)

client = NewClient(
    str(Config.SESSION_DIR / Config.SESSION_NAME),
    DeviceProps(requireFullSync=True, os="Shinigami", platformType=DeviceProps.WEAR_OS),
)
_i18n = i18n(Config.LANGUAGE)


@client.event(ConnectedEv)
def on_connected(_: NewClient, __: ConnectedEv):
    log.info("⚡ Connected")
    if not is_windows():
        Config.send_update_config()

        def send_message(data: dict):
            client.send_message(JID(**data["chat"]), data["message"])

        def update_config(config: dict):
            Config.update_config(**config)

        sgiapi.set_handler("send_message", send_message)
        sgiapi.set_handler("update_config", update_config)
        sgiapi.start()


@client.event(ReceiptEv)
def on_receipt(_: NewClient, receipt: ReceiptEv):
    log.debug(f"Receipt: {receipt}")


@client.event(HistorySyncEv)
def on_history_sync(_: NewClient, history_sync: HistorySyncEv):
    log.debug(f"HistorySync: {history_sync}")
    # HistoryMessage(history_sync)


@client.event(CallOfferEv)
def on_call_offer(_: NewClient, call_offer: CallOfferEv):
    log.debug(f"CallOffer: {call_offer}")
    _.send_message(call_offer.basicCallMeta.callCreator, _i18n["main"]["on_call_offer"])
    # _.update_blocklist(call_offer.basicCallMeta.callCreator, enum.BlocklistAction.BLOCK)  # block contact caller


@client.event(MessageEv)
def on_message(c: NewClient, message: MessageEv):
    global _i18n
    _i18n = i18n(Config.LANGUAGE)
    smsg = SimplifiedMessage(c, message).simplified()
    if message.Info.Category == "peer" or smsg.chat == "status@broadcast":
        return
    time = datetime.fromtimestamp(int(str(smsg.timestamp)[:-3])).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    print(
        _i18n["main"]["on_message"].strip()
        % (time, smsg.pushname, smsg.text, smsg.message_type)
    )
    command_handler.handle_command(
        smsg.text,
        c=c,
        m=message,
        sm=smsg,
        i18n=_i18n,
        args=smsg.text.split(" ") if smsg.text else [],
    )


@client.event(PairStatusEv)
def pair_status(_: NewClient, message: PairStatusEv):
    log.info(f"logged as {message.ID.User}")


def start():
    client.connect()


if __name__ == "__main__":
    start()
