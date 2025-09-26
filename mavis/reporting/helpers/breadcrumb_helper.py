from flask import current_app, url_for


def generate_breadcrumb_items():
    return [
        {
            "text": "Home",
            "href": current_app.config["MAVIS_ROOT_URL"],
        },
        {
            "text": "Reports",
            "href": url_for("main.dashboard"),
        },
    ]
