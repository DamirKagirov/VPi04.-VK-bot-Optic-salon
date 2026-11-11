import asyncio
import json
import logging
from pathlib import Path

from vkbottle import VKAPIError

from app import keyboards, texts
from app.catalog import load_catalog
from app.config import Settings
from app.handlers import build_labeler
from app.handlers.processor import MessageProcessor
from app.manager_state import ManagerState

ROOT = Path(__file__).resolve().parents[1]
CATALOG = load_catalog(ROOT / "catalog" / "services.json")


class FakeMessage:
    def __init__(self, peer_id: int, text: str | None, payload: object) -> None:
        self.peer_id = peer_id
        self.text = text
        self.payload = payload
        self.sent: list[tuple[str, str | None]] = []

    def get_payload_json(self):
        return self.payload

    async def answer(self, message: str, keyboard: str | None = None) -> None:
        self.sent.append((message, keyboard))


def make_labeler(tmp_path):
    settings = Settings(
        token="test-token",
        manager_contact_url="https://vk.me/test",
        manager_mode_ttl_hours=12,
    )
    state = ManagerState(tmp_path / "state.json", 12)
    return build_labeler(CATALOG, settings, state), state


def test_handler_answers_list(tmp_path):
    async def scenario():
        labeler, _ = make_labeler(tmp_path)
        handler = labeler.message_view.handlers[0]
        message = FakeMessage(1, "услуги", None)
        await handler.handle(message)
        assert len(message.sent) == 1
        assert message.sent[0][0] == texts.SERVICE_LIST
        keyboard = json.loads(message.sent[0][1] or "{}")
        labels = [
            button["action"]["label"]
            for row in keyboard["buttons"]
            for button in row
        ]
        assert "Проверка зрения для очков" in labels

    asyncio.run(scenario())


class FailingMessage(FakeMessage):
    def __init__(self, peer_id, text, payload, error: Exception) -> None:
        super().__init__(peer_id, text, payload)
        self.error = error

    async def answer(self, message: str, keyboard: str | None = None) -> None:
        raise self.error


def api_error(code: int = 15, message: str = "Access denied") -> VKAPIError:
    return VKAPIError[code](error_msg=message)


def test_handler_quiet_mode_and_menu_exit(tmp_path):
    async def scenario():
        labeler, state = make_labeler(tmp_path)
        handler = labeler.message_view.handlers[0]

        ack = FakeMessage(2, None, {"v": 1, "a": "mgr_ack"})
        await handler.handle(ack)
        assert await state.is_quiet(2) is True
        assert "12 часов" in ack.sent[0][0]

        text = FakeMessage(2, "привет", None)
        await handler.handle(text)
        assert text.sent == []
        assert await state.is_quiet(2) is True

        menu = FakeMessage(2, None, {"v": 1, "a": "menu"})
        await handler.handle(menu)
        assert menu.sent[0][0] == texts.QUIET_EXIT
        assert await state.is_quiet(2) is False

    asyncio.run(scenario())


def test_vkapi_error_on_send_is_logged_and_next_message_works(tmp_path, caplog):
    async def scenario():
        labeler, _ = make_labeler(tmp_path)
        handler = labeler.message_view.handlers[0]
        caplog.set_level(logging.ERROR)

        failing = FailingMessage(
            3,
            "меню",
            None,
            api_error(15, "Access denied: test-token"),
        )
        await handler.handle(failing)

        assert "code=15" in caplog.text
        assert "test-token" not in caplog.text
        assert "меню" not in caplog.text

        # После ошибки API процесс и обработчик продолжают работать.
        ok = FakeMessage(3, None, {"v": 1, "a": "menu"})
        await handler.handle(ok)
        assert len(ok.sent) == 1
        assert ok.sent[0][0] == texts.MENU

    asyncio.run(scenario())


def test_processing_error_sends_generic_message(tmp_path, monkeypatch, caplog):
    def boom(self, *args, **kwargs):
        raise RuntimeError("scenario failed")

    monkeypatch.setattr(MessageProcessor, "process", boom)
    caplog.set_level(logging.ERROR)

    async def scenario():
        labeler, _ = make_labeler(tmp_path)
        handler = labeler.message_view.handlers[0]

        message = FakeMessage(4, "услуги", None)
        await handler.handle(message)

        assert len(message.sent) == 1
        assert message.sent[0][0] == texts.ACTION_ERROR
        assert message.sent[0][1] == keyboards.main_menu()

    asyncio.run(scenario())
    assert "processing_error" in caplog.text
    assert "услуги" not in caplog.text


def test_processing_error_with_failing_send_does_not_raise(tmp_path, monkeypatch):
    def boom(self, *args, **kwargs):
        raise RuntimeError("scenario failed")

    monkeypatch.setattr(MessageProcessor, "process", boom)

    async def scenario():
        labeler, _ = make_labeler(tmp_path)
        handler = labeler.message_view.handlers[0]

        message = FailingMessage(5, "услуги", None, api_error(7))
        # Ошибка отправки fallback-сообщения не должна выбрасываться наружу.
        await handler.handle(message)

    asyncio.run(scenario())
