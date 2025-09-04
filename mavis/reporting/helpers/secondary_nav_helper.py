from flask import url_for


def generate_secondary_nav_items(organisation_type: str, code: str, current_page: str):
    items = []
    match organisation_type:
        case "region":
            items.append(
                {
                    "text": "Overview",
                    "current": current_page == "region",
                    "href": url_for("main.region", code=code),
                }
            )
            items.append(
                {
                    "text": "Providers",
                    "current": current_page == "region_providers",
                    "href": url_for("main.region_providers", code=code),
                }
            )
        case "provider":
            items.append(
                {
                    "text": "Overview",
                    "current": current_page == "provider",
                    "href": url_for("main.provider", code=code),
                }
            )
            items.append(
                {
                    "text": "Schools",
                    "current": current_page == "provider_schools",
                    "href": url_for("main.provider_schools", code=code),
                }
            )
        case "school":
            items.append(
                {
                    "text": "Overview",
                    "current": current_page == "school",
                    "href": url_for("main.school", code=code),
                }
            )
        case _:
            raise ValueError(f"Invalid organisation type: {organisation_type}")

    return items
