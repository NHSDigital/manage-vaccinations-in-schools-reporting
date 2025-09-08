from datetime import datetime, timedelta, timezone
from typing import cast

from flask.sessions import SessionMixin

from mavis.reporting.helpers import auth_helper
from tests.helpers import mock_user_info


def test_that_log_user_in_sets_last_visit_to_now(app):
    with app.app_context():
        mock_session = {}
        auth_helper.log_user_in(mock_user_info(), cast(SessionMixin, mock_session))
        assert mock_session["last_visit"] is not None
        assert datetime.now().astimezone(timezone.utc) - mock_session[
            "last_visit"
        ] < timedelta(seconds=1)


def test_that_log_user_in_copies_cis2_info_from_the_given_data(app):
    mock_session = {}
    with app.app_context():
        auth_helper.log_user_in(mock_user_info(), cast(SessionMixin, mock_session))
        assert mock_session["cis2_info"] == mock_user_info()["jwt_data"]["cis2_info"]


def test_that_log_user_in_copies_user_from_the_given_data(app):
    mock_session = {}
    fake_data = mock_user_info()

    with app.app_context():
        auth_helper.log_user_in(fake_data, cast(SessionMixin, mock_session))
        assert mock_session["user"] == fake_data["jwt_data"]["user"]


def test_that_log_user_in_sets_minimal_jwt(
    app,
):
    mock_session = {}
    fake_data = mock_user_info()
    with app.app_context():
        auth_helper.log_user_in(fake_data, cast(SessionMixin, mock_session))
        assert mock_session["jwt"] is not None
        jwt_payload = auth_helper.decode_jwt(mock_session["jwt"])

        assert jwt_payload["data"]["user"]["id"] == fake_data["jwt_data"]["user"]["id"]
        assert (
            jwt_payload["data"]["user"]["reporting_api_session_token"]
            == fake_data["jwt_data"]["user"]["reporting_api_session_token"]
        )
        assert jwt_payload["data"]["cis2_info"] == fake_data["jwt_data"]["cis2_info"]
