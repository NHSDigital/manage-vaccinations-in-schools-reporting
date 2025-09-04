from mavis.reporting.helpers import url_helper


def test_url_without_param_with_a_single_param_removes_the_param():
    assert (
        url_helper.url_without_param(
            "https://some.domain/path/file.name?q=search+string", "q"
        )
        == "https://some.domain/path/file.name"
    )


def test_url_without_param_with_multiple_params_removes_the_correct_param():
    assert (
        url_helper.url_without_param(
            "https://some.domain/path/file.name?q=search%20string&other_param=othervalue",
            "q",
        )
        == "https://some.domain/path/file.name?other_param=othervalue"
    )


def test_url_without_param_preserves_the_order_of_params_which_are_not_removed():
    assert (
        url_helper.url_without_param(
            "https://some.domain/path/file.name?q=search%20string&b=bbb&a=aaa",
            "q",
        )
        == "https://some.domain/path/file.name?b=bbb&a=aaa"
    )


def test_url_without_param_with_a_single_param_that_is_not_present_makes_no_changes():
    assert (
        url_helper.url_without_param(
            "https://some.domain/path/file.name?q=search+string&b=bbb&a=aaa&", "c"
        )
        == "https://some.domain/path/file.name?q=search+string&b=bbb&a=aaa&"
    )


class MockRequest:
    def __init__(self, **kwargs):
        self.host_url = kwargs.get("host_url", None)
        self.full_path = kwargs.get("full_path", None)


def test_that_externalise_current_url_uses_root_url_if_given(app):
    request = MockRequest(
        host_url="http://my.server/", full_path="/reporting/full/path?query=val1"
    )
    with app.app_context():
        app.config["ROOT_URL"] = "https://i.am.mavis:4000/reporting"
        assert (
            url_helper.externalise_current_url(app, request)
            == "https://i.am.mavis:4000/reporting/full/path?query=val1"
        )


def test_that_externalise_current_url_uses_request_host_url_if_root_url_not_given(app):
    request = MockRequest(
        host_url="http://my.server/", full_path="/reporting/full/path?query=val1"
    )
    with app.app_context():
        app.config["ROOT_URL"] = None
        assert (
            url_helper.externalise_current_url(app, request)
            == "http://my.server/reporting/full/path?query=val1"
        )
