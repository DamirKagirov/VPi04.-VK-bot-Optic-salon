"""Сборка обработчиков бота."""

from __future__ import annotations

import logging

from vkbottle import VKAPIError
from vkbottle.bot import BotLabeler, Message

from .. import keyboards, texts
from ..catalog import Catalog
from ..config import Settings
from ..manager_state import ManagerState
from .processor import MessageProcessor

logger = logging.getLogger(__name__)


async def _answer(message: Message, text: str, keyboard: str | None) -> bool:
    """Отправляет ответ, не давая ошибке API уронить обработчик.

    Возвращает True, если сообщение удалось отправить.
    """

    try:
        await message.answer(text, keyboard=keyboard)
        return True
    except VKAPIError as exc:
        logger.error(
            "vkapi_error peer_id=%s code=%s method=messages.send",
            message.peer_id,
            getattr(exc, "code", None),
        )
    except Exception:
        logger.exception("send_error peer_id=%s", message.peer_id)
    return False


def build_labeler(catalog: Catalog, settings: Settings, state: ManagerState) -> BotLabeler:
    labeler = BotLabeler()
    processor = MessageProcessor(catalog, settings, state)

    @labeler.message()
    async def handle_message(message: Message) -> None:
        peer_id = message.peer_id

        try:
            result = await processor.process(
                peer_id,
                message.get_payload_json(),
                message.text,
            )
        except Exception:
            # Пользователь не должен остаться без ответа из-за ошибки в сценарии.
            logger.exception("processing_error peer_id=%s", peer_id)
            await _answer(message, texts.ACTION_ERROR, keyboards.main_menu())
            return

        logger.info(
            "message peer_id=%s action=%s service=%s answered=%s",
            peer_id,
            result.action.kind,
            result.action.service_id,
            result.screen is not None,
        )

        if result.screen is None:
            return

        await _answer(message, result.screen.text, result.screen.keyboard)

    return labeler
