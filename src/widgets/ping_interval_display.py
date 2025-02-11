from textual.reactive import reactive
from textual.widgets import Static


class PingIntervalDisplay(Static):
    interval = reactive(0, layout=True)

    def __init__(self, interval):
        super().__init__()
        self.interval = interval

    def render(self):
        return f"⇅ {self.interval:>2}s"
