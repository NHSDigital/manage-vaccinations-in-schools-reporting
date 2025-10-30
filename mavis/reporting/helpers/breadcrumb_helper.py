from flask import current_app, url_for

from mavis.reporting.helpers.mavis_helper import mavis_public_url


def generate_breadcrumb_items():
    return [
        {
            "text": "Home",
            "href": mavis_public_url(current_app, "/"),
        },
        {
            "text": "Reports",
            "href": url_for("main.dashboard"),
        },
    ]
