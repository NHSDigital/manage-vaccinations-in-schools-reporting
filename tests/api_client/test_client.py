import pytest

from mavis.reporting.api_client.client import MavisApiClient
from mavis.reporting.helpers.mavis_helper import MavisApiError
from tests.conftest import MockResponse


@pytest.fixture()
def api_client(app):
    return MavisApiClient(app=app, session={"jwt": "myjwt"})


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
            }
        )
    )

    result = api_client.get_vaccination_data()

    assert result["cohort"] == expected_cohort
    assert "vaccinated_percentage" in result
