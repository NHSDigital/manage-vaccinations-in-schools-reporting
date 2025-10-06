import os

import sentry_sdk
from flask import Flask, redirect

from mavis.reporting.config import config
from mavis.reporting.config.jinja2 import configure_jinja2

if dsn := os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=dsn,
        # Add data like request headers and IP for users, if applicable; see
        # https://docs.sentry.io/platforms/python/data-management/data-collected/
        # for more info
        send_default_pii=True,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        # To collect profiles for all profile sessions,
        # set `profile_session_sample_rate` to 1.0.
        profile_session_sample_rate=1.0,
        # Profiles will be automatically collected while
        # there is an active span.
        profile_lifecycle="trace",
        # Enable logs to be sent to Sentry
        enable_logs=True,
    )


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ["FLASK_ENV"].lower().strip()

    app = Flask(__name__, static_url_path="/reports/assets")
    try:
        app.config.from_object(config[config_name])
    except KeyError:
        app.config.from_object(config["default"])

    # Set cache timeout for static files (1 hour in development, 1 year in production)
    if config_name == "development":
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 3600  # 1 hour
    else:
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 31536000  # 1 year

    configure_jinja2(app)

    # ruff: noqa: PLC0415
    from mavis.reporting.views import main

    app.register_blueprint(main, url_prefix="/reports")

    @app.route("/")
    def root():
        return redirect("/reports")

    return app
