from app.models.member import Member
from app.repositories.meal_repository import MealRepository
from app.repositories.member_repository import MemberRepository


def make_member(conn, phone="01711111111"):
    return MemberRepository(conn).add(Member("Rafi", "101", phone))


def test_set_meals_inserts_new_entry(conn):
    member = make_member(conn)
    repo = MealRepository(conn)
    saved = repo.set_meals(member.id, "2026-10-01", 2)
    assert saved.meal_count == 2
    assert repo.get(member.id, "2026-10-01").meal_count == 2


def test_set_meals_overwrites_same_day(conn):
    member = make_member(conn)
    repo = MealRepository(conn)
    repo.set_meals(member.id, "2026-10-01", 2)
    repo.set_meals(member.id, "2026-10-01", 3)
    assert repo.get(member.id, "2026-10-01").meal_count == 3
    assert len(repo.list_for_month("2026-10")) == 1


def test_get_returns_none_when_no_entry(conn):
    member = make_member(conn)
    assert MealRepository(conn).get(member.id, "2026-10-01") is None


def test_list_for_month_is_ordered_and_filtered(conn):
    member = make_member(conn)
    repo = MealRepository(conn)
    repo.set_meals(member.id, "2026-10-02", 1)
    repo.set_meals(member.id, "2026-10-01", 2)
    repo.set_meals(member.id, "2026-11-01", 3)
    assert [e.meal_date for e in repo.list_for_month("2026-10")] == ["2026-10-01", "2026-10-02"]


def test_month_totals_sums_per_member_and_ignores_other_months(conn):
    first = make_member(conn, "01711111111")
    second = make_member(conn, "01722222222")
    repo = MealRepository(conn)
    repo.set_meals(first.id, "2026-10-01", 2)
    repo.set_meals(first.id, "2026-10-02", 3)
    repo.set_meals(second.id, "2026-10-01", 1)
    repo.set_meals(first.id, "2026-11-01", 3)
    assert repo.month_totals("2026-10") == {first.id: 5, second.id: 1}
