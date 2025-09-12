from typing import TYPE_CHECKING

from flask import current_app, url_for

if TYPE_CHECKING:
    from mavis.reporting.models.organisation import Organisation


def generate_breadcrumb_items(organisation: "Organisation"):
    return [
        {
            "text": "Home",
            "href": current_app.config["MAVIS_ROOT_URL"],
        },
        {
            "text": "Reporting",
            "href": url_for("main.dashboard"),
        },
        {
            "text": organisation.name,
            "href": url_for("main.vaccinations", code=organisation.code),
        },
    ]
