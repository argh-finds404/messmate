from dataclasses import dataclass


@dataclass
class Payment:
    """Represents a recorded wallet payment for a member and month."""

    member_id: int
    month: str
    amount: float
    reference: str
    id: int | None = None
