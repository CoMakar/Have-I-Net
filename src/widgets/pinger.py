from textual import work
from textual.containers import Horizontal
from textual.events import Resize
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static, Label, Button

from src.db.hosts import HostsDb
from src.enums import HostIcon, HostState
from src.icmp_utils import PingResult, Ping


class PingDisplay(Static):
    ping = reactive(0)

    def render(self):
        return f"{self.ping:.1f} ms"

    def fetch(self, ping: float):
        self.ping = ping


class IconDisplay(Static):
    icon = reactive(HostIcon.WAIT)

    def render(self):
        return f"{self.icon}"

    def fetch(self, result: PingResult):
        if not result.resolved:
            self.icon = HostIcon.NOT_RESOLVED
            return

        if not result.is_alive:
            self.icon = HostIcon.UNREACHABLE
        else:
            self.icon = HostIcon.OK


class ResolvedAs(Static):
    ip = reactive("?.?.?.?")

    def render(self):
        return f"⤳ [u]{self.ip}[/]"

    def fetch(self, result: PingResult):
        if not result.resolved:
            self.ip = "?.?.?.?"
            return

        self.ip = result.ip


class StatusDisplay(Static):
    status = reactive(HostState.WAIT)

    def render(self):
        return f"[ {self.status} ]"

    def fetch(self, result: PingResult):
        if not result.resolved:
            self.status = HostState.NOT_RESOLVED
            return

        if not result.is_alive:
            self.status = HostState.UNREACHABLE
            return

        self.status = HostState.OK


class Pinger(Static):
    BEST_PING = 128
    GOOD_PING = 256
    BAD_PING = 512

    interval = reactive(0)

    class Echoed(Message):
        def __init__(self, result: PingResult):
            super().__init__()
            self.result = result

    def __init__(self, alias: str, address: str, interval: int, db_id: int):
        super().__init__()
        self.alias = alias
        self.address = address
        self.interval = interval
        self.db_id = db_id

    def compose(self):
        with Horizontal():
            with Horizontal(id="data-layout"):
                yield IconDisplay()
                yield Label(self.alias, id="alias")
                yield Label(self.address, id="address")
                yield ResolvedAs()
                yield PingDisplay()
                yield StatusDisplay()
            yield Button("⨯", id="delete")

    def on_mount(self):
        self.set_timer(self.interval, self.send_ping)
        self.query_one(PingDisplay).visible = False

    def on_button_pressed(self, event: Button.Pressed):
        match event.button.id:
            case "delete":
                self.delete()

    @work(exclusive=True)
    async def delete(self):
        db = HostsDb()
        await db.remove(self.db_id)
        self.remove()

    def on_resize(self, event: Resize):
        width = event.size.width

        self.query_one(StatusDisplay).display = width > 110
        self.query_one(ResolvedAs).display = width > 90
        self.query_one("#alias").display = width > 60

    def on_pinger_echoed(self, event: Echoed):
        event.stop()

        result = event.result

        self.query_one(IconDisplay).fetch(result)
        self.query_one(ResolvedAs).fetch(result)
        self.query_one(StatusDisplay).fetch(result)

        self.set_class(not result.resolved, "unresolved")
        self.set_class(result.resolved, "resolved")
        self.query_one(PingDisplay).visible = result.resolved
        if not result.resolved:
            return

        self.set_class(not result.is_alive, "not-alive")
        self.set_class(result.is_alive, "alive")
        self.query_one(PingDisplay).visible = result.is_alive
        if not result.is_alive:
            return

        self.query_one(PingDisplay).fetch(result.rtt)
        rtt = round(result.rtt)

        self.add_class("alive")
        self.set_class(rtt in range(self.BEST_PING), "best")
        self.set_class(rtt in range(self.BEST_PING, self.GOOD_PING), "good")
        self.set_class(rtt in range(self.GOOD_PING, self.BAD_PING), "bad")
        self.set_class(rtt > self.BAD_PING, "worst")

    @work(exclusive=True)
    async def send_ping(self):
        result = await Ping.send(self.address, self.interval)

        self.set_timer(self.interval, self.send_ping)
        self.post_message(self.Echoed(result))

    def adjust_ping_interval(self, interval: int):
        self.interval = interval
