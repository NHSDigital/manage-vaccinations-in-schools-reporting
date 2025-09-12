import logging

from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from healthcheck import HealthCheck

from mavis.reporting.api_client.client import MavisApiClient
from mavis.reporting.helpers import auth_helper
from mavis.reporting.helpers.breadcrumb_helper import generate_breadcrumb_items
from mavis.reporting.helpers.secondary_nav_helper import generate_secondary_nav_items
from mavis.reporting.models.organisation import Organisation

logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)


@main.before_request
def stub_mavis_data():
    g.api_client = MavisApiClient()


@main.context_processor
def inject_mavis_data():
    """Inject common data into the template context."""
    return {
        "site_title": "Manage vaccinations in schools",
    }


@main.route("/")
@main.route("/dashboard")
@auth_helper.login_required
def dashboard():
    organisation = Organisation.get_from_session(session)
    return redirect(url_for("main.vaccinations", code=organisation.code))


@main.route("/organisation/<code>/download", methods=["GET", "POST"])
@auth_helper.login_required
def download(code):
    organisation = Organisation.get_from_session(session)
    if organisation.code != code:
        return redirect(url_for("main.download", code=organisation.code))

    if request.method == "POST":
        return redirect(url_for("main.download", code=organisation.code))

    breadcrumb_items = generate_breadcrumb_items(organisation)
    secondary_navigation_items = generate_secondary_nav_items(
        organisation.code,
        current_page="download",
    )

    return render_template(
        "download.jinja",
        organisation=organisation,
        programmes=g.api_client.get_programmes(),
        breadcrumb_items=breadcrumb_items,
        secondary_navigation_items=secondary_navigation_items,
    )


@main.route("/organisation/<code>/vaccinations")
@auth_helper.login_required
def vaccinations(code):
    organisation = Organisation.get_from_session(session)
    if organisation.code != code:
        return redirect(url_for("main.vaccinations", code=organisation.code))

    breadcrumb_items = generate_breadcrumb_items(organisation)
    secondary_navigation_items = generate_secondary_nav_items(
        organisation.code,
        current_page="vaccinations",
    )

    data = g.api_client.get_vaccination_data()

    return render_template(
        "vaccinations.jinja",
        organisation=organisation,
        programmes=g.api_client.get_programmes(),
        year_groups=g.api_client.get_year_groups(),
        genders=g.api_client.get_genders(),
        data=data,
        breadcrumb_items=breadcrumb_items,
        secondary_navigation_items=secondary_navigation_items,
    )


@main.errorhandler(404)
def page_not_found(_error):
    return render_template("errors/404.html"), 404


@main.route("/healthcheck")
def healthcheck():
    return HealthCheck().run()
