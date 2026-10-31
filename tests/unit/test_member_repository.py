from app.models.member import Member
from app.repositories.member_repository import MemberRepository


def test_add_assigns_id_and_persists(conn):
    repo = MemberRepository(conn)
    saved = repo.add(Member("Rafi", "101", "01711111111"))
    assert saved.id is not None
    assert repo.get(saved.id).name == "Rafi"


def test_get_returns_none_when_missing(conn):
    assert MemberRepository(conn).get(42) is None


def test_find_by_phone(conn):
    repo = MemberRepository(conn)
    repo.add(Member("Rafi", "101", "01711111111"))
    assert repo.find_by_phone("01711111111").name == "Rafi"
    assert repo.find_by_phone("01800000000") is None


def test_list_all_and_active_only(conn):
    repo = MemberRepository(conn)
    repo.add(Member("Rafi", "101", "01711111111"))
    second = repo.add(Member("Sami", "102", "01722222222"))
    repo.set_active(second.id, False)
    assert [m.name for m in repo.list_all()] == ["Rafi", "Sami"]
    assert [m.name for m in repo.list_all(active_only=True)] == ["Rafi"]


def test_active_is_a_real_bool(conn):
    repo = MemberRepository(conn)
    saved = repo.add(Member("Rafi", "101", "01711111111"))
    assert repo.get(saved.id).active is True
    repo.set_active(saved.id, False)
    assert repo.get(saved.id).active is False
