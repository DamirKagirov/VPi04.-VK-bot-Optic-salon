import asyncio
from pathlib import Path

from app.catalog import load_catalog
from app.config import Settings
from app.handlers.processor import MessageProcessor
from app.manager_state import ManagerState
from app import texts

ROOT = Path(__file__).resolve().parents[1]
CATALOG = load_catalog(ROOT / "catalog" / "services.json")


def make_settings() -> Settings:
    return Settings(
        token="test-token",
        manager_contact_url="https://vk.me/test",
        manager_mode_ttl_hours=12,
    )


def test_manager_ack_enables_quiet_and_blocks_text(tmp_path):
    async def scenario():
        state = ManagerState(tmp_path / "state.json", 12)
        processor = MessageProcessor(CATALOG, make_settings(), state)
        peer_id = 100

        ack = await processor.process(peer_id, {"v": 1, "a": "mgr_ack"}, None)
        assert ack.screen is not None
        assert "12 часов" in ack.screen.text
        assert await state.is_quiet(peer_id) is True

        silent = await processor.process(peer_id, None, "привет")
        assert silent.screen is None

        silent_service = await processor.process(
            peer_id, {"v": 1, "a": "svc", "id": "lens_refit"}, None
        )
        assert silent_service.screen is None

        start = await processor.process(peer_id, {"command": "start"}, None)
        assert start.screen is None
        assert await state.is_quiet(peer_id) is True

    asyncio.run(scenario())


def test_menu_exits_quiet_and_other_peer_is_unaffected(tmp_path):
    async def scenario():
        state = ManagerState(tmp_path / "state.json", 12)
        processor = MessageProcessor(CATALOG, make_settings(), state)

        await processor.process(7, {"v": 1, "a": "mgr_ack"}, None)
        assert await state.is_quiet(7) is True

        other = await processor.process(8, None, "услуги")
        assert other.screen is not None
        assert await state.is_quiet(8) is False

        menu = await processor.process(7, {"v": 1, "a": "menu"}, None)
        assert menu.screen is not None
        assert menu.screen.text == texts.QUIET_EXIT
        assert await state.is_quiet(7) is False

    asyncio.run(scenario())


def test_stale_payload_returns_menu(tmp_path):
    async def scenario():
        state = ManagerState(tmp_path / "state.json", 12)
        processor = MessageProcessor(CATALOG, make_settings(), state)
        result = await processor.process(1, {"v": 2, "a": "menu"}, None)
        assert result.screen is not None
        assert result.screen.text == texts.STALE_BUTTON

    asyncio.run(scenario())
