import logging

from flask import (
    Blueprint,
    Response,
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
from mavis.reporting.forms.download_form import DownloadForm
from mavis.reporting.helpers import auth_helper, mavis_helper
from mavis.reporting.helpers.breadcrumb_helper import generate_breadcrumb_items
from mavis.reporting.helpers.date_helper import (
    get_current_academic_year_range,
    get_last_updated_time,
)
from mavis.reporting.helpers.environment_helper import Environment
from mavis.reporting.helpers.navigation_helper import build_navigation_items
from mavis.reporting.helpers.secondary_nav_helper import generate_secondary_nav_items
from mavis.reporting.models.team import Team

logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)


@main.before_request
def stub_mavis_data():
    g.api_client = MavisApiClient(app=current_app, session=session)


@main.context_processor
def inject_mavis_data():
    """Inject common data into the template context."""
    env = Environment(current_app.config["ENVIRONMENT"])

    return {
        "app_title": "Manage vaccinations in schools",
        "app_environment": env,
        "navigation_items": build_navigation_items(request),
        "service_guide_url": "https://guide.manage-vaccinations-in-schools.nhs.uk",
    }


@main.route("/")
@main.route("/dashboard")
@auth_helper.login_required
def dashboard():
    team = Team.get_from_session(session)
    return redirect(url_for("main.vaccinations", workgroup=team.workgroup))


@main.route("/team/<workgroup>/start-download", methods=["GET", "POST"])
@auth_helper.login_required
def start_download(workgroup):
    team = Team.get_from_session(session)
    if team.workgroup != workgroup:
        return redirect(url_for("main.start_download", workgroup=team.workgroup))

    form = DataTypeForm()

    if form.validate_on_submit():
        if form.data_type.data == DataTypeForm.CHILD_RECORDS:
            return redirect(mavis_helper.mavis_public_url(current_app, "/programmes"))
        elif form.data_type.data == DataTypeForm.AGGREGATE_DATA:
            return redirect(url_for("main.download", workgroup=team.workgroup))
        else:
            raise ValueError("Invalid data type")

    breadcrumb_items = generate_breadcrumb_items()

    selected_item_text = "Download"
    secondary_navigation_items = generate_secondary_nav_items(
        team.workgroup,
        current_page="download",
    )

    return render_template(
        "start-download.jinja",
        team=team,
        academic_year=get_current_academic_year_range(),
        breadcrumb_items=breadcrumb_items,
        selected_item_text=selected_item_text,
        secondary_navigation_items=secondary_navigation_items,
        form=form,
    )


@main.route("/team/<workgroup>/download", methods=["GET", "POST"])
@auth_helper.login_required
def download(workgroup):
    team = Team.get_from_session(session)
    if team.workgroup != workgroup:
        return redirect(url_for("main.download", workgroup=team.workgroup))

    form = DownloadForm(
        g.api_client.get_programmes(),
        g.api_client.get_variables(),
    )

    if request.method == "POST" and form.validate_on_submit():
        api_response = g.api_client.download_totals_csv(
            form.programme.data, team.workgroup, form.variables.data
        )

        headers = {}
        content_disposition = api_response.headers.get("Content-Disposition")
        if content_disposition:
            headers["Content-Disposition"] = content_disposition

        return Response(api_response.content, mimetype="text/csv", headers=headers)

    return render_template(
        "download.jinja",
        team=team,
        academic_year=get_current_academic_year_range(),
        last_updated_time=get_last_updated_time(),
        form=form,
    )


@main.route("/team/<workgroup>/vaccinations")
@auth_helper.login_required
def vaccinations(workgroup):
    team = Team.get_from_session(session)
    if team.workgroup != workgroup:
        return redirect(url_for("main.vaccinations", workgroup=team.workgroup))

    breadcrumb_items = generate_breadcrumb_items()

    selected_item_text = "Vaccinations"
    secondary_navigation_items = generate_secondary_nav_items(
        team.workgroup,
        current_page="vaccinations",
    )

    filters = {}

    filters["team_workgroup"] = team.workgroup
    filters["programme"] = request.args.get("programme") or "hpv"

    gender_values = request.args.getlist("gender")
    if gender_values:
        filters["gender"] = gender_values

    year_group_values = request.args.getlist("year-group")
    if year_group_values:
        filters["year_group"] = year_group_values

    data = g.api_client.get_vaccination_data(filters)

    return render_template(
        "vaccinations.jinja",
        team=team,
        programmes=g.api_client.get_programmes(),
        year_groups=g.api_client.get_year_groups(),
        genders=g.api_client.get_genders(),
        academic_year=get_current_academic_year_range(),
        data=data,
        current_filters=filters,
        breadcrumb_items=breadcrumb_items,
        selected_item_text=selected_item_text,
        secondary_navigation_items=secondary_navigation_items,
        last_updated_time=get_last_updated_time(),
    )


@main.errorhandler(404)
def page_not_found(_error):
    return render_template("errors/404.html"), 404


@main.route("/healthcheck")
def healthcheck():
    return HealthCheck().run()
