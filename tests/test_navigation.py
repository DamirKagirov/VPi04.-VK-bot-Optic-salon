import pytest

from app import navigation
from app.navigation import Action, parse_action


def P(kind, service_id=None):
    return Action(kind, service_id, source="payload")


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"command": "start"}, Action(navigation.START, source="start")),
        ({"v": 1, "a": "menu"}, P(navigation.MENU)),
        ({"v": 1, "a": "list"}, P(navigation.LIST)),
        ({"v": 1, "a": "price"}, P(navigation.PRICE)),
        ({"v": 1, "a": "mgr"}, P(navigation.MANAGER)),
        ({"v": 1, "a": "mgr_ack"}, P(navigation.MANAGER_ACK)),
        ({"v": 1, "a": "svc", "id": "lens_refit"}, P(navigation.SERVICE, "lens_refit")),
        ({"v": 1, "a": "svc"}, P(navigation.STALE)),
        ({"v": 1, "a": "old"}, P(navigation.STALE)),
        ({"v": 1, "a": []}, P(navigation.STALE)),
        ({"v": 1, "a": {"x": 1}}, P(navigation.STALE)),
        ({"v": 2, "a": "menu"}, P(navigation.STALE)),
        ({"a": "menu"}, P(navigation.STALE)),
        ("not-json", P(navigation.STALE)),
        ("", Action(navigation.START)),
    ],
)
def test_payload(payload, expected):
    assert parse_action(payload, "привет") == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Начать", Action(navigation.START)),
        ("привет", Action(navigation.START)),
        ("  МЕНЮ ", Action(navigation.MENU)),
        ("услуги", Action(navigation.LIST)),
        ("Прайс-лист", Action(navigation.PRICE)),
        ("связаться с менеджером", Action(navigation.MANAGER)),
        ("оператор", Action(navigation.MANAGER)),
        ("сколько стоит", Action(navigation.UNKNOWN)),
        ("лечите ли вы астигматизм", Action(navigation.UNKNOWN)),
        ("", Action(navigation.UNKNOWN)),
        (None, Action(navigation.UNKNOWN)),
    ],
)
def test_text(text, expected):
    assert parse_action(None, text) == expected


def test_payload_has_priority_over_text():
    assert parse_action({"v": 1, "a": "price"}, "услуги") == P(navigation.PRICE)
