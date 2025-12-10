from http import HTTPStatus

from mavis.reporting.forms.data_type_form import DataTypeForm
from mavis.reporting.helpers import auth_helper, mavis_helper
from tests.helpers import mock_user_info


def test_start_download_redirects_to_new_child_record_form(app, client):
    app.config["ROOT_URL"] = "http://mavis.test/reports/"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        with client.session_transaction() as session:
            auth_helper.log_user_in(mock_user_info(), session)

        response = client.post(
            "/reports/team/r1l/start-download",
            data={"data_type": DataTypeForm.CHILD_RECORDS},
            follow_redirects=False,
        )

        expected_location = mavis_helper.mavis_public_url(
            app, "/vaccination-report/new"
        )

        assert response.status_code == HTTPStatus.FOUND
        assert response.headers["Location"] == expected_location
