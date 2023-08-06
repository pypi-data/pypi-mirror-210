from dataclasses import dataclass
from typing import Any


@dataclass
class Event:
    """
    Event dataclass
    """

    channel: str
    payload: Any

    def __eq__(self, event: "Event") -> bool:
        return all(
            [
                isinstance(event, Event),
                self.channel == event.channel,
                self.payload == event.payload,
            ]
        )

    def __repr__(self) -> str:
        return f"Event({self.channel=},{self.payload=})"
