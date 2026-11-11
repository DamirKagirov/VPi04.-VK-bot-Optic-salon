"""Обработка одного сообщения без привязки к транспорту VKBottle."""

from __future__ import annotations

from dataclasses import dataclass

from .. import navigation
from ..catalog import Catalog
from ..config import Settings
from ..manager_state import ManagerState
from ..navigation import Action, parse_action
from ..screens import Screen, render


@dataclass(frozen=True)
class ProcessResult:
    action: Action
    screen: Screen | None


class MessageProcessor:
    def __init__(
        self,
        catalog: Catalog,
        settings: Settings,
        state: ManagerState,
    ) -> None:
        self.catalog = catalog
        self.settings = settings
        self.state = state

    async def process(self, peer_id: int, payload: object, text: str | None) -> ProcessResult:
        action = parse_action(payload, text)
        quiet = await self.state.is_quiet(peer_id)
        quiet_menu = action.kind == navigation.MENU and action.source == "payload"

        if quiet and not quiet_menu:
            return ProcessResult(action, None)

        quiet_exit = quiet and quiet_menu
        if quiet_exit:
            await self.state.exit(peer_id)

        if action.kind == navigation.MANAGER_ACK:
            await self.state.enter(peer_id)

        screen = render(
            action,
            self.catalog,
            self.settings.manager_contact_url,
            self.settings.manager_mode_ttl_hours,
            quiet_exit=quiet_exit,
        )
        return ProcessResult(action, screen)
