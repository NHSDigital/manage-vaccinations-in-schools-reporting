from os import urandom

from datetime import datetime, timedelta, timezone

from mavis_reporting.helpers import auth_helper


def configure_app(app):
    app.config.update(
        {
            "TESTING": True,
            "CLIENT_ID": random_token(),
            "CLIENT_SECRET": random_token(),
        }
    )


def random_token():
    return urandom(16).hex()


def mock_user_info():
    jwt_data = {
        "user": {
            "id": 1,
            "email": "nurse.joy@example.com",
            "created_at": "2025-06-16T11:09:24.289+01:00",
            "updated_at": "2025-07-04T10:11:36.100+01:00",
            "provider": None,
            "uid": None,
            "given_name": "Nurse",
            "family_name": "Joy",
            "fallback_role": "nurse",
        },
        "cis2_info": {
            "selected_org": {"code": "R1L", "name": "SAIS Organisation 1"},
            "selected_role": {
                "code": "S8000:G8000:R8001",
                "workgroups": ["schoolagedimmunisations"],
            },
        },
    }
    jwt_data["user"]["session_token"] = random_token()
    jwt_data["user"]["reporting_api_session_token"] = random_token()
    return {
        "jwt_data": jwt_data,
        "user_nav": {
            "items": [
                {"text": "Test User", "icon": True},
                {"href": "/logout", "text": "Log out"},
            ]
        },
    }


def test_that_log_user_in_sets_last_visit_to_now(app):
    with app.app_context():
        configure_app(app)
        mock_session = {}
        auth_helper.log_user_in(mock_user_info(), mock_session)
        assert mock_session["last_visit"] is not None
        assert datetime.now().astimezone(timezone.utc) - mock_session[
            "last_visit"
        ] < timedelta(seconds=1)


def test_that_log_user_in_copies_cis2_info_from_the_given_data(app):
    mock_session = {}
    with app.app_context():
        configure_app(app)
        auth_helper.log_user_in(mock_user_info(), mock_session)
        assert mock_session["cis2_info"] == mock_user_info()["jwt_data"]["cis2_info"]


def test_that_log_user_in_copies_user_from_the_given_data(app):
    mock_session = {}
    fake_data = mock_user_info()

    with app.app_context():
        configure_app(app)
        auth_helper.log_user_in(fake_data, mock_session)
        assert mock_session["user"] == fake_data["jwt_data"]["user"]


def test_that_log_user_in_sets_minimal_jwt(
    app,
):
    mock_session = {}
    fake_data = mock_user_info()
    with app.app_context():
        configure_app(app)
        auth_helper.log_user_in(fake_data, mock_session)
        assert mock_session["jwt"] is not None
        jwt_payload = auth_helper.decode_jwt(mock_session["jwt"])

        assert jwt_payload["data"]["user"]["id"] == fake_data["jwt_data"]["user"]["id"]
        assert (
            jwt_payload["data"]["user"]["reporting_api_session_token"]
            == fake_data["jwt_data"]["user"]["reporting_api_session_token"]
        )
        assert jwt_payload["data"]["cis2_info"] == fake_data["jwt_data"]["cis2_info"]
