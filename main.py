import logging
import signal

from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv, PairStatusEv, event, ReceiptEv
from neonize.utils import log


from Shinigami.utils.message import SimplifiedMessage
from Shinigami.commands import CommandHandler, CommandLoader

command_handler = CommandHandler()
CommandLoader.load_commands(command_handler)


def interrupted(*_):
    event.set()


log.setLevel(logging.INFO)
signal.signal(signal.SIGINT, interrupted)

client = NewClient("joydazo.db")


@client.event(ConnectedEv)
def on_connected(_: NewClient, __: ConnectedEv):
    log.info("⚡ Connected")


@client.event(ReceiptEv)
def on_receipt(_: NewClient, receipt: ReceiptEv):
    log.debug(f"Receipt: {receipt}")


@client.event(MessageEv)
def on_message(c: NewClient, message: MessageEv):
    simplified_message = SimplifiedMessage(message).simplified()
    log.info(f"Message from {simplified_message.pushname} : {simplified_message.message} - {simplified_message.message_type}")
    command_handler.handle_command(
        simplified_message.message,
        c=c,
        m=message,
        sm=simplified_message
    )


@client.event(PairStatusEv)
def pair_status(_: NewClient, message: PairStatusEv):
    log.info(f"logged as {message.ID.User}")


client.connect()
