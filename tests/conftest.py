import json
import os
import sys
from http import HTTPStatus

from requests.exceptions import JSONDecodeError as RequestsJSONDecodeError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from mavis.reporting import create_app
from tests.helpers import create_random_token


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "MAVIS_ROOT_URL": "http://mavis.test/",
            "TESTING": True,
            "CLIENT_ID": create_random_token(),
            "CLIENT_SECRET": create_random_token(),
        }
    )
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def app_ctx(app):
    with app.app_context():
        yield app


@pytest.fixture()
def mock_mavis_get_request(monkeypatch):
    def _mock(response):
        monkeypatch.setattr(
            "mavis.reporting.helpers.mavis_helper.get_request",
            lambda *_args, **_kwargs: response,
        )

    return _mock


@pytest.fixture()
def mock_mavis_post_request(monkeypatch):
    def _mock(response):
        monkeypatch.setattr(
            "mavis.reporting.helpers.mavis_helper.post_request",
            lambda *_args, **_kwargs: response,
        )

    return _mock


class MockResponse:
    def __init__(self, **kwargs):
        self.status_code = kwargs.get("status_code", HTTPStatus.OK)
        self.text = kwargs.get("text", "")
        self.json_obj = kwargs.get("json_obj")
        provided_content = kwargs.get("content")
        if provided_content is not None:
            self.content = provided_content
        elif self.json_obj is not None:
            self.content = json.dumps(self.json_obj).encode()
        elif self.text:
            self.content = self.text.encode()
        else:
            self.content = b""
        self.ok = (
            self.status_code >= HTTPStatus.OK
            and self.status_code < HTTPStatus.MULTIPLE_CHOICES
            if self.status_code
            else True
        )

    def json(self):
        if self.json_obj is not None:
            return self.json_obj
        if not self.text:
            return {}
        try:
            return json.loads(self.text)
        except json.JSONDecodeError as e:
            raise RequestsJSONDecodeError(str(e), "", 0)


class MockRequest:
    def __init__(self, **kwargs):
        self.host_url = kwargs.get("host_url")
        self.full_path = kwargs.get("full_path")
