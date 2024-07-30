import icmplib as icmp


class Ping:
    @staticmethod
    async def send(address: str, timeout: int | float):
        try:
            return PingResult(await icmp.async_ping(address, 1, timeout=timeout), True)

        except icmp.NameLookupError:
            return PingResult(None, False)


class PingResult:
    def __init__(self, host: icmp.Host | None, resolved: bool):
        self.resolved = resolved
        self.rtt = host.avg_rtt if host else float("inf")
        self.is_alive = host.is_alive if host else False
        self.ip = host.address if host else "Unknown"
