# from rich.repr import Foo
import asyncio
import signal
import os
import struct
from ptyprocess import PtyProcessUnicode
from pathlib import Path
from typing import Callable
from rich.text import Text
from textual import RenderableType, work
from textual.app import App, ComposeResult
from textual.validation import Function
from textual.widget import Widget
from textual.widgets import Button, Header, Footer, Input, Label, ListItem, ListView, Log, Select, Static, TabPane, TabbedContent, Tabs, Welcome, Tab
from textual.containers import Grid, Horizontal, VerticalScroll, Vertical
from textual.reactive import Reactive, reactive
import watchfiles
import os
import re
import socket
WORKDIR = Path(__file__).parent
SHINIGAMI = WORKDIR / 'Shinigami/'

# 7-bit C1 ANSI sequences
ansi_escape = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)


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
            Button("DEBUG: ✅", id="debug", variant="primary"),
            name="action_button"
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
        yield Grid(
            Log(id="log"),
            Log(id="status")
        )
class Session(Widget):
    BINDINGS = [('d', 'toggel_dark', "Toggle Dark Mode")]
    DEFAULT_CSS = """
ActionButton {
    dock: bottom;
    background: red;
    height: 3;
} 

"""
    DEBUG = False
    def compose(self) -> ComposeResult:
        # yield Content(layout)
        with TabbedContent():
            with TabPane("Home"):   
                with Vertical():
                    yield UILog()
                    yield ActionButton()
            with TabPane("Config"):
                with VerticalScroll(id="input_group"):
                        yield Input(placeholder="Bot Name")
                        yield Input(placeholder="Prefix")
                        yield Input(placeholder="Owner")
                        yield Input(placeholder="Session Name")
                        yield Input(placeholder="Sticker Pack")
                        yield Button("Apply", id="apply_config", variant="success")
            with TabPane("Session"):
                with VerticalScroll():
                    with Horizontal(classes="select_group"):
                        yield Select([('Shinigami','Shinigami')], name="Switch Session", allow_blank=False, prompt="Change Session")
                        yield Button("Switch", variant="success")
                    with Horizontal(classes="select_group"):
                        yield Select([('Shinigami', 'Shinigami')], name="Switch Session", allow_blank=False, prompt="Change Session")
                        yield Button("Delete", variant="error")
                    with Horizontal():
                        yield Button("Log Out", variant="error")
        # yield Vertical(
        # yield Footer()
        
    def action_toggle_dark(self) -> None:
        self.dark = not self.dark
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit_button":
            alert = self.app.query_one(Alert)
            al1=alert.query(Grid)
            al1[0].text = "Apakah Anda yakin"
            alert.refresh(layout=True)
            alert.styles.visibility = "visible"
            alert.on_yes(self.app.exit)
        elif event.button.id == "debug":
            self.DEBUG = not self.DEBUG
            # self.app.send_command("debug", int(self.DEBUG).__str__().encode())
            event.button.label = "DEBUG: %s" % ['❌ ','✅'][self.DEBUG]
        elif event.button.id == "restart":
            self.app.restart()
        # self.query_one(Content).walawe()

        # self.query_one(Log).write("hehe\na")
class AllSession(Widget):
    selected = Reactive("default", always_update=True)
    def compose(self) -> ComposeResult:
        yield SESSION[self.selected]

class Message(Widget):
    text = reactive("Are You Sure?")
    def render(self) -> RenderableType:
        return Text(self.text)

class Alert(Widget):
    DEFAULT_CSS = """
    #alert {
        grid-size: 1 2;
        border: heavy white;
    }
    #msg-alert {
    margin-top: 1;
    text-align: center;
    }
    Grid > Grid {
        grid-size: 2 1;
        align: center middle;
    }
    """
    def compose(self) -> ComposeResult:
        yield Grid(
                Message(id="msg-alert"),
                Grid(Button("No", variant="primary", id="no"), Button("Yes", "warning", id="yes")),
                id="alert"
            )
    def on_yes(self, cb: Callable):
        self.yes = cb
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "no":
            self.styles.visibility = "hidden"
        elif event.button.id == "yes":
            self.yes()


class CreateSessionModal(Widget):
    """
    Button {
        align: right;
    }
    #confirmation {
        background: cyan;
        width: 100%;
    }
    Label {
        text-align: right;
        width: auto;
        background: blue;
    }
    """
    def compose(self) -> ComposeResult:
        yield Label('x', id='close_label')
        yield Input(
            placeholder="session name",
            validators=[
                Function(lambda v: v not in SESSION, "session has been used")
            ]
        )
        yield Horizontal(
            Button("Cancel", id="hide_session"),
            # Button("Submit", id="submit_session"),
            id="confirmation"
        )
    def show(self):
        self.query_one(Input).clear()
        self.styles.visibility = "visible"


    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "hide_session":
            self.styles.visibility = "hidden"


    def on_input_submitted(self, event: Input.Submitted):
        global SESSION
        if event.input.is_valid:
            SESSION.update({event.input.value: Session()})
            self.app.query_one(ListView).append(ListItem(Label(event.input.value), id=event.input.value))
            self.styles.visibility = "hidden"
    
class Shinigami(App):
    BINDINGS = [("c", "sidebar()", 'Sidebar')]
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
    Alert {
        width: 40;
        background: $primary 30%; 
        layer: belowx;
        offset: 15 15;
        height: 10;
        visibility: hidden;
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
    def action_sidebar(self):
        q=self.query_one(ListView)
        if q.styles.width.value == 0:
            q.styles.visibility="visible"
            q.styles.animate('width', 30, duration=0.5)
        else:
            def on_complete():
                q.styles.visibility = "hidden"
                self.query_one(ListView).blur()
                # self.query_one(sel).focus()
            q.styles.animate('width', 0, duration=0.5, on_complete=on_complete)

    def on_list_view_selected(self, event: ListView.Selected):
        global SELECTED
        if event.item.id == "add_session":
            self.query_one(CreateSessionModal).show()
            self.query_one(CreateSessionModal).query_one(Input).focus()
        else:
            # self.push_screen(event.item.id.__str__())
            # self.query_one(AllSession).selected = SESSION[event.item.id]
            self.query_one(AllSession).refresh(layout=True)
            self.query_one(AllSession).refresh(layout=True)
        # self.query_one(ListView).append(ListItem(Label("Walawe")))

    @work(thread=True)
    def client(self, sock: socket.socket, addr):
        log=self.query_one('#log', expect_type=Log)
        with open('log.txt', 'w') as file:
            while True:
                try:
                    rdata = sock.recv(4)
                    command_size = struct.unpack('i',rdata)[0]
                    file.writelines('command_size: '+command_size.__str__())
                    command = sock.recv(command_size).decode()
                    file.writelines('command: '+command)
                    data_size = struct.unpack('i', sock.recv(4))[0]
                    file.writelines('data_size: '+data_size.__str__())
                    data = sock.recv(data_size)
                    file.write(f'data: '+data.decode())
                    if command == "restart":
                        self.pty.kill(signal.SIGKILL)
                        break
                except Exception as e:
                    log.write(f'Disconnected: {e} ')
                    break

    def send_command(self, name: str, data: bytes= b""):
        command_size = struct.pack('i',len(name))
        self.socks.send(command_size)
        self.socks.send(name.encode())
        data_size = struct.pack('i', len(data))
        self.socks.send(data_size)
        self.socks.send(data)

    @work(exclusive=True, name="file watcher")
    async def watchfiles(self):
        def file_filter(_: watchfiles.Change, filename: str):
            return filename.endswith('.py')
        async for _ in watchfiles.awatch(SHINIGAMI, watch_filter=file_filter, stop_event=self.watch_event):
            self.pty.kill(signal.SIGKILL)

    @work(thread=True)
    def server(self):
        sock_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_server.bind('listen.sock')
        sock_server.listen()
        while True:
            sock, addr = sock_server.accept()
            self.socks = sock
            self.client(sock, addr)

    @work(thread=True)
    def process(self):
        self.pty = PtyProcessUnicode.spawn(['poetry', 'run', 'shiniagmi'], cwd=Path(__file__).parent)
        log=self.query('Vertical > UILog > Grid > Log').first()
        while True:
            try:
                std = self.pty.read(1024)
                log.write(ansi_escape.sub('', std))
            except EOFError:
                self.pty = PtyProcessUnicode.spawn(['python', 'shell.py'])
    def restart(self):
        self.pty.kill(signal.SIGKILL)
    def on_mount(self):
        self.watch_event = asyncio.Event()
        log = self.query_one("#log", expect_type=Log)
        log.write("bjir")
        if self.DEBUG:
            self.watchfiles()
        pass
        # self.server()
        # self.process()
    def compose(self) -> ComposeResult:
        yield Header(True)
        # yield Alert()
        # yield CreateSessionModal()
        yield ListView(ListItem(Label(r"✏️  Create Session"), id="add_session"))
        yield Session()
        yield Footer()



if __name__ == '__main__':
    sock_file = Path(__file__).parent / 'listen.sock'
    if sock_file.exists():
        os.remove(sock_file)
    app = Shinigami()
    app.styles.layout = "vertical"
    app.run()