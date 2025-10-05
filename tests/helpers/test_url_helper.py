import pytest

from mavis.reporting.helpers import url_helper
from tests.conftest import MockRequest


@pytest.mark.parametrize(
    "input_url,param,expected",
    [
        (
            "https://some.domain/path/file.name?q=search+string",
            "q",
            "https://some.domain/path/file.name",
        ),
        (
            "https://some.domain/path/file.name?q=search%20string&other_param=othervalue",
            "q",
            "https://some.domain/path/file.name?other_param=othervalue",
        ),
        (
            "https://some.domain/path/file.name?q=search%20string&b=bbb&a=aaa",
            "q",
            "https://some.domain/path/file.name?b=bbb&a=aaa",
        ),
        (
            "https://some.domain/path/file.name?q=search+string&b=bbb&a=aaa&",
            "c",
            "https://some.domain/path/file.name?q=search+string&b=bbb&a=aaa&",
        ),
    ],
    ids=["single_param", "keeps_other_params", "preserves_order", "param_not_present"],
)
def test_url_without_param(input_url, param, expected):
    assert url_helper.url_without_param(input_url, param) == expected


def test_externalise_url_uses_root_url(app):
    request = MockRequest(
        host_url="http://my.server/", full_path="/reports/full/path?query=val1"
    )
    app.config["ROOT_URL"] = "https://mavis.test/reportsg"

    assert (
        url_helper.externalise_current_url(app, request)
        == "https://mavis.test/reports/full/path?query=val1"
    )


def test_externalise_url_uses_host_url(app):
    request = MockRequest(
        host_url="http://my.server/", full_path="/reports/full/path?query=val1"
    )
    app.config["ROOT_URL"] = None

    assert (
        url_helper.externalise_current_url(app, request)
        == "http://my.server/reports/full/path?query=val1"
    )
