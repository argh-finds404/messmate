from dataclasses import dataclass


@dataclass
class Member:
    """Represents a registered mess member."""

    name: str
    room: str
    phone: str
    active: bool = True
    id: int | None = None
