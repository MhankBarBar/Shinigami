import asyncio
import json
import os
import re
import signal
import socket
import struct
from pathlib import Path
from typing import Optional

import watchfiles
from ptyprocess import PtyProcessUnicode as PtyProcess
from rich.text import Text
from textual import RenderableType, work
from textual.app import App, ComposeResult
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.reactive import Reactive, reactive
from textual.screen import ModalScreen, Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Log,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

WORKDIR = Path(__file__).parent
SHINIGAMI = WORKDIR / "Shinigami/"

ansi_escape = re.compile(
    r"""
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
""",
    re.VERBOSE,
)


class ActionButton(Widget):
    DEFAULT_CSS = """
    Grid {
        grid-size: 3 1;
    }
    Grid > Button {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Grid(
            Button("Exit ⚠️", id="exit_button", variant="error"),
            Button("Restart 🔁", variant="warning", id="restart"),
            Button("DEBUG: ❌", id="debug", variant="primary"),
            name="action_button",
        )


class UILog(Widget):
    DEFAULT_CSS = """
    Grid {
        grid-size: 2 1;
    }
    Grid > Log {
        border: cyan;
        margin: 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Grid(Log(id="log"), Log(id="status"))


class Session(Widget):
    BINDINGS = [("d", "toggel_dark", "Toggle Dark Mode")]
    DEFAULT_CSS = """
ActionButton {
    dock: bottom;
    background: red;
    height: 3;
}

"""
    DEBUG = False
    SESSION_FILES = Reactive([], always_update=True, layout=True)
    switch_session = Select([], id="switch_session")
    delete_session = Select([], id="delete_session")

    @work(exclusive=True)
    async def session_watcher(self):
        def get_session():
            result = []
            for name in os.listdir(SHINIGAMI / "session"):
                result.append((name, name))
            self.switch_session.set_options(result)
            self.delete_session.set_options(result)

        get_session()
        async for changes in watchfiles.awatch(SHINIGAMI / "session"):
            for change in changes:
                match change[0]:
                    case watchfiles.Change.added:
                        get_session()
                    case watchfiles.Change.deleted:
                        get_session()

    def on_mount(self):
        self.session_watcher()
        # pass

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Home"):
                with Vertical():
                    yield UILog()
                    yield ActionButton()
            with TabPane("Config"):
                with VerticalScroll(id="input_group"):
                    yield Input(placeholder="Bot Name", id="bot_name")
                    yield Input(placeholder="Prefix", id="prefix")
                    yield Input(placeholder="Owner", id="owner")
                    yield Input(placeholder="Session Name", id="session_name")
                    yield Input(placeholder="Sticker Name", id="sticker_name")
                    yield Input(placeholder="Sticker Pack", id="sticker_pack")
                    yield Input(placeholder="CharacterAI Token", id="characterai_token")
                    yield Input(
                        placeholder="CharacterAI Character", id="characterai_character"
                    )
                    yield Input(placeholder="Language", id="language")
                    yield Button("Apply", id="apply_config", variant="success")
            with TabPane("Session"):
                with VerticalScroll():
                    with Horizontal(classes="select_group"):
                        yield self.switch_session
                        yield Button("Switch", variant="success", id="switch")
                    with Horizontal(classes="select_group"):
                        yield self.delete_session
                        yield Button(
                            "Delete", variant="error", id="selete_session_submit"
                        )
                    with Horizontal():
                        yield Button("Log Out", variant="error")

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit_button":
            self.app.push_screen(QuitScreen())
        elif event.button.id == "debug":
            self.DEBUG = not self.DEBUG
            if self.DEBUG:
                self.screen.watchfiles()
            else:
                self.screen.watch_event.set()
            # self.app.send_command("debug", int(self.DEBUG).__str__().encode())\
            # self.app.push_screen(QuitScreen())
            event.button.label = "DEBUG: %s" % ["❌", "✅"][self.DEBUG]
        elif event.button.id == "restart":
            self.screen.restart()
        elif event.button.id == "switch":
            # Not Implemented yet
            pass
        elif event.button.id == "apply_config":
            self.screen.send_command(
                "update_config",
                {
                    "bot_name": self.query_one("#bot_name", expect_type=Input).value,
                    "prefix": self.query_one("#prefix", expect_type=Input).value,
                    "owner": self.query_one("#owner", expect_type=Input).value,
                    "session_name": self.query_one(
                        "#session_name", expect_type=Input
                    ).value,
                    "sticker_name": self.query_one(
                        "#sticker_name", expect_type=Input
                    ).value,
                    "sticker_pack": self.query_one(
                        "#sticker_pack", expect_type=Input
                    ).value,
                    "characterai_token": self.query_one(
                        "#characterai_token", expect_type=Input
                    ).value,
                    "characterai_character": self.query_one(
                        "#characterai_character", expect_type=Input
                    ),
                    "language": self.query_one("#language", expect_type=Input).value,
                },
            )
        elif event.button.id == "selete_session_submit":
            os.remove(
                SHINIGAMI
                / (
                    "session/"
                    + self.query_one("#delete_session", expect_type=Select).value
                )
            )
        # self.query_one(Content).walawe()


class QuitScreen(ModalScreen):
    """Screen with a dialog to quit."""

    DEFAULT_CSS = """
    Grid > Grid {
        grid-size: 2 1;
    }
    Button {
        width: 100%;
    }
    #dialog {
    grid-size: 2;
    grid-gutter: 1 2;
    grid-rows: 1fr 3;
    padding: 0 1;
    width: 60;
    height: 11;
    border: thick $background 80%;
    background: $surface;
	align: center middle;
}
#question {
    column-span: 2;
    height: 1fr;
    width: 1fr;
    content-align: center middle;
}
    """

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            Button("Quit", variant="error", id="quit"),
            Button("Cancel", variant="success", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()


class Hit(Static):
    hit_name: reactive[str] = reactive("", always_update=True)
    hit_value: reactive[int] = reactive(0, always_update=True)

    def render(self) -> RenderableType:
        return Text(f"{self.hit_name}: {self.hit_value}", overflow="ignore")


class MyScreen(Screen):
    BINDINGS = [("c", "sidebar()", "Sidebar")]
    DEFAULT_CSS = """
    Screen {
        layers: below belowx session;
    }
    TabbedContent > TabPane > Session {
        layer: session;
    }
    ListView {
        dock: left;
        width: 0;
        border: white;
        height:100%;
        layer: below;
        visibility: hidden;
    }
    ListView > ListItem {
        background: $boost;
        padding-left: 1;
    }
    #Alert {
        width: 40;
        background: $primary 30%;
        layer: belowx;
        align: center middle;
        height: 10;
    }
    CreateSessionModal {
        layer: session;
        max-width: 50%;
        height: 6;
        offset: 10 10;
    }
    #apply_config {
        width: 100%;
    }
    .select_group {
        height: 5;
    }
    #ab {
        dock: bottom;
    }
    """
    DEBUG = False
    RESTARTED: dict[str, str | int | bool] | None = None

    def action_sidebar(self):
        q = self.query_one(ListView)
        if q.styles.width.value == 0:
            q.styles.visibility = "visible"
            q.styles.animate("width", 30, duration=0.5)
        else:

            def on_complete():
                q.styles.visibility = "hidden"
                self.query_one(ListView).blur()

            q.styles.animate("width", 0, duration=0.5, on_complete=on_complete)
        self.query_one(Session).SESSION_FILES = [("a", "b")]

    def on_list_view_selected(self, event: ListView.Selected):
        global SELECTED
        if event.item.id == "add_session":
            ListItem(Static(Text("yah")))
        else:
            pass

    @work(name="shinigami server", exclusive=True, thread=True, exit_on_error=True)
    def client(self, sock: socket.socket, addr):
        log = self.query_one("#log", expect_type=Log)
        hit = {}
        view = self.screen.query_one("#listview_hit", expect_type=ListView)
        if self.RESTARTED:
            self.RESTARTED.update({"message": "Restarted!"})
            self.send_command("send_message", self.RESTARTED)
            self.RESTARTED = None
        while True:
            try:
                rdata = sock.recv(4)
                command_size = struct.unpack("i", rdata)[0]
                command = sock.recv(command_size).decode()
                data_size = struct.unpack("i", sock.recv(4))[0]
                data = json.loads(sock.recv(data_size))
                log.write_line(f"parent: {command}, {data}")
                match command:
                    case "restart":
                        log.write_line("Restarting....")
                        self.RESTARTED = data
                        self.pty.kill(signal.SIGKILL)
                        break
                    case "update_config":
                        for k, v in data.items():
                            self.query_one(f"#{k}", expect_type=Input).value = v
                    case "hit":
                        name = data["name"]
                        if hit.get(name) is None:
                            hit[name] = 1
                            n_hit = Hit(id="hit_" + name)
                            n_hit.hit_name = name
                            n_hit.hit_value = hit[name]
                            self.app.call_from_thread(view.append, ListItem(n_hit))
                        else:
                            hit[name] += 1
                            self.app.query_one(
                                f"#hit_{name}", expect_type=Hit
                            ).hit_value = hit[name]

            except Exception as e:
                log.write_line(f"Disconnected: {e} ")
                break

    def send_command(self, name: str, data: Optional[dict] = None):
        json_data = json.dumps(data or {}).encode()
        command_size = struct.pack("i", len(name))
        self.socks.send(command_size)
        self.socks.send(name.encode())
        data_size = struct.pack("i", len(json_data))
        self.socks.send(data_size)
        self.socks.send(json_data)

    @work(exclusive=True, name="file watcher")
    async def watchfiles(self):
        if self.watch_event.is_set():
            self.watch_event = asyncio.Event()

        def file_filter(_: watchfiles.Change, filename: str):
            return filename.endswith(".py")

        async for _ in watchfiles.awatch(
            SHINIGAMI, watch_filter=file_filter, stop_event=self.watch_event
        ):
            self.pty.kill(signal.SIGKILL)

    @work(thread=True, exclusive=True)
    def server(self):
        sock_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_server.bind("listen.sock")
        sock_server.listen()
        while True:
            sock, addr = sock_server.accept()
            self.socks = sock
            self.client(sock, addr)

    @work(thread=True)
    def process(self):
        self.pty = PtyProcess.spawn(
            ["python", "-m", "Shinigami"],
            cwd=str(Path(__file__).parent),
            env=os.environ,
        )
        log = self.app.query_one("#log", expect_type=Log)
        while True:
            try:
                std = self.pty.read(1024)
                log.write(ansi_escape.sub("", std))
            except EOFError:
                self.pty = PtyProcess.spawn(
                    ["python", "-m", "Shinigami"],
                    cwd=str(Path(__file__).parent),
                    env=os.environ,
                )

    def restart(self):
        self.pty.kill(signal.SIGKILL)

    def on_mount(self):
        self.watch_event = asyncio.Event()
        if self.DEBUG:
            self.watchfiles()
        self.server()
        self.process()

    def compose(self) -> ComposeResult:
        yield Header(True)
        yield ListView(id="listview_hit")
        yield Session()
        yield Footer()


class Shinigami(App):
    DEFAULT_CSS = """

    QuitScreen{
        align: center middle;
    }
    """

    def on_mount(self):
        self.install_screen(MyScreen(), "HOME")
        self.push_screen("HOME")


if __name__ == "__main__":
    sock_file = Path(__file__).parent / "listen.sock"
    if sock_file.exists():
        os.remove(sock_file)
    app = Shinigami()
    app.styles.layout = "vertical"
    app.run()
