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

from mavis.reporting.helpers import auth_helper, breadcrumb_helper
from mavis.reporting.models.organisation import Organisation

logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)


@main.before_request
def stub_mavis_data():
    g.programmes = [
        {"value": "hpv", "text": "HPV", "checked": True},
        {"value": "flu", "text": "Flu"},
        {"value": "menacwy", "text": "MenACWY"},
        {"value": "td-ipv", "text": "Td/IPV"},
    ]

    g.year_groups = [
        {"value": "0", "text": "Reception"},
        {"value": "1", "text": "Year 1"},
        {"value": "2", "text": "Year 2"},
        {"value": "3", "text": "Year 3"},
        {"value": "4", "text": "Year 4"},
        {"value": "5", "text": "Year 5"},
        {"value": "6", "text": "Year 6"},
        {"value": "7", "text": "Year 7"},
        {"value": "8", "text": "Year 8"},
        {"value": "9", "text": "Year 9"},
        {"value": "10", "text": "Year 10"},
        {"value": "11", "text": "Year 11"},
    ]

    g.genders = [
        {"value": "male", "text": "Male"},
        {"value": "female", "text": "Female"},
        {"value": "other", "text": "Other"},
        {"value": "unknown", "text": "Unknown"},
    ]


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
    return redirect(url_for("main.monthly_vaccinations", code=organisation.code))


@main.route("/download", methods=["GET", "POST"])
@auth_helper.login_required
def download():
    if request.method == "POST":
        return redirect(url_for("main.download"))

    return render_template("download.jinja", programmes=g.programmes)


@main.route("/organisation/<code>/monthly-vaccinations")
@auth_helper.login_required
def monthly_vaccinations(code):
    organisation = Organisation.get_from_session(session)
    if organisation.code != code:
        return redirect(url_for("main.monthly_vaccinations", code=organisation.code))

    breadcrumb_items = breadcrumb_helper.generate_breadcrumb_items(organisation)
    secondary_navigation_items = [
        {
            "text": "Monthly vaccinations",
            "href": url_for("main.dashboard"),
        },
    ]

    fake_data = [
        {"month": "September", "year": 2025, "number_of_vaccinations": 102},
        {"month": "October", "year": 2025, "number_of_vaccinations": 86},
        {"month": "November", "year": 2025, "number_of_vaccinations": 324},
        {"month": "December", "year": 2025, "number_of_vaccinations": 299},
    ]

    return render_template(
        "monthly_vaccinations.jinja",
        organisation=organisation,
        data=fake_data,
        programmes=g.programmes,
        year_groups=g.year_groups,
        genders=g.genders,
        breadcrumb_items=breadcrumb_items,
        secondary_navigation_items=secondary_navigation_items,
    )


@main.errorhandler(404)
def page_not_found(_error):
    return render_template("errors/404.html"), 404


@main.route("/healthcheck")
def healthcheck():
    return HealthCheck().run()
