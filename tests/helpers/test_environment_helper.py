import pytest

from mavis.reporting.helpers.environment_helper import HostingEnvironment


def test_name_reads_from_sentry_environment(monkeypatch):
    """Test that name reads from SENTRY_ENVIRONMENT env var."""
    monkeypatch.setenv("SENTRY_ENVIRONMENT", "qa")
    assert HostingEnvironment.name() == "qa"


def test_name_raises_when_sentry_environment_not_set(monkeypatch):
    """Test that name raises KeyError when SENTRY_ENVIRONMENT is not set."""
    monkeypatch.delenv("SENTRY_ENVIRONMENT", raising=False)
    with pytest.raises(KeyError):
        HostingEnvironment.name()


def test_is_production_behaviour(monkeypatch):
    """Test that is_production behaves correctly for different environments."""
    monkeypatch.setenv("SENTRY_ENVIRONMENT", "production")
    assert HostingEnvironment.is_production() is True

    monkeypatch.setenv("SENTRY_ENVIRONMENT", "development")
    assert HostingEnvironment.is_production() is False

    monkeypatch.setenv("SENTRY_ENVIRONMENT", "qa")
    assert HostingEnvironment.is_production() is False


def test_colour(monkeypatch):
    """Test that colour returns correct color for each environment."""
    monkeypatch.setenv("SENTRY_ENVIRONMENT", "production")
    assert HostingEnvironment.colour() == "blue"

    monkeypatch.setenv("SENTRY_ENVIRONMENT", "development")
    assert HostingEnvironment.colour() == "white"

    monkeypatch.setenv("SENTRY_ENVIRONMENT", "qa")
    assert HostingEnvironment.colour() == "orange"

    monkeypatch.setenv("SENTRY_ENVIRONMENT", "test")
    assert HostingEnvironment.colour() == "red"


def test_colour_defaults_to_white_for_unknown(monkeypatch):
    """Test that colour defaults to white for unknown environments."""
    monkeypatch.setenv("SENTRY_ENVIRONMENT", "unknown")
    assert HostingEnvironment.colour() == "white"


def test_title(monkeypatch):
    """Test that title returns capitalized environment name."""
    monkeypatch.setenv("SENTRY_ENVIRONMENT", "production")
    assert HostingEnvironment.title() == "Production"

    monkeypatch.setenv("SENTRY_ENVIRONMENT", "development")
    assert HostingEnvironment.title() == "Development"

    monkeypatch.setenv("SENTRY_ENVIRONMENT", "qa")
    assert HostingEnvironment.title() == "QA"


def test_title_in_sentence(monkeypatch):
    """Test that title_in_sentence returns the environment name for sentences."""
    monkeypatch.setenv("SENTRY_ENVIRONMENT", "development")
    assert HostingEnvironment.title_in_sentence() == "development"

    monkeypatch.setenv("SENTRY_ENVIRONMENT", "qa")
    assert HostingEnvironment.title_in_sentence() == "QA"

    monkeypatch.setenv("SENTRY_ENVIRONMENT", "production")
    assert HostingEnvironment.title_in_sentence() == "production"


def test_theme_colour(monkeypatch):
    """Test that theme_colour returns correct hex colour for each environment."""
    monkeypatch.setenv("SENTRY_ENVIRONMENT", "production")
    assert HostingEnvironment.theme_colour() == "#005eb8"

    monkeypatch.setenv("SENTRY_ENVIRONMENT", "development")
    assert HostingEnvironment.theme_colour() == "#fff"

    monkeypatch.setenv("SENTRY_ENVIRONMENT", "qa")
    assert HostingEnvironment.theme_colour() == "#ffdc8e"

    monkeypatch.setenv("SENTRY_ENVIRONMENT", "test")
    assert HostingEnvironment.theme_colour() == "#f7d4d1"


def test_theme_colour_defaults_for_unknown(monkeypatch):
    """Test that theme_colour defaults to white for unknown environments."""
    monkeypatch.setenv("SENTRY_ENVIRONMENT", "unknown")
    assert HostingEnvironment.theme_colour() == "#fff"
