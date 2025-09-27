from flask import url_for


def generate_secondary_nav_items(organisation_code: str, current_page: str):
    return [
        {
            "text": "Vaccinations",
            "href": url_for("main.vaccinations", code=organisation_code),
            "current": current_page == "vaccinations",
        },
        {
            "text": "Download data",
            "href": url_for("main.start_download", code=organisation_code),
            "current": current_page == "download",
        },
    ]
