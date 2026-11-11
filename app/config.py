"""Загрузка и проверка настроек из окружения и .env."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}
DEFAULT_MANAGER_TTL_HOURS = 12
MANAGER_URL_PREFIXES = ("https://vk.com/", "https://vk.me/", "https://vk.ru/")


class ConfigError(RuntimeError):
    """Конфигурация не позволяет запустить бота."""


@dataclass(frozen=True)
class Settings:
    token: str = field(repr=False)
    manager_contact_url: str
    manager_mode_ttl_hours: int = DEFAULT_MANAGER_TTL_HOURS
    log_level: str = "INFO"
    state_path: Path = Path("runtime/state.json")
    catalog_path: Path = Path("catalog/services.json")


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(f"Не задан {name}. Добавьте его в .env.")
    return value


def _parse_ttl(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(
            "MANAGER_MODE_TTL_HOURS должен быть целым от 1 до 168."
        ) from exc
    if not 1 <= value <= 168:
        raise ConfigError("MANAGER_MODE_TTL_HOURS должен быть целым от 1 до 168.")
    return value


def _parse_log_level(raw: str) -> str:
    value = raw.strip().upper()
    if value not in ALLOWED_LOG_LEVELS:
        raise ConfigError(
            "Неизвестный LOG_LEVEL. Допустимо: DEBUG, INFO, WARNING, ERROR."
        )
    return value


def load_settings(env_path: str | Path = ".env") -> Settings:
    """Читает .env (если есть) и переменные процесса.

    Переменные процесса имеют приоритет: load_dotenv не перезаписывает их.
    """

    path = Path(env_path)
    if path.is_file():
        load_dotenv(dotenv_path=path, override=False)

    token = _required("VK_BOT_TOKEN")
    if any(char.isspace() for char in token):
        raise ConfigError("VK_BOT_TOKEN не должен содержать пробелов и переносов строк.")

    manager_url = _required("MANAGER_CONTACT_URL")
    if not manager_url.startswith(MANAGER_URL_PREFIXES):
        raise ConfigError(
            "MANAGER_CONTACT_URL должен начинаться с https://vk.com/, https://vk.me/ "
            "или https://vk.ru/."
        )

    ttl_raw = os.getenv("MANAGER_MODE_TTL_HOURS", str(DEFAULT_MANAGER_TTL_HOURS))
    log_level_raw = os.getenv("LOG_LEVEL", "INFO")

    return Settings(
        token=token,
        manager_contact_url=manager_url,
        manager_mode_ttl_hours=_parse_ttl(ttl_raw),
        log_level=_parse_log_level(log_level_raw),
        state_path=Path(os.getenv("STATE_PATH", "runtime/state.json")),
        catalog_path=Path(os.getenv("CATALOG_PATH", "catalog/services.json")),
    )
