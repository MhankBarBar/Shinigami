import logging
import signal
from datetime import datetime

from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv, PairStatusEv, event, ReceiptEv, HistorySyncEv
from neonize.proto.def_pb2 import DeviceProps
from neonize.utils import log

from Shinigami.commands import CommandHandler, CommandLoader
from Shinigami.config import SESSION_NAME
from Shinigami.utils.message import SimplifiedMessage  # HistoryMessage

command_handler = CommandHandler()
CommandLoader.load_commands(command_handler)


def interrupted(*_):
    event.set()


log.setLevel(logging.INFO)
signal.signal(signal.SIGINT, interrupted)

client = NewClient(SESSION_NAME, DeviceProps(requireFullSync=True, os="Shinigami", platformType=DeviceProps.WEAR_OS))


@client.event(ConnectedEv)
def on_connected(_: NewClient, __: ConnectedEv):
    log.info("⚡ Connected")


@client.event(ReceiptEv)
def on_receipt(_: NewClient, receipt: ReceiptEv):
    log.debug(f"Receipt: {receipt}")


@client.event(HistorySyncEv)
def on_history_sync(_: NewClient, history_sync: HistorySyncEv):
    log.debug(f"HistorySync: {history_sync}")
    # HistoryMessage(history_sync)


@client.event(MessageEv)
def on_message(c: NewClient, message: MessageEv):
    smsg = SimplifiedMessage(c, message).simplified()
    if message.Info.Category == "peer":
        return
    if smsg.chat == "status@broadcast":
        return
    time = datetime.fromtimestamp(int(str(smsg.timestamp)[:-3])).strftime("%Y-%m-%d %H:%M:%S")
    print(message)
    print(f"{time} - Message from {smsg.pushname} : {smsg.message} - {smsg.message_type}")
    command_handler.handle_command(
        smsg.message,
        c=c,
        m=message,
        sm=smsg
    )


@client.event(PairStatusEv)
def pair_status(_: NewClient, message: PairStatusEv):
    log.info(f"logged as {message.ID.User}")


def start():
    client.connect()


if __name__ == "__main__":
    start()
