from flask import Flask, redirect
from mavis_reporting.config import config
from mavis_reporting.config.jinja2 import configure_jinja2

import os


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, static_url_path="/reporting/assets")
    app.config.from_object(config[config_name])

    configure_jinja2(app)

    # ruff: noqa: PLC0415
    from mavis_reporting.views import main

    app.register_blueprint(main, url_prefix="/reporting")

    @app.route("/")
    def root():
        return redirect("/reporting")

    return app
