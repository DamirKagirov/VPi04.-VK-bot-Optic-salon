"""Сборка экранов: текст + клавиатура. Не зависит от VKBottle-событий."""

from __future__ import annotations

from dataclasses import dataclass

from . import keyboards, navigation, texts
from .catalog import Catalog
from .navigation import Action


@dataclass(frozen=True)
class Screen:
    text: str
    keyboard: str


def render(
    action: Action,
    catalog: Catalog,
    manager_contact_url: str,
    ttl_hours: int,
    *,
    quiet_exit: bool = False,
) -> Screen:
    if action.kind == navigation.START:
        return Screen(texts.GREETING, keyboards.main_menu())

    if action.kind == navigation.MENU:
        return Screen(
            texts.QUIET_EXIT if quiet_exit else texts.MENU,
            keyboards.main_menu(),
        )

    if action.kind == navigation.LIST:
        return Screen(texts.SERVICE_LIST, keyboards.service_list(catalog))

    if action.kind == navigation.PRICE:
        return Screen(texts.price_list(catalog), keyboards.price_menu())

    if action.kind == navigation.SERVICE:
        service = catalog.get(action.service_id or "")
        if service is None:
            return Screen(texts.SERVICE_NOT_FOUND, keyboards.service_list(catalog))
        return Screen(texts.service_card(service), keyboards.service_card())

    if action.kind == navigation.MANAGER:
        return Screen(
            texts.manager_screen(manager_contact_url),
            keyboards.manager(manager_contact_url),
        )

    if action.kind == navigation.MANAGER_ACK:
        return Screen(texts.quiet_ack(ttl_hours), keyboards.quiet_mode())

    if action.kind == navigation.STALE:
        return Screen(texts.STALE_BUTTON, keyboards.main_menu())

    return Screen(texts.UNKNOWN, keyboards.main_menu())
