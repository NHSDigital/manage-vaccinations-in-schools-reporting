from flask import (
    Blueprint,
    render_template,
    request,
    session,
    current_app,
    redirect,
    url_for,
)

from healthcheck import HealthCheck

from werkzeug.exceptions import Unauthorized

import logging

from mavis.reporting.helpers import mavis_helper, auth_helper, url_helper

logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)


@main.context_processor
def inject_mavis_data():
    """Inject common data into the template context."""
    return {
        "site_title": "Manage vaccinations in schools",
    }


@main.route("/")
@auth_helper.login_required
def index():
    return render_template("default.jinja")


@main.route("/download", methods=["GET", "POST"])
@auth_helper.login_required
def download():
    if request.method == "POST":
        return redirect(url_for("main.download"))

    programmes = [
        {"code": "hpv", "name": "HPV"},
        {"code": "flu", "name": "Flu"},
        {"code": "menacwy", "name": "MenACWY"},
        {"code": "td-ipv", "name": "Td/IPV"},
    ]
    return render_template("download.jinja", programmes=programmes)


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
        return_url = url_helper.externalise_current_url(current_app, request)
        return mavis_helper.login_and_return_after(current_app, return_url)

    data = response.json()
    return render_template("api_call.jinja", response=response, data=data)
