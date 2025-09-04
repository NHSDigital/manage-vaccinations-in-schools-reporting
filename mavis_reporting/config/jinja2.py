import os

from jinja2 import FileSystemLoader, ChoiceLoader, PackageLoader, ChainableUndefined
from mavis_reporting.helpers.static_file_helper import static
from mavis_reporting.helpers.number_helper import thousands, percentage


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

    # Add the static function to allow for cache busting of static files
    app.jinja_env.globals["static"] = static

    # Add custom filters
    app.jinja_env.filters["thousands"] = thousands
    app.jinja_env.filters["percentage"] = percentage

    return app
