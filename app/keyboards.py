"""Клавиатуры и payload навигации."""

from __future__ import annotations

from typing import Iterable

from vkbottle import Keyboard, KeyboardButtonColor, OpenLink, Text

from .catalog import Catalog, Service

SCHEMA_VERSION = 1


def payload(action: str, service_id: str | None = None) -> dict[str, object]:
    data: dict[str, object] = {"v": SCHEMA_VERSION, "a": action}
    if service_id is not None:
        data["id"] = service_id
    return data


def _kb() -> Keyboard:
    return Keyboard(one_time=False, inline=False)


def main_menu() -> str:
    return (
        _kb()
        .add(Text("Услуги", payload=payload("list")), color=KeyboardButtonColor.PRIMARY)
        .add(Text("Прайс-лист", payload=payload("price")), color=KeyboardButtonColor.SECONDARY)
        .row()
        .add(
            Text("Связаться с менеджером", payload=payload("mgr")),
            color=KeyboardButtonColor.POSITIVE,
        )
        .get_json()
    )


def service_list(services: Iterable[Service] | Catalog) -> str:
    items = services.ordered() if isinstance(services, Catalog) else tuple(services)
    keyboard = _kb()
    for index, service in enumerate(items):
        if index and index % 3 == 0:
            keyboard.row()
        keyboard.add(
            Text(service.button, payload=payload("svc", service.id)),
            color=KeyboardButtonColor.SECONDARY,
        )
    keyboard.row()
    keyboard.add(
        Text("К списку услуг", payload=payload("list")),
        color=KeyboardButtonColor.SECONDARY,
    )
    keyboard.add(
        Text("В главное меню", payload=payload("menu")),
        color=KeyboardButtonColor.PRIMARY,
    )
    return keyboard.get_json()


def service_card() -> str:
    return (
        _kb()
        .add(Text("К списку услуг", payload=payload("list")), color=KeyboardButtonColor.SECONDARY)
        .add(Text("В главное меню", payload=payload("menu")), color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(
            Text("Связаться с менеджером", payload=payload("mgr")),
            color=KeyboardButtonColor.POSITIVE,
        )
        .get_json()
    )


def price_menu() -> str:
    return (
        _kb()
        .add(Text("К услугам", payload=payload("list")), color=KeyboardButtonColor.SECONDARY)
        .add(Text("В главное меню", payload=payload("menu")), color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(
            Text("Связаться с менеджером", payload=payload("mgr")),
            color=KeyboardButtonColor.POSITIVE,
        )
        .get_json()
    )


def manager(manager_contact_url: str) -> str:
    return (
        _kb()
        .add(OpenLink(manager_contact_url, "Написать менеджеру"))
        .row()
        .add(
            Text("Я написал менеджеру", payload=payload("mgr_ack")),
            color=KeyboardButtonColor.POSITIVE,
        )
        .add(Text("В главное меню", payload=payload("menu")), color=KeyboardButtonColor.PRIMARY)
        .get_json()
    )


def quiet_mode() -> str:
    return (
        _kb()
        .add(Text("В главное меню", payload=payload("menu")), color=KeyboardButtonColor.PRIMARY)
        .get_json()
    )
