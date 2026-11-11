import pytest

from app.config import ConfigError, Settings, load_settings


@pytest.fixture()
def env(monkeypatch, tmp_path):
    monkeypatch.delenv("VK_BOT_TOKEN", raising=False)
    monkeypatch.delenv("MANAGER_CONTACT_URL", raising=False)
    monkeypatch.delenv("MANAGER_MODE_TTL_HOURS", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("STATE_PATH", raising=False)
    monkeypatch.delenv("CATALOG_PATH", raising=False)
    return tmp_path / "no.env"


def test_valid_settings(env, monkeypatch):
    monkeypatch.setenv("VK_BOT_TOKEN", "secret-token")
    monkeypatch.setenv("MANAGER_CONTACT_URL", "https://vk.me/clear-eyes")
    settings = load_settings(env)
    assert settings.token == "secret-token"
    assert settings.manager_contact_url == "https://vk.me/clear-eyes"
    assert settings.manager_mode_ttl_hours == 12
    assert settings.log_level == "INFO"
    assert str(settings.state_path).endswith("state.json")
    assert str(settings.catalog_path).endswith("services.json")


def test_vk_ru_manager_url_accepted(env, monkeypatch):
    monkeypatch.setenv("VK_BOT_TOKEN", "secret-token")
    monkeypatch.setenv("MANAGER_CONTACT_URL", "https://vk.ru/club243135828")
    settings = load_settings(env)
    assert settings.manager_contact_url == "https://vk.ru/club243135828"


def test_token_is_hidden_from_repr(env, monkeypatch):
    monkeypatch.setenv("VK_BOT_TOKEN", "super-secret-token")
    monkeypatch.setenv("MANAGER_CONTACT_URL", "https://vk.com/clear-eyes")
    settings = load_settings(env)
    assert "super-secret-token" not in repr(settings)
    assert isinstance(settings, Settings)


def test_missing_token(env):
    with pytest.raises(ConfigError, match="VK_BOT_TOKEN"):
        load_settings(env)


def test_missing_manager_url(env, monkeypatch):
    monkeypatch.setenv("VK_BOT_TOKEN", "token")
    with pytest.raises(ConfigError, match="MANAGER_CONTACT_URL"):
        load_settings(env)


@pytest.mark.parametrize("url", ["http://vk.com/x", "https://example.com/x", "vk.me/x"])
def test_bad_manager_url(env, monkeypatch, url):
    monkeypatch.setenv("VK_BOT_TOKEN", "token")
    monkeypatch.setenv("MANAGER_CONTACT_URL", url)
    with pytest.raises(ConfigError, match="MANAGER_CONTACT_URL"):
        load_settings(env)


@pytest.mark.parametrize("ttl", ["0", "169", "abc", ""])
def test_bad_ttl(env, monkeypatch, ttl):
    monkeypatch.setenv("VK_BOT_TOKEN", "token")
    monkeypatch.setenv("MANAGER_CONTACT_URL", "https://vk.me/x")
    monkeypatch.setenv("MANAGER_MODE_TTL_HOURS", ttl)
    with pytest.raises(ConfigError, match="MANAGER_MODE_TTL_HOURS"):
        load_settings(env)


def test_bad_log_level(env, monkeypatch):
    monkeypatch.setenv("VK_BOT_TOKEN", "token")
    monkeypatch.setenv("MANAGER_CONTACT_URL", "https://vk.me/x")
    monkeypatch.setenv("LOG_LEVEL", "TRACE")
    with pytest.raises(ConfigError, match="LOG_LEVEL"):
        load_settings(env)


def test_token_with_spaces_rejected(env, monkeypatch):
    monkeypatch.setenv("VK_BOT_TOKEN", "token with space")
    monkeypatch.setenv("MANAGER_CONTACT_URL", "https://vk.me/x")
    with pytest.raises(ConfigError, match="VK_BOT_TOKEN"):
        load_settings(env)
