import json
import logging
from urllib.parse import unquote

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
from markupsafe import Markup

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
from mavis.reporting.helpers.mavis_helper import mavis_url
from mavis.reporting.helpers.secondary_nav_helper import generate_secondary_nav_items
from mavis.reporting.models.organisation import Organisation

logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)


@main.before_request
def stub_mavis_data():
    g.api_client = MavisApiClient(app=current_app, session=session)


def _parse_navigation_counts_cookie(request):
    nav_counts = {}
    if cookie_value := request.cookies.get("mavis_navigation_counts"):
        try:
            decoded_value = unquote(cookie_value)
            nav_counts = json.loads(decoded_value)
            current_app.logger.info(f"Navigation counts from cookie: {nav_counts}")
        except (json.JSONDecodeError, ValueError):
            current_app.logger.warning(
                f"Failed to parse navigation counts cookie: {cookie_value}"
            )
    else:
        current_app.logger.info("No mavis_navigation_counts cookie found")
    return nav_counts


def _build_nav_item(href, text, nav_counts, active=False, count_key=None):
    item = {"href": href, "active": active}

    if count_key and (count := nav_counts.get(count_key)) is not None:
        badge = (
            '<span class="app-count">'
            '<span class="nhsuk-u-visually-hidden"> (</span>'
            f"{count}"
            '<span class="nhsuk-u-visually-hidden">)</span>'
            "</span>"
        )
        item["html"] = Markup(f"{text}{badge}")
        item["classes"] = "app-header__navigation-item--with-count"
    else:
        item["text"] = text

    return item


@main.context_processor
def inject_mavis_data():
    """Inject common data into the template context."""
    env = Environment(current_app.config["ENVIRONMENT"])
    nav_counts = _parse_navigation_counts_cookie(request)

    navigation_items = [
        _build_nav_item(
            url_for("main.dashboard"), "Programmes", nav_counts, active=True
        ),
        _build_nav_item(mavis_url(current_app, "/sessions"), "Sessions", nav_counts),
        _build_nav_item(mavis_url(current_app, "/patients"), "Children", nav_counts),
        _build_nav_item(
            mavis_url(current_app, "/consent-forms"),
            "Unmatched responses",
            nav_counts,
            count_key="unmatched_consent_responses",
        ),
        _build_nav_item(
            mavis_url(current_app, "/school-moves"),
            "School moves",
            nav_counts,
            count_key="school_moves",
        ),
        _build_nav_item(mavis_url(current_app, "/vaccines"), "Vaccines", nav_counts),
        _build_nav_item(
            mavis_url(current_app, "/imports"),
            "Imports",
            nav_counts,
            count_key="imports",
        ),
        _build_nav_item(mavis_url(current_app, "/team"), "Your team", nav_counts),
    ]

    return {
        "app_title": "Manage vaccinations in schools",
        "app_environment": env,
        "navigation_items": navigation_items,
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

    if form.validate_on_submit():
        if form.data_type.data == DataTypeForm.CHILD_RECORDS:
            return redirect(mavis_helper.mavis_url(current_app, "/programmes"))
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


@main.route("/organisation/<code>/download", methods=["GET", "POST"])
@auth_helper.login_required
def download(code):
    organisation = Organisation.get_from_session(session)
    if organisation.code != code:
        return redirect(url_for("main.download", code=organisation.code))

    form = DownloadForm(
        g.api_client.get_programmes(),
        g.api_client.get_variables(),
    )

    if request.method == "POST" and form.validate_on_submit():
        api_response = g.api_client.download_totals_csv(
            form.programme.data, form.variables.data
        )

        headers = {}
        content_disposition = api_response.headers.get("Content-Disposition")
        if content_disposition:
            headers["Content-Disposition"] = content_disposition

        return Response(api_response.content, mimetype="text/csv", headers=headers)

    return render_template(
        "download.jinja",
        organisation=organisation,
        academic_year=get_current_academic_year_range(),
        last_updated_time=get_last_updated_time(),
        form=form,
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
        organisation=organisation,
        programmes=g.api_client.get_programmes(),
        year_groups=g.api_client.get_year_groups(),
        genders=g.api_client.get_genders(),
        academic_year=get_current_academic_year_range(),
        data=data,
        current_filters=filters,
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
