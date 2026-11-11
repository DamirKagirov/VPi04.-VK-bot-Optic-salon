"""Загрузка и валидация каталога услуг."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,40}$")
PRICE_TYPES = {"fixed", "from"}
CONFIRMATION_TYPES = {"medical", "workshop"}


class CatalogError(RuntimeError):
    """Каталог отсутствует или не соответствует схеме."""


@dataclass(frozen=True)
class Service:
    id: str
    name: str
    button: str
    short: str
    full: str
    includes: tuple[str, ...]
    price: int
    price_type: str
    price_unit: str
    caveats: tuple[str, ...]
    requires_owner_confirmation: bool
    confirmation_type: str
    sort_order: int


@dataclass(frozen=True)
class Catalog:
    schema_version: int
    updated_at: str
    price_note: str
    services: tuple[Service, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "_by_id", {service.id: service for service in self.services})

    def get(self, service_id: str) -> Service | None:
        return self._by_id.get(service_id)  # type: ignore[attr-defined]

    def ordered(self) -> tuple[Service, ...]:
        return tuple(sorted(self.services, key=lambda service: service.sort_order))


def _fail(message: str) -> None:
    raise CatalogError(f"Ошибка каталога: {message}")


def _require_str(item: dict[str, Any], key: str, where: str, *, max_len: int | None = None) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        _fail(f"{where}: поле {key} должно быть непустой строкой.")
    value = value.strip()
    if max_len is not None and len(value) > max_len:
        _fail(f"{where}: поле {key} длиннее {max_len} символов.")
    return value


def _require_list(item: dict[str, Any], key: str, where: str) -> tuple[str, ...]:
    value = item.get(key)
    if not isinstance(value, list) or not 1 <= len(value) <= 10:
        _fail(f"{where}: поле {key} должно быть списком из 1–10 пунктов.")
    result: list[str] = []
    for index, entry in enumerate(value, start=1):
        if not isinstance(entry, str) or not entry.strip():
            _fail(f"{where}: пункт {index} в {key} должен быть непустой строкой.")
        result.append(entry.strip())
    return tuple(result)


def _parse_service(item: Any, index: int) -> Service:
    where = f"услуга №{index}"
    if not isinstance(item, dict):
        _fail(f"{where}: ожидался объект.")

    service_id = _require_str(item, "id", where, max_len=40)
    if not ID_PATTERN.fullmatch(service_id):
        _fail(f"{where}: id={service_id!r} не соответствует шаблону {ID_PATTERN.pattern}.")
    where = f"услуга {service_id}"

    button = _require_str(item, "button", where, max_len=40)
    price = item.get("price")
    if isinstance(price, bool) or not isinstance(price, int) or price <= 0:
        _fail(f"{where}: price должен быть целым положительным числом.")

    price_type = _require_str(item, "price_type", where)
    if price_type not in PRICE_TYPES:
        _fail(f"{where}: price_type должен быть fixed или from.")

    confirmation_type = _require_str(item, "confirmation_type", where)
    if confirmation_type not in CONFIRMATION_TYPES:
        _fail(f"{where}: confirmation_type должен быть medical или workshop.")

    requires_confirmation = item.get("requires_owner_confirmation")
    if not isinstance(requires_confirmation, bool):
        _fail(f"{where}: requires_owner_confirmation должен быть true или false.")

    sort_order = item.get("sort_order")
    if isinstance(sort_order, bool) or not isinstance(sort_order, int):
        _fail(f"{where}: sort_order должен быть целым числом.")

    return Service(
        id=service_id,
        name=_require_str(item, "name", where, max_len=120),
        button=button,
        short=_require_str(item, "short", where, max_len=200),
        full=_require_str(item, "full", where, max_len=1200),
        includes=_require_list(item, "includes", where),
        price=price,
        price_type=price_type,
        price_unit=_require_str(item, "price_unit", where),
        caveats=_require_list(item, "caveats", where),
        requires_owner_confirmation=requires_confirmation,
        confirmation_type=confirmation_type,
        sort_order=sort_order,
    )


def parse_catalog(data: Any) -> Catalog:
    if not isinstance(data, dict):
        _fail("корень файла должен быть объектом.")

    if data.get("schema_version") != 1:
        _fail("schema_version должен быть равен 1.")

    updated_at = _require_str(data, "updated_at", "каталог")
    price_note = _require_str(data, "price_note", "каталог")

    raw_services = data.get("services")
    if not isinstance(raw_services, list) or not raw_services:
        _fail("services должен быть непустым массивом.")

    services = tuple(
        _parse_service(item, index) for index, item in enumerate(raw_services, start=1)
    )

    ids = [service.id for service in services]
    if len(set(ids)) != len(ids):
        _fail("ID услуг должны быть уникальны.")

    buttons = [service.button for service in services]
    if len(set(buttons)) != len(buttons):
        _fail("Подписи кнопок услуг должны быть уникальны.")

    orders = [service.sort_order for service in services]
    if len(set(orders)) != len(orders):
        _fail("sort_order услуг должен быть уникален.")

    return Catalog(
        schema_version=1,
        updated_at=updated_at,
        price_note=price_note,
        services=services,
    )


def load_catalog(path: str | Path) -> Catalog:
    catalog_path = Path(path)
    if not catalog_path.is_file():
        raise CatalogError(f"Каталог не найден: {catalog_path}.")

    try:
        raw = catalog_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CatalogError(f"Не удалось прочитать каталог {catalog_path}: {exc}.") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CatalogError(
            f"Ошибка каталога: некорректный JSON, строка {exc.lineno}, колонка {exc.colno}."
        ) from exc

    return parse_catalog(data)
