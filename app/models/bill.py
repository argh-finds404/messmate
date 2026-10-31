from dataclasses import dataclass


@dataclass
class BillLine:
    """Represents a single member's monthly bill line."""

    member_id: int
    name: str
    meals: int
    charge: float
