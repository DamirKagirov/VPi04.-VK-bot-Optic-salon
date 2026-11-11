import asyncio
import logging

from vkbottle import VKAPIError

from app import __main__ as entrypoint
from app.config import ConfigError, Settings


class FakeErrorHandler:
    def __init__(self) -> None:
        self.handlers = {}

    def register_error_handler(self, exc):
        def decorator(func):
            self.handlers[exc] = func
            return func

        return decorator


class FakeBot:
    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.error_handler = FakeErrorHandler()
        self.ran = False
        FakeBot.instances.append(self)

    def run(self):
        self.ran = True


def make_settings(tmp_path) -> Settings:
    return Settings(
        token="test-token",
        manager_contact_url="https://vk.me/test",
        state_path=tmp_path / "state.json",
        catalog_path="catalog/services.json",
    )


def test_main_returns_2_on_config_error(monkeypatch, capsys):
    def fail():
        raise ConfigError("Не задан VK_BOT_TOKEN. Добавьте его в .env.")

    monkeypatch.setattr(entrypoint, "load_settings", fail)
    assert entrypoint.main() == 2
    assert "VK_BOT_TOKEN" in capsys.readouterr().err


def test_run_builds_bot_without_network(monkeypatch, tmp_path):
    # Для проверки запуска используем реальный каталог проекта.
    FakeBot.instances.clear()
    monkeypatch.setattr(entrypoint, "Bot", FakeBot)

    assert entrypoint.run(make_settings(tmp_path)) == 0
    assert len(FakeBot.instances) == 1
    assert FakeBot.instances[0].ran is True
    assert FakeBot.instances[0].kwargs["skip_old_events"] is False


def test_run_returns_3_on_catalog_error(monkeypatch, tmp_path, caplog):
    settings = Settings(
        token="test-token",
        manager_contact_url="https://vk.me/test",
        state_path=tmp_path / "state.json",
        catalog_path=tmp_path / "missing.json",
    )

    with caplog.at_level(logging.ERROR):
        assert entrypoint.run(settings) == 3
    assert "Каталог не найден" in caplog.text


def test_error_handlers_are_registered_and_log_only_code(monkeypatch, tmp_path, caplog):
    FakeBot.instances.clear()
    monkeypatch.setattr(entrypoint, "Bot", FakeBot)

    assert entrypoint.run(make_settings(tmp_path)) == 0
    handlers = FakeBot.instances[0].error_handler.handlers
    assert VKAPIError in handlers
    assert Exception in handlers

    error = VKAPIError[15](error_msg="Access denied for test-token")
    with caplog.at_level(logging.ERROR):
        asyncio.run(handlers[VKAPIError](error))

    assert "code=15" in caplog.text
    assert "test-token" not in caplog.text
