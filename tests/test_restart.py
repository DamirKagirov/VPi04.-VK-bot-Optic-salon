import asyncio
import json
from pathlib import Path

from app import texts
from app.catalog import load_catalog
from app.config import Settings
from app.handlers import build_labeler
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


def build_bot(tmp_path: Path):
    """Создаёт состояние и лейблер так же, как точка входа при запуске."""

    settings = Settings(
        token="test-token",
        manager_contact_url="https://vk.me/test",
        manager_mode_ttl_hours=12,
        state_path=tmp_path / "state.json",
    )
    state = ManagerState(settings.state_path, settings.manager_mode_ttl_hours)
    state.load()
    return build_labeler(CATALOG, settings, state), state


async def handle(labeler, message: FakeMessage) -> None:
    await labeler.message_view.handlers[0].handle(message)


def read_state(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))


def test_quiet_mode_survives_restart_and_replayed_event(tmp_path):
    async def scenario():
        labeler, state = build_bot(tmp_path)
        await handle(labeler, FakeMessage(9, None, {"v": 1, "a": "mgr_ack"}))
        assert await state.is_quiet(9) is True

        # «Перезапуск»: новый объект состояния читает тот же файл.
        restarted, restarted_state = build_bot(tmp_path)
        assert await restarted_state.is_quiet(9) is True

        # ВКонтакте может повторить последнее событие после перезапуска.
        await handle(restarted, FakeMessage(9, None, {"v": 1, "a": "mgr_ack"}))
        data = read_state(tmp_path)
        assert list(data["quiet"]) == ["9"]
        assert set(data["quiet"]["9"]) == {"until", "set_at"}

        silent = FakeMessage(9, "привет", None)
        await handle(restarted, silent)
        assert silent.sent == []

        menu = FakeMessage(9, None, {"v": 1, "a": "menu"})
        await handle(restarted, menu)
        assert menu.sent[0][0] == texts.QUIET_EXIT
        assert await restarted_state.is_quiet(9) is False
        assert read_state(tmp_path)["quiet"] == {}

    asyncio.run(scenario())


def test_corrupt_state_after_restart_does_not_block_answers(tmp_path):
    (tmp_path / "state.json").write_text("{not json", encoding="utf-8")

    async def scenario():
        labeler, state = build_bot(tmp_path)
        assert await state.is_quiet(1) is False

        message = FakeMessage(1, "услуги", None)
        await handle(labeler, message)
        assert len(message.sent) == 1
        assert message.sent[0][0] == texts.SERVICE_LIST

        # Следующая запись создаёт корректный файл состояния.
        ack = FakeMessage(1, None, {"v": 1, "a": "mgr_ack"})
        await handle(labeler, ack)
        assert read_state(tmp_path)["schema_version"] == 1

    asyncio.run(scenario())


def test_repeated_navigation_event_is_idempotent(tmp_path):
    async def scenario():
        labeler, state = build_bot(tmp_path)
        payload = {"v": 1, "a": "svc", "id": "lens_refit"}

        first = FakeMessage(2, None, payload)
        repeated = FakeMessage(2, None, payload)
        await handle(labeler, first)
        await handle(labeler, repeated)

        assert first.sent[0] == repeated.sent[0]
        assert await state.is_quiet(2) is False
        assert not (tmp_path / "state.json").exists()

    asyncio.run(scenario())
