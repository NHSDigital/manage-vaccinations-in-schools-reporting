import json
from urllib.parse import unquote_plus

from flask import current_app
from markupsafe import Markup

FALLBACK_ITEMS = [
    {"path": "/schools", "title": "Schools"},
    {"path": "/patients", "title": "Children"},
    {"path": "/sessions", "title": "Sessions"},
    {"path": "/vaccines", "title": "Vaccines"},
    {"path": "/consent-forms", "title": "Unmatched responses"},
    {"path": "/school-moves", "title": "School moves"},
    {"path": "/reports", "title": "Reports"},
    {"path": "/imports", "title": "Imports"},
    {"path": "/team", "title": "Your team"},
]


def build_navigation_items(request):
    items = FALLBACK_ITEMS
    if cookie_value := request.cookies.get("mavis_navigation_items"):
        try:
            decoded_value = unquote_plus(cookie_value)
            if parsed := json.loads(decoded_value):
                items = parsed
        except (json.JSONDecodeError, ValueError):
            current_app.logger.warning(
                f"Failed to parse navigation items cookie: {cookie_value}"
            )

    nav_items: list[dict] = []
    for item in items:
        nav_item: dict = {"href": item["path"], "text": item["title"]}

        if item["path"] == "/reports":
            nav_item["current"] = True

        if (count := item.get("count")) is not None:
            badge = (
                '<span class="app-count">'
                '<span class="nhsuk-u-visually-hidden"> (</span>'
                f"{count}"
                '<span class="nhsuk-u-visually-hidden">)</span>'
                "</span>"
            )
            nav_item["html"] = Markup(f"{item['title']}{badge}")
            nav_item["classes"] = "app-header__navigation-item--with-count"
            del nav_item["text"]

        nav_items.append(nav_item)

    return nav_items
