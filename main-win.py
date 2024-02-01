import asyncio
import os
import signal
from collections.abc import Callable
from multiprocessing.context import Process

import watchfiles
from winpty import PtyProcess as PtyProcessUnicode


class PtyProcess:
    def __init__(self, f: Callable[[bytes], None], command: list[str]):
        self.func = f
        self.command = command
        os.environ.update({"debug": "1"})
        self.pty = PtyProcessUnicode.spawn(
            command, cwd=os.path.dirname(__file__), env=os.environ
        )

    def on_message(self, m: bytes):
        self.func(m)

    @classmethod
    def start(cls, f, command):
        process = cls(f, command)
        while True:
            try:
                process.on_message(process.pty.read(1024))
            except EOFError:
                process = cls(process.func, process.command)


async def main(event: asyncio.Event):
    def create_pty():
        p = Process(
            target=PtyProcess.start, args=(print, ["python", "-m", "Shinigami"])
        )
        p.start()
        return p

    p = create_pty()

    def file_filter(_: watchfiles.Change, filename: str):
        return filename.endswith(".py")

    async for _ in watchfiles.awatch(
        os.path.dirname(__file__), watch_filter=file_filter, stop_event=event
    ):
        p.kill()
        p = create_pty()
    p.kill()


if __name__ == "__main__":
    event = asyncio.Event()
    signal.signal(signal.SIGINT, lambda *_: event.set())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(event))
