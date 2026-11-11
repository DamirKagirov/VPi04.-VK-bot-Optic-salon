"""Точка входа: python -m app."""

from __future__ import annotations

import logging
import re
import sys

from vkbottle import VKAPIError
from vkbottle.bot import Bot

from .catalog import CatalogError, load_catalog
from .config import ConfigError, Settings, load_settings
from .handlers import build_labeler
from .manager_state import ManagerState

TOKEN_RE = re.compile(r"vk1\.[A-Za-z0-9._-]+")


class RedactingFormatter(logging.Formatter):
    """Убирает токен из готовой строки лога, включая traceback.

    Фильтр на ``LogRecord`` не видит текст исключения: logging форматирует
    traceback уже после фильтров. Поэтому очищаем итоговую строку.
    """

    def __init__(self, fmt: str, token: str) -> None:
        super().__init__(fmt)
        self.token = token

    def _redact(self, value: str) -> str:
        if self.token:
            value = value.replace(self.token, "***")
        return TOKEN_RE.sub("***", value)

    def format(self, record: logging.LogRecord) -> str:
        return self._redact(super().format(record))


def setup_logging(level: str, token: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        RedactingFormatter("%(asctime)s %(levelname)s %(name)s %(message)s", token)
    )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # VKBottle добавляет свой цветной StreamHandler. Убираем его, чтобы
    # сообщения шли только через наш RedactingFormatter и не дублировались.
    vkbottle_logger = logging.getLogger("vkbottle")
    vkbottle_logger.handlers.clear()
    vkbottle_logger.propagate = True
    vkbottle_logger.setLevel(max(logging.INFO, logging.getLogger().level))


def run(settings: Settings) -> int:
    try:
        catalog = load_catalog(settings.catalog_path)
    except CatalogError as exc:
        logging.getLogger(__name__).error("%s", exc)
        return 3

    pending = [
        service.id
        for service in catalog.services
        if service.requires_owner_confirmation
    ]
    if pending:
        logging.getLogger(__name__).warning(
            "Услуги без подтверждения владельцем: %s", ", ".join(pending)
        )

    state = ManagerState(settings.state_path, settings.manager_mode_ttl_hours)
    state.load()

    labeler = build_labeler(catalog, settings, state)
    bot = Bot(token=settings.token, labeler=labeler, skip_old_events=False)

    @bot.error_handler.register_error_handler(VKAPIError)
    async def handle_vkapi_error(exc: VKAPIError) -> None:
        logging.getLogger(__name__).error("vkapi_error code=%s", getattr(exc, "code", None))

    @bot.error_handler.register_error_handler(Exception)
    async def handle_unexpected_error(exc: Exception) -> None:
        logging.getLogger(__name__).error(
            "unexpected_error type=%s", type(exc).__name__, exc_info=exc
        )

    logging.getLogger(__name__).info(
        "Запуск бота: услуг=%s, каталог=%s", len(catalog.services), settings.catalog_path
    )
    bot.run()
    return 0


def main() -> int:
    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 2

    setup_logging(settings.log_level, settings.token)

    try:
        return run(settings)
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Остановлено пользователем")
        return 0
    except Exception:
        logging.getLogger(__name__).exception("Не удалось запустить бота")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
