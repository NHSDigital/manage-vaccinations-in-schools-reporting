import pytest

from mavis.reporting.api_client.client import MavisApiClient
from mavis.reporting.helpers.mavis_helper import MavisApiError
from tests.conftest import MockResponse


@pytest.fixture()
def api_client(app):
    return MavisApiClient(
        app=app,
        session={
            "jwt": "myjwt",
            "cis2_info": {
                "team_workgroup": "r1l",
            },
        },
    )


def test_missing_cohort_field_raises_error(api_client, mock_mavis_get_request):
    mock_mavis_get_request(MockResponse(json_obj={"some_field": "value"}))

    with pytest.raises(MavisApiError, match="missing 'cohort' field"):
        api_client.get_vaccination_data()


def test_valid_vaccination_data(api_client, mock_mavis_get_request):
    expected_cohort = 100
    mock_mavis_get_request(
        MockResponse(
            json_obj={
                "cohort": expected_cohort,
                "vaccinated": 80,
                "not_vaccinated": 20,
                "vaccinated_by_sais": 70,
                "vaccinated_elsewhere_declared": 5,
                "vaccinated_elsewhere_recorded": 3,
                "vaccinated_previously": 2,
                "consent_given": 60,
                "no_consent": 40,
                "consent_no_response": 30,
                "consent_refused": 8,
                "consent_conflicts": 2,
            }
        )
    )

    result = api_client.get_vaccination_data()

    assert result["cohort"] == expected_cohort
    assert "vaccinated_percentage" in result
    assert "consent_refused_percentage" in result
    assert "consent_conflicts_percentage" in result


class TestGetYearGroupsForProgramme:
    def test_flu_returns_all_year_groups(self, api_client):
        result = api_client.get_year_groups_for_programme("flu")
        values = [yg["value"] for yg in result]
        assert values == [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
        ]

    def test_hpv_returns_years_8_to_11(self, api_client):
        result = api_client.get_year_groups_for_programme("hpv")
        values = [yg["value"] for yg in result]
        assert values == ["8", "9", "10", "11"]

    def test_menacwy_returns_years_9_to_11(self, api_client):
        result = api_client.get_year_groups_for_programme("menacwy")
        values = [yg["value"] for yg in result]
        assert values == ["9", "10", "11"]

    def test_td_ipv_returns_years_9_to_11(self, api_client):
        result = api_client.get_year_groups_for_programme("td_ipv")
        values = [yg["value"] for yg in result]
        assert values == ["9", "10", "11"]

    def test_unknown_programme_returns_empty_list(self, api_client):
        result = api_client.get_year_groups_for_programme("unknown")
        assert result == []


class TestGetSchoolsData:
    def test_valid_schools_data(self, api_client, mock_mavis_get_request):
        mock_mavis_get_request(
            MockResponse(
                json_obj=[
                    {
                        "school_urn": "100000",
                        "school_name": "Test School",
                        "cohort": 100,
                        "vaccinated": 80,
                        "not_vaccinated": 20,
                    }
                ]
            )
        )

        result = api_client.get_schools_data()

        assert len(result) == 1
        assert result[0]["school_name"] == "Test School"

    def test_non_list_response_raises_error(self, api_client, mock_mavis_get_request):
        mock_mavis_get_request(MockResponse(json_obj={"some_field": "value"}))

        with pytest.raises(MavisApiError, match="must be a list"):
            api_client.get_schools_data()


class TestGetProgrammes:
    def test_returns_all_when_no_programme_types(self, app):
        client = MavisApiClient(
            app=app, session={"jwt": "x", "cis2_info": {}, "programme_types": []}
        )
        result = client.get_programmes()
        values = [p["value"] for p in result]
        assert values == ["flu", "hpv", "menacwy", "td_ipv"]

    def test_filters_by_programme_types(self, app):
        client = MavisApiClient(
            app=app,
            session={"jwt": "x", "programme_types": ["flu", "hpv"]},
        )
        result = client.get_programmes()
        values = [p["value"] for p in result]
        assert values == ["flu", "hpv"]

    def test_returns_all_when_cis2_info_missing(self, app):
        client = MavisApiClient(app=app, session={"jwt": "x"})
        result = client.get_programmes()
        values = [p["value"] for p in result]
        assert values == ["flu", "hpv", "menacwy", "td_ipv"]


class TestGetFormOptions:
    def test_returns_file_formats(self, api_client, mock_mavis_get_request):
        mock_mavis_get_request(
            MockResponse(json_obj={"file_formats": ["mavis", "systm_one"]})
        )

        result = api_client.get_form_options("r1l")

        assert result["file_formats"] == ["mavis", "systm_one"]


class TestCreateExport:
    def test_creates_export_and_returns_id(
        self, api_client, mock_mavis_post_request
    ):
        mock_mavis_post_request(
            MockResponse(
                status_code=201,
                json_obj={"id": "abc-123", "status": "pending"},
            )
        )

        result = api_client.create_export(
            workgroup="r1l",
            programme_type="flu",
            file_format="mavis",
            academic_year=2024,
        )

        assert result["id"] == "abc-123"
        assert result["status"] == "pending"

    def test_creates_export_with_date_range(
        self, api_client, mock_mavis_post_request
    ):
        mock_mavis_post_request(
            MockResponse(
                status_code=201,
                json_obj={"id": "abc-456", "status": "pending"},
            )
        )

        result = api_client.create_export(
            workgroup="r1l",
            programme_type="flu",
            file_format="mavis",
            academic_year=2024,
            date_from="2024-09-01",
            date_to="2025-03-31",
        )

        assert result["id"] == "abc-456"


class TestGetExportStatus:
    def test_returns_pending_status(self, api_client, mock_mavis_get_request):
        mock_mavis_get_request(
            MockResponse(json_obj={"status": "pending", "expires_at": None})
        )

        result = api_client.get_export_status("abc-123")

        assert result["status"] == "pending"

    def test_returns_ready_status_with_download_url(
        self, api_client, mock_mavis_get_request
    ):
        mock_mavis_get_request(
            MockResponse(
                json_obj={
                    "status": "ready",
                    "download_url": "http://rails.test/api/reporting/exports/abc-123/download",
                    "expires_at": "2025-03-17T04:00:00Z",
                }
            )
        )

        result = api_client.get_export_status("abc-123")

        assert result["status"] == "ready"
        assert "download_url" in result
