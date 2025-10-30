import os
from urllib.parse import quote

import sentry_sdk
from flask import Flask, redirect, request
from werkzeug.exceptions import Unauthorized

from mavis.reporting.helpers import mavis_helper, url_helper
from mavis.reporting.helpers.environment_helper import EnvType
from mavis.reporting.jinja2_config import configure_jinja2

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

    app.config["CLIENT_ID"] = os.environ["CLIENT_ID"]
    app.config["CLIENT_SECRET"] = os.environ["CLIENT_SECRET"]
    app.config["MAVIS_ROOT_URL"] = os.environ["MAVIS_ROOT_URL"]
    app.config["ROOT_URL"] = os.environ["ROOT_URL"]
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

    app.config["DEBUG"] = False
    app.config["ENVIRONMENT"] = EnvType.PROD
    app.config["LOG_LEVEL"] = "INFO"
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 31536000
    app.config["SESSION_TTL_SECONDS"] = 600
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["TESTING"] = False

    if config_name == "development":
        app.config["DEBUG"] = True
        app.config["ENVIRONMENT"] = EnvType.DEV
        app.config["LOG_LEVEL"] = "DEBUG"
        app.config["MAVIS_BACKEND_URL"] = os.environ["MAVIS_BACKEND_URL"]
    elif config_name == "test":
        app.config["DEBUG"] = True
        app.config["ENVIRONMENT"] = EnvType.TEST
        app.config["LOG_LEVEL"] = "DEBUG"
        app.config["TESTING"] = True
    elif config_name == "staging":
        app.config["ENVIRONMENT"] = EnvType.STAGING

    configure_jinja2(app)

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(_error):
        return_url = url_helper.externalise_current_url(app, request)
        target_url = mavis_helper.mavis_public_url(
            app,
            "/start?redirect_uri=" + quote(return_url),
        )
        return redirect(str(target_url))

    # ruff: noqa: PLC0415
    from mavis.reporting.views import main

    app.register_blueprint(main, url_prefix="/reports")

    if config_name == "development":
        # In development: Proxy all non-/reports routes to Mavis
        # In production: Load balancer handles this
        from mavis.reporting.dev_proxy import proxy_to_mavis

        all_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"]

        app.route("/", defaults={"path": ""})(proxy_to_mavis)
        app.route("/<path:path>", methods=all_methods)(proxy_to_mavis)

    return app
