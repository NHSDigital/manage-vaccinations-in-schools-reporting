from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import pytest

from mavis.reporting.helpers.auth_helper import log_user_in
from tests.conftest import MockResponse
from tests.helpers import mock_user_info


@pytest.fixture(autouse=True)
def _app_context(app):
    with app.app_context():
        yield


@pytest.fixture
def consent_response():
    return {
        "cohort": 546,
        "consent_given": 456,
        "consent_no_response": 90,
        "consent_conflicts": 10,
        "parent_refused_consent": 20,
        "child_refused_vaccination": 15,
    }


@pytest.fixture
def authenticated_session(client):
    with client.session_transaction() as session:
        log_user_in(mock_user_info(), session)
    return client


@pytest.fixture
def mock_api_call(monkeypatch):
    mock_calls = []

    def _mock(response):
        mock_response = MockResponse(json_obj=response)

        def api_call_wrapper(*args, **kwargs):
            mock_calls.append((args, kwargs))
            return mock_response

        monkeypatch.setattr(
            "mavis.reporting.helpers.mavis_helper.api_call",
            api_call_wrapper,
        )
        return mock_calls

    return _mock


def test_consents_route_requires_authentication(client):
    with client.session_transaction() as session:
        session["user_id"] = None

    response = client.get("/reports/team/r1l/consents", follow_redirects=False)
    assert response.status_code == HTTPStatus.FOUND
    redirect_to = response.headers["Location"]
    assert redirect_to.startswith("http://mavis.test/")
    assert "/start" in redirect_to


def test_consents_route_with_default_filters(
    authenticated_session, consent_response, mock_api_call
):
    mock_api_call(consent_response)
    response = authenticated_session.get("/reports/team/r1l/consents")
    assert response.status_code == HTTPStatus.OK
    assert b"consents.jinja" in response.data or b"Consents" in response.data


def test_consents_route_with_custom_filters(
    authenticated_session, consent_response, mock_api_call
):
    mock_calls = mock_api_call(consent_response)
    response = authenticated_session.get(
        "/reports/team/r1l/consents?programme=flu&gender=1&gender=2&year-group=7&year-group=8"
    )
    assert response.status_code == HTTPStatus.OK

    params = mock_calls[0][1]["params"]
    assert params["programme"] == "flu"
    assert params["gender"] == ["1", "2"]
    assert params["year_group"] == ["7", "8"]


def test_consents_route_calls_api_client_correctly(
    authenticated_session, consent_response, mock_api_call
):
    mock_calls = mock_api_call(consent_response)
    response = authenticated_session.get("/reports/team/r1l/consents")
    assert response.status_code == HTTPStatus.OK

    assert len(mock_calls) == 1
    assert mock_calls[0][0][2] == "/api/reporting/totals"
    assert "params" in mock_calls[0][1]


def test_consents_route_redirects_wrong_workgroup(authenticated_session):
    response = authenticated_session.get(
        "/reports/team/WRONG/consents", follow_redirects=False
    )
    assert response.status_code == HTTPStatus.FOUND
    redirect_to = response.headers["Location"]
    assert "/team/r1l/consents" in redirect_to


def test_consents_route_renders_correct_template(
    authenticated_session, consent_response, mock_api_call
):
    mock_api_call(consent_response)
    response = authenticated_session.get("/reports/team/r1l/consents")
    assert response.status_code == HTTPStatus.OK


def test_consents_route_with_expired_session_redirects(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["last_visit"] = datetime.now().astimezone(timezone.utc) - timedelta(
            hours=101
        )

    response = client.get("/reports/team/r1l/consents")
    assert response.status_code == HTTPStatus.FOUND
    redirect_to = response.headers["Location"]
    assert redirect_to.startswith("http://mavis.test/")
    assert "/start" in redirect_to


def test_consents_route_with_programme_filter(
    authenticated_session, consent_response, mock_api_call
):
    mock_calls = mock_api_call(consent_response)
    response = authenticated_session.get("/reports/team/r1l/consents?programme=menacwy")
    assert response.status_code == HTTPStatus.OK

    params = mock_calls[0][1]["params"]
    assert params["programme"] == "menacwy"


def test_consents_route_with_gender_filter(
    authenticated_session, consent_response, mock_api_call
):
    mock_calls = mock_api_call(consent_response)
    response = authenticated_session.get("/reports/team/r1l/consents?gender=1")
    assert response.status_code == HTTPStatus.OK

    params = mock_calls[0][1]["params"]
    assert params["gender"] == ["1"]


def test_consents_route_with_year_group_filter(
    authenticated_session, consent_response, mock_api_call
):
    mock_calls = mock_api_call(consent_response)
    response = authenticated_session.get("/reports/team/r1l/consents?year-group=9")
    assert response.status_code == HTTPStatus.OK

    params = mock_calls[0][1]["params"]
    assert params["year_group"] == ["9"]
