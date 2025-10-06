from mavis.reporting.helpers.environment_helper import (
    Environment,
    EnvType,
)


def test_environment_is_production_behaviour():
    """Test that is_production behaves correctly for different environments."""
    assert Environment(EnvType.PROD).is_production() is True
    assert Environment(EnvType.DEV).is_production() is False
    assert Environment(EnvType.STAGING).is_production() is False
    assert Environment(EnvType.TEST).is_production() is False


def test_environment_colour_property():
    """Test that colour property returns correct color for each environment."""
    assert Environment(EnvType.PROD).colour == "blue"
    assert Environment(EnvType.DEV).colour == "white"
    assert Environment(EnvType.STAGING).colour == "purple"
    assert Environment(EnvType.TEST).colour == "red"


def test_environment_title_property():
    """Test that title property returns capitalized environment type."""
    assert Environment(EnvType.PROD).title == "Production"
    assert Environment(EnvType.DEV).title == "Development"
    assert Environment(EnvType.STAGING).title == "Staging"


def test_environment_title_in_sentence_property():
    """Test that title_in_sentence property returns correct warning message."""
    title_in_sentence = Environment(EnvType.DEV).title_in_sentence
    assert (
        title_in_sentence
        == "This is a development environment."
        + " Do not use it to make clinical decisions."
    )
