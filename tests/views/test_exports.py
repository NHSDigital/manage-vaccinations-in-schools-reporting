from http import HTTPStatus
from unittest.mock import MagicMock, patch

from mavis.reporting.helpers import auth_helper
from tests.helpers import mock_user_info


def _log_in(client, app):
    with app.app_context():
        with client.session_transaction() as sess:
            auth_helper.log_user_in(mock_user_info(), sess)


def _mock_api_client(file_formats=None, programmes=None, export=None, export_status=None):
    mock = MagicMock()
    if file_formats is not None:
        mock.get_form_options.return_value = {"file_formats": file_formats}
    if programmes is not None:
        mock.get_programmes.return_value = programmes
    if export is not None:
        mock.create_export.return_value = export
    if export_status is not None:
        mock.get_export_status.return_value = export_status
    return mock


def test_exports_new_get_renders_form(app, client):
    app.config["WTF_CSRF_ENABLED"] = False

    mock_instance = _mock_api_client(
        file_formats=["mavis", "systm_one"],
        programmes=[{"value": "flu", "text": "Flu"}],
    )
    with patch("mavis.reporting.views.MavisApiClient", return_value=mock_instance):
        _log_in(client, app)

        response = client.get("/reports/team/r1l/exports/new")

        assert response.status_code == HTTPStatus.OK
        assert b"Request vaccination export" in response.data


def test_exports_new_post_redirects_to_status(app, client):
    app.config["WTF_CSRF_ENABLED"] = False

    mock_instance = _mock_api_client(
        file_formats=["mavis", "systm_one"],
        programmes=[{"value": "flu", "text": "Flu"}],
        export={"id": "abc-123", "status": "pending"},
    )
    with patch("mavis.reporting.views.MavisApiClient", return_value=mock_instance):
        _log_in(client, app)

        response = client.post(
            "/reports/team/r1l/exports/new",
            data={
                "programme_type": "flu",
                "file_format": "mavis",
                "academic_year": 2024,
            },
            follow_redirects=False,
        )

        assert response.status_code == HTTPStatus.FOUND
        assert "/exports/abc-123" in response.headers["Location"]


def test_export_status_shows_pending(app, client):
    mock_instance = _mock_api_client(
        export_status={"status": "pending", "expires_at": None},
    )
    with patch("mavis.reporting.views.MavisApiClient", return_value=mock_instance):
        _log_in(client, app)

        response = client.get("/reports/team/r1l/exports/abc-123")

        assert response.status_code == HTTPStatus.OK
        assert b"being prepared" in response.data


def test_export_status_shows_download_when_ready(app, client):
    mock_instance = _mock_api_client(
        export_status={
            "status": "ready",
            "download_url": "http://rails.test/api/reporting/exports/abc-123/download",
            "expires_at": "2025-03-17T04:00:00Z",
        },
    )
    with patch("mavis.reporting.views.MavisApiClient", return_value=mock_instance):
        _log_in(client, app)

        response = client.get("/reports/team/r1l/exports/abc-123")

        assert response.status_code == HTTPStatus.OK
        assert b"Download" in response.data


def test_export_status_shows_failed(app, client):
    mock_instance = _mock_api_client(
        export_status={"status": "failed", "expires_at": None},
    )
    with patch("mavis.reporting.views.MavisApiClient", return_value=mock_instance):
        _log_in(client, app)

        response = client.get("/reports/team/r1l/exports/abc-123")

        assert response.status_code == HTTPStatus.OK
        assert b"Export failed" in response.data


def test_start_download_child_records_redirects_to_exports_new(app, client):
    app.config["WTF_CSRF_ENABLED"] = False

    _log_in(client, app)

    response = client.post(
        "/reports/team/r1l/start-download",
        data={"data_type": "child-records"},
        follow_redirects=False,
    )

    assert response.status_code == HTTPStatus.FOUND
    assert "/exports/new" in response.headers["Location"]
