from environs import Env
from textual import on, work
from textual.app import App
from textual.containers import Container, VerticalScroll, Center
from textual.events import Resize
from textual.geometry import clamp
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Label, Footer, Button, Rule, Input

from src.db.hosts import HostsDb
from src.icmp_utils import Ping, PingResult
from src.widgets.ping_interval_display import PingIntervalDisplay
from src.widgets.pinger import Pinger

ENV = Env()
ENV.read_env("./.env")


class HostsPingScreen(Screen):
    BINDINGS = [
        ("a", "app.push_screen('add_host')", " - Add host"),
        ("c", "toggle_compact()", " - Toggle compact mode"),
        ("e", "handle_interval_change(1)", " - Interval ↑"),
        ("q", "handle_interval_change(-1)", " - Interval ↓")
    ]

    MIN_INTERVAL = ENV.int("MIN_INTERVAL")
    MAX_INTERVAL = ENV.int("MAX_INTERVAl")

    ping_interval = reactive(ENV.int("DEFAULT_PING_INTERVAL"))
    compact = reactive(False)

    def compose(self):
        with VerticalScroll(id="pingers"):
            pass
        yield Label("/ [blink][i]No hosts to ping[/][/] /", id="no-hosts")
        with Container(id="ping-interval-display-container"):
            yield PingIntervalDisplay(self.ping_interval)
        yield Footer()

    def action_toggle_compact(self):
        self.compact = not self.compact

    def action_handle_interval_change(self, delta: int):
        self.log.error(self.ping_interval)
        self.ping_interval += delta

    def validate_ping_interval(self, ping_interval: int):
        return clamp(ping_interval, self.MIN_INTERVAL, self.MAX_INTERVAL)

    def watch_ping_interval(self, old: int, new: int):
        if not self.is_mounted:
            return

        self.query_one(PingIntervalDisplay).interval = new
        for widget in self.query(Pinger):
            widget.interval = new

    def watch_compact(self):
        self.query(Pinger).set_class(self.compact, "compact")

    async def on_mount(self):
        db = HostsDb()
        hosts = await db.read_all()
        for host in hosts:
            self.query_one("#pingers").mount(Pinger(host["alias"], host["address"], self.ping_interval, host.doc_id))

        self.show_no_hosts()
        self.set_interval(1, self.show_no_hosts)

    def show_no_hosts(self):
        self.query_one("#no-hosts").display = len(self.query(Pinger)) == 0

    @work(exclusive=True)
    async def add_pinger(self, doc_id):
        db = HostsDb()
        host = await db.read_one(doc_id)
        self.query_one("#pingers").mount(Pinger(host["alias"], host["address"], self.ping_interval, host.doc_id))
        self.query(Pinger).set_class(self.compact, "compact")
        self.show_no_hosts()


class HostAddScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen()", " - Cancel"),
    ]

    class AddressChecked(Message):
        def __init__(self, result: PingResult):
            super().__init__()
            self.result = result

    class HostAdded(Message):
        def __init__(self, doc_id: int):
            super().__init__()
            self.doc_id = doc_id

    def compose(self):
        with Container(id="panel"):
            with Center():
                yield Label("Add a new host", id="header")
            yield Rule()
            with Center(id="inputs"):
                yield Input(placeholder="alias", id="alias")
                yield Input(placeholder="address / ip", id="address")
            with Container(id="buttons"):
                yield Button("Add", id="add")
                yield Button("Cancel", id="cancel")
        yield Footer()

    def on_mount(self):
        self.query_one("#add", Button).disabled = True

    @on(Button.Pressed, "#add")
    @on(Input.Submitted, "#inputs Input")
    def handle_add_host(self):
        address = self.query_one("#address", Input).value

        if address == "":
            self.notify(f"Specify the address", title="No address", severity="warning",
                        timeout=3)
            return

        self.query_one("#add", Button).disabled = True
        self.query(Input).set(disabled=True)

        self.notify("Checking the address...", title="Wait", severity="information", timeout=2)

        self.check_address(address)

    def on_button_pressed(self, event: Button.Pressed):
        match event.button.id:
            case "cancel":
                self.app.pop_screen()

    def on_input_changed(self, event: Input.Changed):
        match event.input.id:
            case "address":
                self.query_one("#add", Button).disabled = len(event.input.value) == 0

    def on_resize(self, event: Resize):
        width = event.size.width

        for widget in self.query("#buttons Button"):
            widget.set_class(width <= 70, "btn-vertical")
            widget.set_class(width > 70, "btn-horizontal")

    async def on_host_add_screen_address_checked(self, event: AddressChecked):
        event.stop()

        address = self.query_one("#address", Input).value
        alias = self.query_one("#alias", Input).value

        self.query_one("#add", Button).disabled = False
        self.query(Input).set(disabled=False)

        result = event.result

        if not result.resolved:
            self.notify(f"Address: [u]{address}[/] cannot be [b]resolved[/]", title="Unresolved", severity="error",
                        timeout=5)
            return

        if not result.is_alive:
            self.notify(f"Address: [u]{address}[/] is [b]unreachable[/]", title="Unreachable", severity="error",
                        timeout=5)
            return

        doc_id = await self.add_host(alias, address)

        self.post_message(self.HostAdded(doc_id))

        if alias != "":
            message = f"[u]{address}[/] as [b]{alias}[/] successfully added!"
        else:
            message = f"[u]{address}[/] successfully added!"

        self.notify(message, title="OK", severity="information", timeout=5)

        for widget in self.query(Input):
            widget.value = ""

    @work(exclusive=True)
    async def check_address(self, address: str):
        result = await Ping.send(address, 5)

        self.post_message(self.AddressChecked(result))

    async def add_host(self, alias: str, address: str):
        db = HostsDb()
        return await db.add_host(alias, address)


class HaveINet(App):
    TITLE = "HaveINet"
    SUB_TITLE = "Checks for the Internet connection"
    CSS_PATH = ENV.path("STYLE_PATH")
    SCREENS = {"ping_hosts": HostsPingScreen(), "add_host": HostAddScreen()}

    def on_mount(self):
        self.push_screen("ping_hosts")

    def on_host_add_screen_host_added(self, event: HostAddScreen.HostAdded):
        self.get_screen("ping_hosts").add_pinger(event.doc_id)


def main():
    app = HaveINet()
    app.run()


if __name__ == "__main__":
    main()
