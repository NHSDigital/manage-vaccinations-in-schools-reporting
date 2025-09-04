from flask import url_for

from mavis.reporting.models.organisation import Organisation


def generate_breadcrumb_items(organisations: list[Organisation]):
    items = [
        {
            "text": "Home",
            "href": url_for("main.index"),
        }
    ]
    for organisation in organisations:
        match organisation.__class__.__name__:
            case "Region":
                items.append(
                    {
                        "text": organisation.name,
                        "href": url_for("main.region", code=organisation.code),
                    }
                )
            case "Provider":
                items.append(
                    {
                        "text": organisation.name,
                        "href": url_for("main.provider", code=organisation.code),
                    }
                )
            case "School":
                items.append(
                    {
                        "text": organisation.name,
                        "href": url_for("main.school", code=organisation.code),
                    }
                )
            case _:
                raise ValueError(
                    f"Invalid organisation type: {organisation.__class__.__name__}"
                )

    return items
