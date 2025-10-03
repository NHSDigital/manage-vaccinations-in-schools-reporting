from http import HTTPStatus

import pytest
from flask import current_app
from werkzeug.exceptions import Unauthorized

from mavis.reporting.helpers import mavis_helper
from mavis.reporting.helpers.mavis_helper import MavisApiError
from tests.conftest import MockResponse


def test_mavis_url_with_just_path():
    url = mavis_helper.mavis_url(current_app, "/some/path.json")
    assert url == "http://mavis.test/some/path.json"


def test_mavis_url_with_params():
    url = mavis_helper.mavis_url(
        current_app, "/some/path.json", {"param1": "param 1 value"}
    )
    assert url == "http://mavis.test/some/path.json?param1=param+1+value"


def test_mavis_url_with_multiple_params():
    url = mavis_helper.mavis_url(
        current_app,
        "/some/path.json",
        {"param1": "param 1 value", "param2": 123, "param3": "something else"},
    )
    assert (
        url
        == "http://mavis.test/some/path.json?param1=param+1+value&param2=123&param3=something+else"
    )


def test_mavis_url_encodes_params():
    url = mavis_helper.mavis_url(
        current_app,
        "/some/path.json",
        {"return_url": "https://some.other.domain/login?token=123"},
    )
    assert (
        url
        == "http://mavis.test/some/path.json?return_url=https%3A%2F%2Fsome.other.domain%2Flogin%3Ftoken%3D123"
    )


def test_mavis_url_with_list_params():
    url = mavis_helper.mavis_url(
        current_app, "/some/path.json", {"year_group": ["8", "9"]}
    )
    assert (
        url == "http://mavis.test/some/path.json?year_group%5B%5D=8&year_group%5B%5D=9"
    )


@pytest.mark.parametrize(
    "status_code",
    [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN],
    ids=["unauthorized", "forbidden"],
)
def test_unauthorized_api_call_clears_session(app, mock_mavis_get_request, status_code):
    mock_session = {"jwt": "myjwt"}
    mock_mavis_get_request(
        MockResponse(
            status_code=status_code, json_obj={"jwt": "myjwt", "data": "mydata"}
        )
    )

    with pytest.raises(Unauthorized):
        mavis_helper.api_call(
            app,
            mock_session,
            "/my/api/path",
            {"param1": "param 1 value", "param2": 222},
        )

    assert not mock_session


def test_parse_json_empty_body():
    with pytest.raises(MavisApiError, match="Empty response body") as exc_info:
        mavis_helper.parse_json_response(MockResponse(content=b""), "Test context")

    assert exc_info.value.status_code == HTTPStatus.OK


def test_parse_json_invalid():
    with pytest.raises(MavisApiError, match="Invalid JSON") as exc_info:
        mavis_helper.parse_json_response(
            MockResponse(text="not valid json"), "Test context"
        )

    assert exc_info.value.status_code == HTTPStatus.OK


def test_parse_json_valid():
    result = mavis_helper.parse_json_response(
        MockResponse(json_obj={"key": "value"}), "Test context"
    )

    assert result == {"key": "value"}


def test_api_call_non_2xx_status(app, mock_mavis_get_request):
    mock_mavis_get_request(
        MockResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            text="Internal Server Error",
        )
    )

    with pytest.raises(MavisApiError, match="500") as exc_info:
        mavis_helper.api_call(app, {"jwt": "myjwt"}, "/my/api/path")

    assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def test_verify_auth_code_unauthorized(app, mock_mavis_post_request):
    mock_mavis_post_request(MockResponse(status_code=HTTPStatus.UNAUTHORIZED))

    with pytest.raises(Unauthorized):
        mavis_helper.verify_auth_code("mock_code", app)


def test_verify_auth_code_internal_server_error(app, mock_mavis_post_request):
    mock_mavis_post_request(MockResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR))

    with pytest.raises(MavisApiError, match="500") as exc_info:
        mavis_helper.verify_auth_code("mock_code", app)

    assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert exc_info.value.message == "Authorization response: 500"


def test_verify_auth_code_missing_jwt(app, mock_mavis_post_request):
    mock_mavis_post_request(MockResponse(json_obj={"data": "mydata"}))

    with pytest.raises(MavisApiError, match="missing 'jwt' field"):
        mavis_helper.verify_auth_code("mock_code", app)
