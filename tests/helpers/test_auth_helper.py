from datetime import datetime, timedelta, timezone
from typing import cast

import pytest
from flask.sessions import SessionMixin

from mavis.reporting.helpers import auth_helper
from tests.helpers import mock_user_info


@pytest.fixture()
def user_data():
    return mock_user_info()


@pytest.fixture()
def logged_in_session(user_data):
    session = {}
    auth_helper.log_user_in(user_data, cast(SessionMixin, session))
    return session


def test_log_user_in_sets_last_visit(logged_in_session):
    assert logged_in_session["last_visit"] is not None
    now = datetime.now().astimezone(timezone.utc)
    time_diff = now - logged_in_session["last_visit"]
    assert time_diff < timedelta(seconds=1)


def test_log_user_in_sets_cis2_info(logged_in_session, user_data):
    assert logged_in_session["cis2_info"] == user_data["jwt_data"]["cis2_info"]


def test_log_user_in_sets_user(logged_in_session, user_data):
    assert logged_in_session["user"] == user_data["jwt_data"]["user"]


def test_log_user_in_sets_jwt(logged_in_session, user_data):
    assert logged_in_session["jwt"] is not None

    jwt_payload = auth_helper.decode_jwt(logged_in_session["jwt"])
    assert jwt_payload["data"]["user"]["id"] == user_data["jwt_data"]["user"]["id"]
    assert (
        jwt_payload["data"]["user"]["reporting_api_session_token"]
        == user_data["jwt_data"]["user"]["reporting_api_session_token"]
    )
    assert jwt_payload["data"]["cis2_info"] == user_data["jwt_data"]["cis2_info"]


def test_log_user_in_sets_programme_types(logged_in_session, user_data):
    assert (
        logged_in_session["programme_types"] == user_data["jwt_data"]["programme_types"]
    )
