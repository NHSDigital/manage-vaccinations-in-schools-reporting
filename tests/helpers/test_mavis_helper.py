import json
from http import HTTPStatus
from unittest.mock import patch

import pytest
from flask import current_app
from werkzeug.exceptions import Unauthorized

from mavis.reporting.helpers import mavis_helper


def test_mavis_url_with_just_path(app):
    with app.app_context():
        app.config["MAVIS_ROOT_URL"] = "http://i.am.mavis:4000/"
        url = mavis_helper.mavis_url(current_app, "/some/path.json")
        assert url == "http://i.am.mavis:4000/some/path.json"


def test_mavis_url_with_path_and_params(app):
    with app.app_context():
        app.config["MAVIS_ROOT_URL"] = "http://i.am.mavis:4000/"
        url = mavis_helper.mavis_url(
            current_app, "/some/path.json", {"param1": "param 1 value"}
        )
        assert url == "http://i.am.mavis:4000/some/path.json?param1=param+1+value"


def test_mavis_url_with_path_and_multiple_params(app):
    with app.app_context():
        app.config["MAVIS_ROOT_URL"] = "http://i.am.mavis:4000/"
        url = mavis_helper.mavis_url(
            current_app,
            "/some/path.json",
            {"param1": "param 1 value", "param2": 123, "param3": "something else"},
        )
        assert (
            url
            == "http://i.am.mavis:4000/some/path.json?param1=param+1+value&param2=123&param3=something+else"
        )


def test_that_mavis_url_applies_url_encoding_to_params(app):
    with app.app_context():
        app.config["MAVIS_ROOT_URL"] = "http://i.am.mavis:4000/"
        url = mavis_helper.mavis_url(
            current_app,
            "/some/path.json",
            {"return_url": "https://some.other.domain/login?token=123"},
        )
        assert (
            url
            == "http://i.am.mavis:4000/some/path.json?return_url=https%3A%2F%2Fsome.other.domain%2Flogin%3Ftoken%3D123"
        )


class MockResponse:
    def __init__(self, **kwargs):
        self.status_code = kwargs.get("status_code", None)
        self.text = kwargs.get("text", None)
        self.json_obj = kwargs.get("json_obj", None)

    def json(self):
        return self.json_obj or json.loads(self.text or "{}")


def test_that_verify_auth_code_is_called_correctly(
    app,
):
    with app.app_context():
        app.config["MAVIS_ROOT_URL"] = "http://i.am.mavis:4000/"
        app.config["CLIENT_ID"] = "my secret key"

        expected_url = "http://i.am.mavis:4000/api/reporting/authorize"
        expected_body = {
            "client_id": "my secret key",
            "code": "mock_code",
            "grant_type": "authorization_code",
        }
        expected_headers = {
            "Accept": "application/json; charset=utf-8",
            "Content-type": "application/json; charset=utf-8",
        }
        mock_response = MockResponse(
            status_code=200, json_obj={"jwt": "myjwt", "data": "mydata"}
        )
        with patch(
            "mavis.reporting.helpers.mavis_helper.post_request",
            return_value=mock_response,
        ) as mocked_request:
            with patch("jwt.decode", return_value={"data": "my data"}):
                mavis_helper.verify_auth_code("mock_code", app)

                mocked_request.assert_called_once_with(
                    expected_url, body=expected_body, headers=expected_headers
                )


def test_that_api_call_is_called_correctly(
    app,
):
    mock_session = {"jwt": "myjwt"}
    with app.app_context():
        app.config["MAVIS_ROOT_URL"] = "http://i.am.mavis:4000/"
        app.config["CLIENT_SECRET"] = "my secret key"

        mock_response = MockResponse(
            status_code=200, json_obj={"jwt": "myjwt", "data": "mydata"}
        )
        with patch(
            "mavis.reporting.helpers.mavis_helper.get_request",
            return_value=mock_response,
        ) as mocked_request:
            mavis_helper.api_call(
                app,
                mock_session,
                "/my/api/path",
                {"param1": "param 1 value", "param2": 222},
            )

            expected_url = (
                "http://i.am.mavis:4000/my/api/path?param1=param+1+value&param2=222"
            )
            expected_headers = {
                "Authorization": "Bearer myjwt",
                "Accept": "application/json; charset=utf-8",
                "Content-type": "application/json; charset=utf-8",
            }
            mocked_request.assert_called_once_with(
                expected_url, headers=expected_headers
            )


def test_that_an_unauthorized_api_call_raises_an_exception_and_clears_the_session(
    app,
):
    for code in [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN]:
        mock_session = {"jwt": "myjwt"}
        with app.app_context():
            app.config["MAVIS_ROOT_URL"] = "http://i.am.mavis:4000/"
            app.config["CLIENT_SECRET"] = "my secret key"

            mock_response = MockResponse(
                status_code=code, json_obj={"jwt": "myjwt", "data": "mydata"}
            )
            with patch(
                "mavis.reporting.helpers.mavis_helper.get_request",
                return_value=mock_response,
            ):
                with pytest.raises(Unauthorized):
                    mavis_helper.api_call(
                        app,
                        mock_session,
                        "/my/api/path",
                        {"param1": "param 1 value", "param2": 222},
                    )

                    assert not mock_session


def test_login_and_return_after_redirects_to_the_mavis_start_path_correctly(
    app,
):
    with app.app_context():
        app.config["MAVIS_ROOT_URL"] = "http://i.am.mavis:4000/"

        return_value = mavis_helper.login_and_return_after(
            app, "http://this.app/some/path"
        )

        assert return_value.status_code == HTTPStatus.FOUND
        assert (
            return_value.location
            == "http://i.am.mavis:4000/start?redirect_uri=http%3A%2F%2Fthis.app%2Fsome%2Fpath"
        )
