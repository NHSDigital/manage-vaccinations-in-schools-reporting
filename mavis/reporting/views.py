import logging

from flask import (
    Blueprint,
    current_app,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from healthcheck import HealthCheck

from mavis.reporting.api_client.client import MavisApiClient
from mavis.reporting.forms.data_type_form import DataTypeForm
from mavis.reporting.helpers import auth_helper
from mavis.reporting.helpers.breadcrumb_helper import generate_breadcrumb_items
from mavis.reporting.helpers.date_helper import get_current_academic_year_range
from mavis.reporting.helpers.secondary_nav_helper import generate_secondary_nav_items
from mavis.reporting.models.organisation import Organisation

logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)


@main.before_request
def stub_mavis_data():
    g.api_client = MavisApiClient(app=current_app, session=session)


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


@main.route("/organisation/<code>/start-download", methods=["GET", "POST"])
@auth_helper.login_required
def start_download(code):
    organisation = Organisation.get_from_session(session)
    if organisation.code != code:
        return redirect(url_for("main.start_download", code=organisation.code))

    form = DataTypeForm()

    if request.method == "POST" and form.validate_on_submit():
        if form.data_type.data == DataTypeForm.CHILD_RECORDS:
            return redirect(current_app.config["MAVIS_ROOT_URL"] + "/programmes")
        elif form.data_type.data == DataTypeForm.AGGREGATE_DATA:
            return redirect(url_for("main.download", code=organisation.code))
        else:
            raise ValueError("Invalid data type")

    breadcrumb_items = generate_breadcrumb_items()

    selected_item_text = "Download"
    secondary_navigation_items = generate_secondary_nav_items(
        organisation.code,
        current_page="download",
    )

    return render_template(
        "start-download.jinja",
        organisation=organisation,
        academic_year=get_current_academic_year_range(),
        breadcrumb_items=breadcrumb_items,
        selected_item_text=selected_item_text,
        secondary_navigation_items=secondary_navigation_items,
        form=form,
    )


@main.route("/organisation/<code>/download")
@auth_helper.login_required
def download(code):
    organisation = Organisation.get_from_session(session)
    if organisation.code != code:
        return redirect(url_for("main.download", code=organisation.code))

    return render_template(
        "download.jinja",
        organisation=organisation,
        programmes=g.api_client.get_programmes(),
        academic_year=get_current_academic_year_range(),
    )


@main.route("/organisation/<code>/vaccinations")
@auth_helper.login_required
def vaccinations(code):
    organisation = Organisation.get_from_session(session)
    if organisation.code != code:
        return redirect(url_for("main.vaccinations", code=organisation.code))

    breadcrumb_items = generate_breadcrumb_items()

    selected_item_text = "Vaccinations"
    secondary_navigation_items = generate_secondary_nav_items(
        organisation.code,
        current_page="vaccinations",
    )

    filters = {}
    if request.args.get("programme"):
        filters["programme"] = request.args.get("programme")
    if request.args.get("year_group"):
        filters["year_group"] = request.args.get("year_group")
    if request.args.get("gender"):
        filters["gender"] = request.args.get("gender")
    if request.args.get("from_date"):
        filters["from_date"] = request.args.get("from_date")
    if request.args.get("to_date"):
        filters["to_date"] = request.args.get("to_date")

    data = g.api_client.get_vaccination_data(filters)

    return render_template(
        "vaccinations.jinja",
        organisation=organisation,
        programmes=g.api_client.get_programmes(),
        year_groups=g.api_client.get_year_groups(),
        genders=g.api_client.get_genders(),
        academic_year=get_current_academic_year_range(),
        data=data,
        breadcrumb_items=breadcrumb_items,
        selected_item_text=selected_item_text,
        secondary_navigation_items=secondary_navigation_items,
    )


@main.errorhandler(404)
def page_not_found(_error):
    return render_template("errors/404.html"), 404


@main.route("/healthcheck")
def healthcheck():
    return HealthCheck().run()
