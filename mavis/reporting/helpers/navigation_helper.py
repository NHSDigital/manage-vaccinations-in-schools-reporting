import json
from urllib.parse import unquote

from flask import current_app, url_for
from markupsafe import Markup

from mavis.reporting.helpers.mavis_helper import mavis_url


def parse_navigation_counts_cookie(request):
    nav_counts = {}
    if cookie_value := request.cookies.get("mavis_navigation_counts"):
        try:
            decoded_value = unquote(cookie_value)
            nav_counts = json.loads(decoded_value)
            current_app.logger.info(f"Navigation counts from cookie: {nav_counts}")
        except (json.JSONDecodeError, ValueError):
            current_app.logger.warning(
                f"Failed to parse navigation counts cookie: {cookie_value}"
            )
    else:
        current_app.logger.info("No mavis_navigation_counts cookie found")
    return nav_counts


def build_nav_item(href, text, nav_counts, active=False, count_key=None):
    item = {"href": href, "active": active}

    if count_key and (count := nav_counts.get(count_key)) is not None:
        badge = (
            '<span class="app-count">'
            '<span class="nhsuk-u-visually-hidden"> (</span>'
            f"{count}"
            '<span class="nhsuk-u-visually-hidden">)</span>'
            "</span>"
        )
        item["html"] = Markup(f"{text}{badge}")
        item["classes"] = "app-header__navigation-item--with-count"
    else:
        item["text"] = text

    return item


def build_navigation_items(request):
    nav_counts = parse_navigation_counts_cookie(request)
    return [
        build_nav_item(url_for("main.dashboard"), "Reports", nav_counts, active=True),
        build_nav_item(mavis_url(current_app, "/sessions"), "Sessions", nav_counts),
        build_nav_item(mavis_url(current_app, "/patients"), "Children", nav_counts),
        build_nav_item(
            mavis_url(current_app, "/consent-forms"),
            "Unmatched responses",
            nav_counts,
            count_key="unmatched_consent_responses",
        ),
        build_nav_item(
            mavis_url(current_app, "/school-moves"),
            "School moves",
            nav_counts,
            count_key="school_moves",
        ),
        build_nav_item(mavis_url(current_app, "/vaccines"), "Vaccines", nav_counts),
        build_nav_item(
            mavis_url(current_app, "/imports"),
            "Imports",
            nav_counts,
            count_key="imports",
        ),
        build_nav_item(mavis_url(current_app, "/team"), "Your team", nav_counts),
    ]
