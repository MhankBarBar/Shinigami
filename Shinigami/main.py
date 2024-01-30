import json
import logging
import signal
from datetime import datetime

from neonize.client import JID, NewClient
from neonize.events import (
    ConnectedEv,
    MessageEv,
    PairStatusEv,
    event,
    ReceiptEv,
    HistorySyncEv,
    CallOfferEv,
)
from neonize.proto.def_pb2 import DeviceProps
from neonize.utils import log  # , enum
from .ipc import sgiapi
from Shinigami.commands import CommandHandler, CommandLoader
from Shinigami.config import Config
from Shinigami.utils.message import SimplifiedMessage  # HistoryMessage

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


@client.event(ConnectedEv)
def on_connected(_: NewClient, __: ConnectedEv):
    log.info("⚡ Connected")
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
    _.send_message(
        call_offer.basicCallMeta.callCreator, "I'm a bot and I don't accept calls"
    )
    # _.update_blocklist(call_offer.basicCallMeta.callCreator, enum.BlocklistAction.BLOCK)  # block contact caller


@client.event(MessageEv)
def on_message(c: NewClient, message: MessageEv):
    smsg = SimplifiedMessage(c, message).simplified()
    if message.Info.Category == "peer" or smsg.chat == "status@broadcast":
        return
    time = datetime.fromtimestamp(int(str(smsg.timestamp)[:-3])).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    print(f"{time} - Message from {smsg.pushname} : {smsg.text} - {smsg.message_type}")
    command_handler.handle_command(smsg.text, c=c, m=message, sm=smsg)


@client.event(PairStatusEv)
def pair_status(_: NewClient, message: PairStatusEv):
    log.info(f"logged as {message.ID.User}")


def start():
    client.connect()


if __name__ == "__main__":
    start()
