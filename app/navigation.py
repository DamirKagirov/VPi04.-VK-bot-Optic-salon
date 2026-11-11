"""Разбор payload и текстовых команд. Чистая логика без ВКонтакте."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

MENU = "menu"
START = "start"
LIST = "list"
PRICE = "price"
SERVICE = "svc"
MANAGER = "mgr"
MANAGER_ACK = "mgr_ack"
STALE = "stale"
UNKNOWN = "unknown"

_ACTIONS = {MENU, START, LIST, PRICE, MANAGER, MANAGER_ACK}

_TEXT_ALIASES: dict[str, str] = {
    "начать": START,
    "старт": START,
    "привет": START,
    "здравствуйте": START,
    "меню": MENU,
    "главное меню": MENU,
    "услуги": LIST,
    "список услуг": LIST,
    "каталог": LIST,
    "прайс": PRICE,
    "прайс-лист": PRICE,
    "прайс лист": PRICE,
    "цены": PRICE,
    "стоимость": PRICE,
    "менеджер": MANAGER,
    "связаться с менеджером": MANAGER,
    "связь": MANAGER,
    "оператор": MANAGER,
}


@dataclass(frozen=True)
class Action:
    kind: str
    service_id: str | None = None
    source: str = "text"


def parse_action(payload: Any, text: str | None) -> Action:
    """Возвращает действие по payload; payload имеет приоритет над текстом."""

    if isinstance(payload, str) and not payload.strip():
        # Пустая строка встречается у обычных сообщений без payload.
        payload = None

    if isinstance(payload, dict):
        if payload.get("command") == "start":
            return Action(START, source="start")
        if payload.get("v") != 1:
            return Action(STALE, source="payload")
        kind = payload.get("a")
        if isinstance(kind, str) and kind in _ACTIONS:
            return Action(kind, source="payload")
        if kind == SERVICE:
            service_id = payload.get("id")
            if isinstance(service_id, str) and service_id:
                return Action(SERVICE, service_id, source="payload")
        return Action(STALE, source="payload")

    if payload is not None:
        # Строка вместо объекта — повреждённый payload.
        return Action(STALE, source="payload")

    normalized = (text or "").strip().casefold()
    return Action(_TEXT_ALIASES.get(normalized, UNKNOWN))
