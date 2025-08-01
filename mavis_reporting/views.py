from flask import (
    Blueprint,
    render_template,
    request,
    session,
    current_app,
)

from healthcheck import HealthCheck

from werkzeug.exceptions import Unauthorized

import logging

from mavis_reporting.helpers import mavis_helper
from mavis_reporting.helpers import auth_helper

logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)


@main.route("/")
@auth_helper.login_required
def index():
    return render_template("default.jinja")


@main.errorhandler(404)
def page_not_found():
    return render_template("errors/404.html"), 404


@main.route("/healthcheck")
def healthcheck():
    return HealthCheck().run()


@main.route("/api-call/")
@auth_helper.login_required
def api_call():
    response = None
    try:
        response = mavis_helper.api_call(current_app, session, "/api/reporting/totals")
    except Unauthorized:
        return mavis_helper.login_and_return_after(current_app, request.url)

    data = response.json()
    return render_template("api_call.jinja", response=response, data=data)
