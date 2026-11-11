import asyncio
import json
from datetime import timedelta

from app.manager_state import ManagerState


def test_enter_exit_and_persistence(tmp_path):
    path = tmp_path / "runtime" / "state.json"
    peer_id = 123456789

    async def scenario():
        state = ManagerState(path, 12)
        state.load()
        assert await state.is_quiet(peer_id) is False

        await state.enter(peer_id)
        assert await state.is_quiet(peer_id) is True
        assert path.is_file()

        restored = ManagerState(path, 12)
        restored.load()
        assert await restored.is_quiet(peer_id) is True

        await restored.exit(peer_id)
        assert await restored.is_quiet(peer_id) is False
        assert peer_id not in json.loads(path.read_text(encoding="utf-8"))["quiet"]

    asyncio.run(scenario())


def test_expired_entry_is_pruned(tmp_path):
    path = tmp_path / "state.json"
    peer_id = 42

    async def scenario():
        state = ManagerState(path, 1)
        state.ttl = timedelta(seconds=-1)
        await state.enter(peer_id)
        assert await state.is_quiet(peer_id) is False

    asyncio.run(scenario())


def test_corrupt_file_does_not_crash(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{not json", encoding="utf-8")

    async def scenario():
        state = ManagerState(path, 12)
        state.load()
        assert await state.is_quiet(1) is False

    asyncio.run(scenario())


def test_unknown_format_does_not_crash(tmp_path):
    path = tmp_path / "state.json"
    path.write_text(json.dumps({"schema_version": 99}), encoding="utf-8")

    async def scenario():
        state = ManagerState(path, 12)
        state.load()
        assert await state.is_quiet(1) is False

    asyncio.run(scenario())


def test_state_file_is_valid_json(tmp_path):
    path = tmp_path / "state.json"

    async def scenario():
        state = ManagerState(path, 12)
        await state.enter(7)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_version"] == 1
        assert "7" in data["quiet"]
        assert set(data["quiet"]["7"]) == {"until", "set_at"}

    asyncio.run(scenario())
