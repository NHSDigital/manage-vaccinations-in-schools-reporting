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
from mavis.reporting.forms.export_form import ExportForm
from mavis.reporting.helpers import auth_helper, mavis_helper
from mavis.reporting.helpers.breadcrumb_helper import generate_breadcrumb_items
from mavis.reporting.helpers.date_helper import (
    get_current_academic_year,
    get_current_academic_year_range,
    get_last_updated_time,
)
from mavis.reporting.helpers.environment_helper import HostingEnvironment
from mavis.reporting.helpers.filter_helper import build_report_filters
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
    return {
        "app_title": "Manage vaccinations in schools",
        "app_environment": HostingEnvironment,
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
            return redirect(url_for("main.exports_new", workgroup=team.workgroup))
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

    filters, year_groups = build_report_filters(team, g.api_client)
    data = g.api_client.get_vaccination_data(filters)

    return render_template(
        "vaccinations.jinja",
        team=team,
        programmes=g.api_client.get_programmes(),
        year_groups=year_groups,
        genders=g.api_client.get_genders(),
        academic_year=get_current_academic_year_range(),
        data=data,
        current_filters=filters,
        breadcrumb_items=breadcrumb_items,
        selected_item_text=selected_item_text,
        secondary_navigation_items=secondary_navigation_items,
        last_updated_time=get_last_updated_time(),
    )


@main.route("/team/<workgroup>/consent")
@auth_helper.login_required
def consent(workgroup):
    team = Team.get_from_session(session)
    if team.workgroup != workgroup:
        return redirect(url_for("main.consent", workgroup=team.workgroup))

    breadcrumb_items = generate_breadcrumb_items()

    selected_item_text = "Consent"
    secondary_navigation_items = generate_secondary_nav_items(
        team.workgroup,
        current_page="consent",
    )

    filters, year_groups = build_report_filters(team, g.api_client)
    data = g.api_client.get_vaccination_data(filters)

    return render_template(
        "consents.jinja",
        team=team,
        programmes=g.api_client.get_programmes(),
        year_groups=year_groups,
        genders=g.api_client.get_genders(),
        academic_year=get_current_academic_year_range(),
        data=data,
        current_filters=filters,
        breadcrumb_items=breadcrumb_items,
        selected_item_text=selected_item_text,
        secondary_navigation_items=secondary_navigation_items,
        last_updated_time=get_last_updated_time(),
    )


@main.route("/team/<workgroup>/schools")
@auth_helper.login_required
def schools(workgroup):
    team = Team.get_from_session(session)
    if team.workgroup != workgroup:
        return redirect(url_for("main.schools", workgroup=team.workgroup))

    breadcrumb_items = generate_breadcrumb_items()

    selected_item_text = "Schools"
    secondary_navigation_items = generate_secondary_nav_items(
        team.workgroup,
        current_page="schools",
    )

    filters, year_groups = build_report_filters(team, g.api_client)
    schools_data = g.api_client.get_schools_data(filters)

    return render_template(
        "schools.jinja",
        team=team,
        programmes=g.api_client.get_programmes(),
        year_groups=year_groups,
        genders=g.api_client.get_genders(),
        academic_year=get_current_academic_year_range(),
        schools_data=schools_data,
        current_filters=filters,
        breadcrumb_items=breadcrumb_items,
        selected_item_text=selected_item_text,
        secondary_navigation_items=secondary_navigation_items,
        last_updated_time=get_last_updated_time(),
    )


@main.route("/team/<workgroup>/exports/new", methods=["GET", "POST"])
@auth_helper.login_required
def exports_new(workgroup):
    team = Team.get_from_session(session)
    if team.workgroup != workgroup:
        return redirect(url_for("main.exports_new", workgroup=team.workgroup))

    form_options = g.api_client.get_form_options(team.workgroup)
    programmes = g.api_client.get_programmes()
    start_year = get_current_academic_year()
    academic_years = list(range(start_year, start_year - 3, -1))

    form = ExportForm(
        programmes=programmes,
        file_formats=form_options.get("file_formats", ["mavis", "systm_one"]),
        academic_years=academic_years,
    )

    if form.validate_on_submit():
        result = g.api_client.create_export(
            workgroup=team.workgroup,
            programme_type=form.programme_type.data,
            file_format=form.file_format.data,
            academic_year=form.academic_year.data,
            date_from=form.date_from.data.isoformat() if form.date_from.data else None,
            date_to=form.date_to.data.isoformat() if form.date_to.data else None,
        )
        return redirect(
            url_for("main.export_status", workgroup=team.workgroup, export_id=result["id"])
        )

    return render_template(
        "exports-new.jinja",
        team=team,
        form=form,
    )


@main.route("/team/<workgroup>/exports/<export_id>")
@auth_helper.login_required
def export_status(workgroup, export_id):
    team = Team.get_from_session(session)
    if team.workgroup != workgroup:
        return redirect(url_for("main.export_status", workgroup=team.workgroup, export_id=export_id))

    export = g.api_client.get_export_status(export_id)

    download_url = (
        url_for("main.export_download", workgroup=workgroup, export_id=export_id)
        if export.get("download_url")
        else None
    )

    return render_template(
        "export-status.jinja",
        team=team,
        workgroup=team.workgroup,
        export_id=export_id,
        export_status=export.get("status"),
        download_url=download_url,
        expires_at=export.get("expires_at"),
    )


@main.route("/team/<workgroup>/exports/<export_id>/download")
@auth_helper.login_required
def export_download(workgroup, export_id):
    team = Team.get_from_session(session)
    if team.workgroup != workgroup:
        return redirect(
            url_for("main.export_download", workgroup=team.workgroup, export_id=export_id)
        )

    url = mavis_helper.mavis_api_url(current_app, f"/api/reporting/exports/{export_id}/download")
    headers = {"Authorization": "Bearer " + session["jwt"]}
    response = mavis_helper.get_request(url, headers=headers)

    if response.is_redirect or response.status_code in (301, 302, 303, 307, 308):
        return redirect(response.headers["Location"])

    mavis_helper.validate_http_response(response, session=session)
    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers.get("Content-Type", "application/octet-stream"),
        headers={"Content-Disposition": response.headers.get("Content-Disposition", "attachment")},
    )


@main.errorhandler(404)
def page_not_found(_error):
    return render_template("errors/404.html"), 404


@main.route("/healthcheck")
def healthcheck():
    return HealthCheck().run()
