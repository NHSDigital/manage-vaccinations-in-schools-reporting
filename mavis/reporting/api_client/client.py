from mavis.reporting.helpers import mavis_helper
from mavis.reporting.helpers.mavis_helper import MavisApiError, parse_json_response


class MavisApiClient:
    def __init__(self, app=None, session=None):
        self.app = app
        self.session = session

    def add_percentages(self, data: dict):
        n = data["cohort"]

        if n > 0:
            data["vaccinated_percentage"] = data["vaccinated"] / n
            data["not_vaccinated_percentage"] = data["not_vaccinated"] / n
            data["vaccinated_by_sais_percentage"] = data["vaccinated_by_sais"] / n
            data["vaccinated_elsewhere_declared_percentage"] = (
                data["vaccinated_elsewhere_declared"] / n
            )
            data["vaccinated_elsewhere_recorded_percentage"] = (
                data["vaccinated_elsewhere_recorded"] / n
            )
            data["vaccinated_previously_percentage"] = data["vaccinated_previously"] / n
        else:
            data["vaccinated_percentage"] = 0
            data["not_vaccinated_percentage"] = 0
            data["vaccinated_by_sais_percentage"] = 0
            data["vaccinated_elsewhere_declared_percentage"] = 0
            data["vaccinated_elsewhere_recorded_percentage"] = 0
            data["vaccinated_previously_percentage"] = 0
        return data

    def get_vaccination_data(self, filters=None):
        params = {}

        if filters:
            filter_keys = [
                "programme",
                "gender",
                "year_group",
                "academic_year",
                "team_id",
                "local_authority",
                "school_local_authority",
            ]

            for key in filter_keys:
                if key in filters:
                    params[key] = filters[key]

        response = mavis_helper.api_call(
            self.app, self.session, "/api/reporting/totals", params=params
        )
        data = parse_json_response(response, "Vaccination data")

        if "cohort" not in data:
            raise MavisApiError(
                "Vaccination data response missing 'cohort' field",
                status_code=response.status_code,
                response_body=str(data),
            )

        return self.add_percentages(data)

    def download_totals_csv(self, programme, variables=None):
        params = {"programme": programme}

        if variables:
            params["group"] = ",".join(variables)

        return mavis_helper.api_call(
            self.app, self.session, "/api/reporting/totals.csv", params=params
        )

    def get_variables(self) -> list[dict]:
        return [
            {"value": "local_authority", "text": "Local Authority"},
            {"value": "school", "text": "School"},
            {"value": "year_group", "text": "Year group"},
            {"value": "gender", "text": "Gender"},
        ]

    def get_programmes(self) -> list[dict]:
        return [
            {"value": "flu", "text": "Flu"},
            {"value": "hpv", "text": "HPV"},
            {"value": "menacwy", "text": "MenACWY"},
            {"value": "td-ipv", "text": "Td/IPV"},
        ]

    def get_year_groups(self) -> list[dict]:
        return [
            {"value": "0", "text": "Reception"},
            {"value": "1", "text": "Year 1"},
            {"value": "2", "text": "Year 2"},
            {"value": "3", "text": "Year 3"},
            {"value": "4", "text": "Year 4"},
            {"value": "5", "text": "Year 5"},
            {"value": "6", "text": "Year 6"},
            {"value": "7", "text": "Year 7"},
            {"value": "8", "text": "Year 8"},
            {"value": "9", "text": "Year 9"},
            {"value": "10", "text": "Year 10"},
            {"value": "11", "text": "Year 11"},
        ]

    # https://www.datadictionary.nhs.uk/attributes/person_gender_code.html
    def get_genders(self) -> list[dict]:
        return [
            {"value": "2", "text": "Female"},
            {"value": "1", "text": "Male"},
            {"value": "9", "text": "Other"},
            {"value": "0", "text": "Unknown"},
        ]
