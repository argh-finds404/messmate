from unittest.mock import Mock

import pytest

from app.errors import NotFoundError, ValidationError
from app.models.member import Member
from app.services.member_service import MemberService


@pytest.fixture
def repo():
    repo = Mock()
    repo.find_by_phone.return_value = None
    repo.add.side_effect = lambda m: Member(m.name, m.room, m.phone, m.active, id=1)
    return repo


@pytest.fixture
def service(repo):
    return MemberService(repo)


def test_register_saves_valid_member(service, repo):
    member = service.register("Rafi", "101", "01711111111")
    assert member.id == 1
    repo.add.assert_called_once()
    saved = repo.add.call_args[0][0]
    assert saved.name == "Rafi" and saved.room == "101"


def test_register_strips_whitespace(service, repo):
    service.register("  Rafi  ", " 101 ", "01711111111")
    saved = repo.add.call_args[0][0]
    assert saved.name == "Rafi" and saved.room == "101"


@pytest.mark.parametrize(
    "name, room, phone, message",
    [
        ("", "101", "01711111111", "Name is required"),
        ("   ", "101", "01711111111", "Name is required"),
        ("Rafi", "", "01711111111", "Room is required"),
        ("Rafi", "101", "1711111111", "Phone must be 11 digits"),
        ("Rafi", "101", "0171111111", "Phone must be 11 digits"),
        ("Rafi", "101", "017111111111", "Phone must be 11 digits"),
        ("Rafi", "101", "0271111111a", "Phone must be 11 digits"),
    ],
)
def test_register_rejects_invalid_input(service, repo, name, room, phone, message):
    with pytest.raises(ValidationError, match=message):
        service.register(name, room, phone)
    repo.add.assert_not_called()


def test_register_rejects_duplicate_phone(service, repo):
    repo.find_by_phone.return_value = Member("Old", "102", "01711111111", id=5)
    with pytest.raises(ValidationError, match="Phone already registered"):
        service.register("Rafi", "101", "01711111111")
    repo.add.assert_not_called()


def test_get_raises_when_missing(service, repo):
    repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Member not found"):
        service.get(99)


def test_get_returns_member(service, repo):
    repo.get.return_value = Member("Rafi", "101", "01711111111", id=1)
    assert service.get(1).name == "Rafi"


def test_list_members_passes_filter_to_repo(service, repo):
    repo.list_all.return_value = []
    assert service.list_members(active_only=True) == []
    repo.list_all.assert_called_once_with(active_only=True)


def test_deactivate_missing_member_raises(service, repo):
    repo.get.return_value = None
    with pytest.raises(NotFoundError):
        service.deactivate(99)
    repo.set_active.assert_not_called()


def test_deactivate_marks_member_inactive(service, repo):
    repo.get.return_value = Member("Rafi", "101", "01711111111", id=1)
    service.deactivate(1)
    repo.set_active.assert_called_once_with(1, False)
