from unittest.mock import Mock, call

import pytest

from app.adapters.notifiers import NotificationError
from app.models.bill import BillLine
from app.models.member import Member
from app.services.notification_service import NotificationService

MEMBERS = {
    1: Member("Rafi", "101", "01711111111", id=1),
    3: Member("Tina", "103", "01733333333", id=3),
}
LINES = [
    BillLine(1, "Rafi", 10, 1000.0),
    BillLine(2, "Sami", 0, 0.0),
    BillLine(3, "Tina", 5, 500.0),
]


@pytest.fixture
def parts():
    member_repo, notifier = Mock(), Mock()
    member_repo.get.side_effect = lambda member_id: MEMBERS.get(member_id)
    return NotificationService(member_repo, notifier), member_repo, notifier


def test_sends_a_notice_to_each_member_who_owes(parts):
    service, _, notifier = parts
    sent = service.send_bill_notices("2026-10", LINES)
    assert sent == 2
    assert notifier.send.call_args_list == [
        call("01711111111", "Dear Rafi, your mess bill for 2026-10 is 1000.00 BDT."),
        call("01733333333", "Dear Tina, your mess bill for 2026-10 is 500.00 BDT."),
    ]


def test_members_with_zero_charge_get_no_notice(parts):
    service, member_repo, _ = parts
    service.send_bill_notices("2026-10", LINES)
    assert call(2) not in member_repo.get.call_args_list


def test_one_failed_message_does_not_stop_the_rest(parts):
    service, _, notifier = parts
    notifier.send.side_effect = [NotificationError("down"), None]
    assert service.send_bill_notices("2026-10", LINES) == 1
    assert notifier.send.call_count == 2


def test_missing_member_is_skipped(parts):
    service, member_repo, notifier = parts
    member_repo.get.side_effect = lambda member_id: None
    assert service.send_bill_notices("2026-10", LINES) == 0
    notifier.send.assert_not_called()
