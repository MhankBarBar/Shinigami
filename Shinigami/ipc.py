import json
import struct
import socket
from typing import Callable, Dict, Optional
from neonize.utils import log
from threading import Thread


class ShinigamiIPC:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.sock.connect("listen.sock")
        self.handler: Dict[str, Callable[[dict]]] = {}

    def default_handler(self, arg: str):
        log.debug(arg)

    def on_message(self, command: str, data: bytes):
        f = self.handler.get(command)
        data_json = json.loads(data)
        if f:
            f(data_json)
            log.debug(command, data_json)

        else:
            log.debug(f"{command} command not set on current handler")

    def set_handler(self, command: str, f: Callable[[dict], None]):
        self.handler.update({command: f})

    def get_data(self):
        while True:
            command_size = self.sock.recv(4)
            command = self.sock.recv(struct.unpack("i", command_size)[0])
            data_size = self.sock.recv(4)
            data = self.sock.recv(struct.unpack("i", data_size)[0])
            self.on_message(command.decode(), data)

    def send_commmand(self, name: str, message: Optional[dict] = None):
        log.debug(name, message)
        message_data = json.dumps(message or {}).encode()
        self.sock.send(struct.pack("i", len(name)))
        self.sock.send(name.encode())
        self.sock.send(struct.pack("i", len(message_data)))
        self.sock.send(message_data)

    def start(self):
        th = Thread(target=self.get_data, args=())
        th.setDaemon(True)
        th.start()


sgiapi = ShinigamiIPC()
