import json
from pathlib import Path

import pytest

from app import navigation, texts
from app.catalog import load_catalog
from app.navigation import Action
from app.screens import render
from app.texts import price_with_unit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = load_catalog(ROOT / "catalog" / "services.json")
URL = "https://vk.me/test"


def test_card_and_price_list_use_same_price_string():
    price_screen = render(Action(navigation.PRICE), CATALOG, URL, 12)
    for service in CATALOG.services:
        card = render(Action(navigation.SERVICE, service.id), CATALOG, URL, 12)
        price_line = f"{service.name} — {price_with_unit(service)}"
        assert price_line in price_screen.text
        assert card.text.splitlines()[2] == price_with_unit(service)


def test_card_contains_sections_and_disclaimer():
    card = render(Action(navigation.SERVICE, "vision_exam_glasses"), CATALOG, URL, 12)
    assert "Что входит:" in card.text
    assert "Важно:" in card.text
    assert texts.DISCLAIMER in card.text


def test_unknown_and_stale_screens():
    unknown = render(Action(navigation.UNKNOWN), CATALOG, URL, 12)
    stale = render(Action(navigation.STALE), CATALOG, URL, 12)
    assert unknown.text == texts.UNKNOWN
    assert stale.text == texts.STALE_BUTTON
    assert "master" not in unknown.text.lower()


def test_missing_service_opens_list():
    screen = render(Action(navigation.SERVICE, "removed_service"), CATALOG, URL, 12)
    assert screen.text == texts.SERVICE_NOT_FOUND
    payload = json.loads(screen.keyboard)
    labels = [button["action"]["label"] for row in payload["buttons"] for button in row]
    assert "Проверка зрения для очков" in labels


def test_manager_screen_and_quiet_ack():
    screen = render(Action(navigation.MANAGER), CATALOG, URL, 12)
    assert URL in screen.text
    assert "Отвечает человек" in screen.text
    assert "10:00" in screen.text and "19:00" in screen.text
    ack = render(Action(navigation.MANAGER_ACK), CATALOG, URL, 12)
    assert "12 часов" in ack.text


def test_start_shows_greeting():
    screen = render(Action(navigation.START, source="start"), CATALOG, URL, 12)
    assert screen.text == texts.GREETING
    assert "Ясные очи" in screen.text


def test_quiet_exit_text():
    screen = render(Action(navigation.MENU), CATALOG, URL, 12, quiet_exit=True)
    assert screen.text == texts.QUIET_EXIT


def test_all_keyboards_fit_vk_limits():
    screens = [
        render(Action(navigation.MENU), CATALOG, URL, 12),
        render(Action(navigation.LIST), CATALOG, URL, 12),
        render(Action(navigation.PRICE), CATALOG, URL, 12),
        render(Action(navigation.MANAGER), CATALOG, URL, 12),
        render(Action(navigation.MANAGER_ACK), CATALOG, URL, 12),
    ]
    screens += [
        render(Action(navigation.SERVICE, service.id), CATALOG, URL, 12)
        for service in CATALOG.services
    ]
    for screen in screens:
        payload = json.loads(screen.keyboard)
        for row in payload["buttons"]:
            assert len(row) <= 5
            for button in row:
                action = button["action"]
                assert len(action["label"]) <= 40
                if "payload" in action:
                    assert len(json.dumps(action["payload"], ensure_ascii=False)) <= 255
