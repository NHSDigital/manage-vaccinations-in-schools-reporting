import os

from flask import Flask, redirect

from mavis.reporting.config import config
from mavis.reporting.config.jinja2 import configure_jinja2


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ["FLASK_ENV"]

    app = Flask(__name__, static_url_path="/reporting/assets")
    app.config.from_object(config[config_name])

    # Set cache timeout for static files (1 hour in development, 1 year in production)
    if config_name == "development":
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 3600  # 1 hour
    else:
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 31536000  # 1 year

    configure_jinja2(app)

    # ruff: noqa: PLC0415
    from mavis.reporting.views import main

    app.register_blueprint(main, url_prefix="/reporting")

    @app.route("/")
    def root():
        return redirect("/reporting")

    return app
