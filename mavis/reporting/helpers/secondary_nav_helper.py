from flask import url_for


def generate_secondary_nav_items(team_workgroup: str, current_page: str):
    return [
        {
            "text": "Vaccinations",
            "href": url_for("main.vaccinations", workgroup=team_workgroup),
            "current": current_page == "vaccinations",
        },
        {
            "text": "Consents",
            "href": url_for("main.consents", workgroup=team_workgroup),
            "current": current_page == "consents",
        },
        {
            "text": "Download data",
            "href": url_for("main.start_download", workgroup=team_workgroup),
            "current": current_page == "download",
        },
    ]
