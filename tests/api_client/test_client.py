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


@pytest.fixture
def consent_data():
    def _build(cohort=100, **overrides):
        defaults = {
            "cohort": cohort,
            "consent_given": 60,
            "consent_no_response": 20,
            "consent_conflicts": 5,
            "parent_refused_consent": 10,
            "child_refused_vaccination": 8,
            "refusal_reasons": {},
            "consent_routes": {},
        }
        defaults.update(overrides)
        return defaults

    return _build


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


def test_missing_cohort_field_in_consent_data_raises_error(
    api_client, mock_mavis_get_request
):
    mock_mavis_get_request(MockResponse(json_obj={"some_field": "value"}))

    with pytest.raises(MavisApiError, match="missing 'cohort' field"):
        api_client.get_consent_data()


def test_get_consent_data_with_no_filters(
    api_client, mock_mavis_get_request, consent_data
):
    data = consent_data(
        refusal_reasons={"personal_choice": 7, "already_vaccinated": 3},
        consent_routes={"website": 40, "phone": 20},
    )
    mock_mavis_get_request(MockResponse(json_obj=data))

    result = api_client.get_consent_data()

    assert result["cohort"] == 100
    assert result["consent_given"] == 60
    assert result["consent_no_response"] == 20
    assert result["consent_conflicts"] == 5
    assert result["parent_refused_consent"] == 10
    assert result["child_refused_vaccination"] == 8


def test_get_consent_data_with_filters(
    api_client, mock_mavis_get_request, consent_data
):
    data = consent_data(
        cohort=50,
        consent_given=30,
        consent_no_response=10,
        consent_conflicts=2,
        parent_refused_consent=5,
        child_refused_vaccination=3,
        refusal_reasons={"personal_choice": 4, "medical_reasons": 1},
        consent_routes={"website": 20, "phone": 10},
    )
    mock_mavis_get_request(MockResponse(json_obj=data))

    filters = {"programme": "hpv", "gender": "2", "year_group": "8"}
    result = api_client.get_consent_data(filters)

    assert result["cohort"] == 50
    assert result["consent_given"] == 30


def test_get_consent_data_calculates_percentages(
    api_client, mock_mavis_get_request, consent_data
):
    mock_mavis_get_request(MockResponse(json_obj=consent_data()))

    result = api_client.get_consent_data()

    assert result["consent_given_percentage"] == 0.6
    assert result["consent_no_response_percentage"] == 0.2
    assert result["consent_conflicts_percentage"] == 0.05
    assert result["parent_refused_consent_percentage"] == 0.1
    assert result["child_refused_vaccination_percentage"] == 0.08


def test_get_consent_data_calculates_derived_metrics(
    api_client, mock_mavis_get_request, consent_data
):
    mock_mavis_get_request(MockResponse(json_obj=consent_data()))

    result = api_client.get_consent_data()

    assert result["no_consent"] == 40
    assert result["consent_requested"] == 80
    assert result["no_consent_percentage"] == 0.4
    assert result["consent_requested_percentage"] == 0.8


def test_get_consent_data_passes_through_refusal_reasons(
    api_client, mock_mavis_get_request, consent_data
):
    data = consent_data(
        refusal_reasons={
            "personal_choice": 7,
            "already_vaccinated": 2,
            "medical_reasons": 1,
        },
        consent_routes={"website": 40, "phone": 20},
    )
    mock_mavis_get_request(MockResponse(json_obj=data))

    result = api_client.get_consent_data()

    assert "refusal_reasons" in result
    assert result["refusal_reasons"]["personal_choice"] == 7
    assert result["refusal_reasons"]["already_vaccinated"] == 2
    assert result["refusal_reasons"]["medical_reasons"] == 1


def test_get_consent_data_passes_through_consent_routes(
    api_client, mock_mavis_get_request, consent_data
):
    data = consent_data(consent_routes={"website": 40, "phone": 15, "paper": 5})
    mock_mavis_get_request(MockResponse(json_obj=data))

    result = api_client.get_consent_data()

    assert "consent_routes" in result
    assert result["consent_routes"]["website"] == 40
    assert result["consent_routes"]["phone"] == 15
    assert result["consent_routes"]["paper"] == 5


def test_get_consent_data_with_zero_cohort(
    api_client, mock_mavis_get_request, consent_data
):
    data = consent_data(
        cohort=0,
        consent_given=0,
        consent_no_response=0,
        consent_conflicts=0,
        parent_refused_consent=0,
        child_refused_vaccination=0,
    )
    mock_mavis_get_request(MockResponse(json_obj=data))

    result = api_client.get_consent_data()

    assert result["cohort"] == 0
    assert result["no_consent"] == 0
    assert result["consent_requested"] == 0
    assert result["consent_given_percentage"] == 0
    assert result["consent_no_response_percentage"] == 0
    assert result["no_consent_percentage"] == 0
    assert result["consent_requested_percentage"] == 0
