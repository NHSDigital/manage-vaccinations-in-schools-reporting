# ruff: noqa: PLR2004

from http import HTTPStatus

from bs4 import BeautifulSoup

from mavis.reporting.helpers import auth_helper
from tests.conftest import MockResponse
from tests.helpers import mock_user_info

MOCK_LOCAL_AUTHORITIES_DATA = [
    {
        "local_authority_official_name": "Test County Council",
        "cohort": 100,
        "consent_no_response": 10,
        "consent_given": 80,
        "vaccinated": 75,
    },
    {
        "local_authority_official_name": "Test Borough Council",
        "cohort": 200,
        "consent_no_response": 20,
        "consent_given": 160,
        "vaccinated": 150,
    },
]


def _get_local_authorities_page(app, client, mock_mavis_get_request):
    app.config["ROOT_URL"] = "http://mavis.test/reports/"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        with client.session_transaction() as session:
            auth_helper.log_user_in(mock_user_info(), session)

        mock_mavis_get_request(MockResponse(json_obj=MOCK_LOCAL_AUTHORITIES_DATA))
        response = client.get("/reports/team/r1l/local-authorities")

    return response


def test_local_authorities_view_has_expected_table_headers(
    app, client, mock_mavis_get_request
):
    response = _get_local_authorities_page(app, client, mock_mavis_get_request)
    assert response.status_code == HTTPStatus.OK

    soup = BeautifulSoup(response.data.decode("utf-8"), "html.parser")

    headers = [th.get_text(strip=True) for th in soup.find_all("th")]

    assert "Local authority" in headers
    assert "Cohort" in headers
    assert "No response" in headers
    assert "Consent given" in headers
    assert "Vaccinated" in headers


def test_local_authorities_view_renders_data_in_table(
    app, client, mock_mavis_get_request
):
    response = _get_local_authorities_page(app, client, mock_mavis_get_request)
    soup = BeautifulSoup(response.data.decode("utf-8"), "html.parser")

    table_body = soup.find("tbody")
    assert table_body is not None
    rows = table_body.find_all("tr")

    assert len(rows) == 2

    first_row_cells = [td.get_text(strip=True) for td in rows[0].find_all("td")]
    assert "Test County Council" in first_row_cells

    second_row_cells = [td.get_text(strip=True) for td in rows[1].find_all("td")]
    assert "Test Borough Council" in second_row_cells
