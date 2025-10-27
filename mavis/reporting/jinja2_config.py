import os

from jinja2 import ChainableUndefined, ChoiceLoader, FileSystemLoader, PackageLoader

from mavis.reporting.helpers.date_helper import format_date_string
from mavis.reporting.helpers.mavis_helper import mavis_public_url
from mavis.reporting.helpers.number_helper import percentage, thousands
from mavis.reporting.helpers.static_file_helper import static


def configure_jinja2(app):
    app.jinja_options = {
        # This is needed to prevent jinja from throwing an error
        # when chained parameters are undefined
        "undefined": ChainableUndefined,
        "loader": ChoiceLoader(
            [
                FileSystemLoader(os.path.join(app.root_path, "templates")),
                PackageLoader(
                    "nhsuk_frontend_jinja", package_path="templates/nhsuk/components"
                ),
                PackageLoader(
                    "nhsuk_frontend_jinja", package_path="templates/nhsuk/macros"
                ),
                PackageLoader("nhsuk_frontend_jinja", package_path="templates"),
                PackageLoader("nhsuk_frontend_jinja"),
            ]
        ),
    }

    # Add functions for cache busting of static files
    # and for generating Mavis URLs
    app.jinja_env.globals["static"] = static
    app.jinja_env.globals["mavis_url"] = lambda path: mavis_public_url(app, path)

    # Add custom filters
    app.jinja_env.filters["thousands"] = thousands
    app.jinja_env.filters["percentage"] = percentage
    app.jinja_env.filters["date"] = format_date_string

    return app
