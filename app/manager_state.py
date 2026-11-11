"""«Тихий режим» менеджера: небольшое состояние, переживающее перезапуск."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ManagerState:
    def __init__(self, path: str | Path, ttl_hours: int) -> None:
        self.path = Path(path)
        self.ttl = timedelta(hours=ttl_hours)
        self._lock = asyncio.Lock()
        self._data: dict[str, dict[str, str]] = {}

    def load(self) -> None:
        """Читает файл состояния. Ошибки не мешают запуску бота."""

        if not self.path.is_file():
            self._data = {}
            return

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Не удалось прочитать %s: %s. Тихий режим отключён.", self.path, exc)
            self._data = {}
            return

        if not isinstance(raw, dict) or raw.get("schema_version") != 1:
            logger.warning("Файл %s имеет неизвестный формат. Тихий режим отключён.", self.path)
            self._data = {}
            return

        quiet = raw.get("quiet")
        if not isinstance(quiet, dict):
            logger.warning("В %s нет объекта quiet. Тихий режим отключён.", self.path)
            self._data = {}
            return

        cleaned: dict[str, dict[str, str]] = {}
        for peer_id, entry in quiet.items():
            if not isinstance(peer_id, str) or not isinstance(entry, dict):
                continue
            until = entry.get("until")
            set_at = entry.get("set_at")
            if isinstance(until, str) and isinstance(set_at, str):
                cleaned[peer_id] = {"until": until, "set_at": set_at}
        self._data = cleaned

    async def is_quiet(self, peer_id: int) -> bool:
        async with self._lock:
            self._prune()
            return str(peer_id) in self._data

    async def enter(self, peer_id: int) -> datetime:
        now = datetime.now(timezone.utc)
        until = now + self.ttl
        async with self._lock:
            self._prune(now)
            self._data[str(peer_id)] = {
                "until": until.isoformat(),
                "set_at": now.isoformat(),
            }
            self._save()
        return until

    async def exit(self, peer_id: int) -> None:
        async with self._lock:
            self._data.pop(str(peer_id), None)
            self._save()

    def _prune(self, now: datetime | None = None) -> None:
        current = now or datetime.now(timezone.utc)
        expired: list[str] = []
        for peer_id, entry in self._data.items():
            try:
                until = datetime.fromisoformat(entry["until"])
            except (KeyError, ValueError):
                expired.append(peer_id)
                continue
            if until.tzinfo is None:
                until = until.replace(tzinfo=timezone.utc)
            if until <= current:
                expired.append(peer_id)
        for peer_id in expired:
            self._data.pop(peer_id, None)

    def _save(self) -> None:
        payload: dict[str, Any] = {"schema_version": 1, "quiet": self._data}
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self.path.with_name(f"{self.path.name}.tmp")
            tmp_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(tmp_path, self.path)
        except OSError as exc:
            logger.warning(
                "Не удалось сохранить %s: %s. Тихий режим не сохранится.",
                self.path,
                exc,
            )
