# ruff: noqa: PLR2004

from http import HTTPStatus

from bs4 import BeautifulSoup

from mavis.reporting.helpers import auth_helper
from tests.helpers import mock_user_info


def test_download_view_has_expected_programmes_and_variables(app, client):
    """Test that the download view displays the correct programmes and variables."""
    app.config["ROOT_URL"] = "http://mavis.test/reports/"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        with client.session_transaction() as session:
            auth_helper.log_user_in(mock_user_info(), session)

        response = client.get("/reports/team/r1l/download")

        assert response.status_code == HTTPStatus.OK

        soup = BeautifulSoup(response.data.decode("utf-8"), "html.parser")

        # Check that the expected programmes are present
        # (filtered by user's programme_types: ["flu", "hpv"])
        programme_radios = soup.find_all(
            "input", {"name": "programme", "type": "radio"}
        )
        programme_values = [radio.get("value") for radio in programme_radios]

        assert len(programme_values) == 2
        assert "flu" in programme_values
        assert "hpv" in programme_values

        # Check that the expected variables are present
        variable_checkboxes = soup.find_all(
            "input", {"name": "variables", "type": "checkbox"}
        )
        variable_values = [checkbox.get("value") for checkbox in variable_checkboxes]

        assert len(variable_values) == 4
        assert "local_authority" in variable_values
        assert "school" in variable_values
        assert "year_group" in variable_values
        assert "gender" in variable_values


def test_download_view_shows_all_programmes_when_no_programme_types_in_session(
    app, client
):
    """Test that all programmes are shown when programme_types is empty."""
    app.config["ROOT_URL"] = "http://mavis.test/reports/"
    app.config["WTF_CSRF_ENABLED"] = False

    user_info = mock_user_info()

    # Set programme_types to empty list to give user access to all programmes
    user_info["jwt_data"]["programme_types"] = []

    with app.app_context():
        with client.session_transaction() as session:
            auth_helper.log_user_in(user_info, session)

        response = client.get("/reports/team/r1l/download")

        assert response.status_code == HTTPStatus.OK

        soup = BeautifulSoup(response.data.decode("utf-8"), "html.parser")

        # Check that all programmes are present when programme_types is empty
        programme_radios = soup.find_all(
            "input", {"name": "programme", "type": "radio"}
        )
        programme_values = [radio.get("value") for radio in programme_radios]

        assert len(programme_values) == 4
        assert "flu" in programme_values
        assert "hpv" in programme_values
        assert "menacwy" in programme_values
        assert "td_ipv" in programme_values
