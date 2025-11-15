import pytest
from bs4 import BeautifulSoup

from mavis.reporting import create_app


def card_params():
    return {
        "classes": "nhsuk-grid-column-one-third",
        "card_classes": "app-card--blue",
        "heading": "Test Heading",
        "description": "123",
        "caption": "children",
    }


def card_params_with_html():
    return {
        "classes": "nhsuk-grid-column-one-third",
        "card_classes": "app-card--blue",
        "heading": "<strong>Test Heading</strong>",
        "description": "<p>123</p>",
        "caption": "<strong>children</strong>",
    }


def card_soup(render_macro, params):
    """Get the BeautifulSoup object for a card."""
    html = render_macro(params)
    return BeautifulSoup(html, "html.parser")


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "MAVIS_ROOT_URL": "http://mavis.test/",
            "TESTING": True,
            "CLIENT_ID": "test_client_id",
            "CLIENT_SECRET": "test_client_secret",
        }
    )
    return app


@pytest.fixture()
def render_macro(app):
    """Helper fixture to render the app_dashboard_card macro."""

    def _render(params):
        with app.app_context():
            template = app.jinja_env.get_template("components/app_dashboard_card.jinja")
            macro = template.module.app_dashboard_card
            return macro(params)

    return _render


class TestAppDashboardCard:
    def test_card_classes_are_correct(self, render_macro):
        """Test that the card classes are correct."""

        soup = card_soup(render_macro, card_params())

        outer_div = soup.find("div", class_="nhsuk-card-group__item")
        assert outer_div is not None
        outer_classes = outer_div.get("class") or []
        assert "nhsuk-grid-column-one-third" in outer_classes
        assert "app-card-group__item" in outer_classes

        card = outer_div.find("div", class_="app-card")
        assert card is not None
        card_classes = card.get("class") or []
        assert "app-card--blue" in card_classes

    def test_heading_is_correct(self, render_macro):
        """Test that the heading is rendered with correct classes and level."""

        soup = card_soup(render_macro, card_params())
        heading = soup.find("h3", class_="nhsuk-heading-xs")
        assert heading is not None
        assert heading.text.strip() == "Test Heading"

    def test_description_and_caption_are_correct(self, render_macro):
        """Test that description and caption are rendered correctly."""

        soup = card_soup(render_macro, card_params())
        description_p = soup.find("p", class_="nhsuk-card__description")
        assert description_p is not None
        assert description_p.contents[0].text == "123"

        caption_span = description_p.find("span", class_="nhsuk-card__caption")
        assert caption_span is not None
        assert caption_span.text.strip() == "children"

    def test_html_is_escaped(self, render_macro):
        """Test that HTML is escaped."""

        soup = card_soup(render_macro, card_params_with_html())
        heading = soup.find("h3", class_="nhsuk-heading-xs")
        assert heading is not None
        assert heading.text.strip() == "<strong>Test Heading</strong>"

        description_p = soup.find("p", class_="nhsuk-card__description")
        assert description_p is not None
        assert description_p.contents[0].text == "<p>123</p>"

        caption_span = description_p.find("span", class_="nhsuk-card__caption")
        assert caption_span is not None
        assert caption_span.text.strip() == "<strong>children</strong>"
