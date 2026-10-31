import re

from app.errors import NotFoundError, ValidationError
from app.models.member import Member
from app.repositories.member_repository import MemberRepository


class MemberService:
    """Business logic and validation for managing mess members."""

    def __init__(self, member_repo: MemberRepository) -> None:
        self.member_repo = member_repo

    def register(self, name: str, room: str, phone: str) -> Member:
        """Validate input and register a new active member."""
        name = name.strip()
        room = room.strip()
        if not name:
            raise ValidationError("Name is required")
        if not room:
            raise ValidationError("Room is required")
        if not re.fullmatch(r"01\d{9}", phone):
            raise ValidationError("Phone must be 11 digits starting with 01")
        if self.member_repo.find_by_phone(phone) is not None:
            raise ValidationError("Phone already registered")
        return self.member_repo.add(Member(name, room, phone))

    def get(self, member_id: int) -> Member:
        """Return a member by id or raise NotFoundError."""
        member = self.member_repo.get(member_id)
        if member is None:
            raise NotFoundError("Member not found")
        return member

    def list_members(self, active_only: bool = False) -> list[Member]:
        """Return all members, or only active members when active_only is True."""
        return self.member_repo.list_all(active_only=active_only)

    def deactivate(self, member_id: int) -> None:
        """Mark an existing member as inactive."""
        self.get(member_id)
        self.member_repo.set_active(member_id, False)
