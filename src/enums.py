from enum import StrEnum


class HostState(StrEnum):
    WAIT = "Wait"
    NOT_RESOLVED = "Not Resolved"
    UNREACHABLE = "Unreachable"
    OK = "OK"


class HostIcon(StrEnum):
    WAIT = "▢"
    NOT_RESOLVED = "▼"
    UNREACHABLE = "◆"
    OK = "●"
