from mavis.reporting.helpers import mavis_helper
from mavis.reporting.helpers.mavis_helper import MavisApiError, parse_json_response

PROGRAMME_YEAR_GROUPS = {
    "flu": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"],
    "hpv": ["8", "9", "10", "11"],
    "menacwy": ["9", "10", "11"],
    "td_ipv": ["9", "10", "11"],
}


class MavisApiClient:
    def __init__(self, app=None, session=None):
        self.app = app
        self.session = session

    def add_percentages(self, data: dict):
        n = data["cohort"]

        if n > 0:
            if "vaccinated" in data:
                data["vaccinated_percentage"] = data["vaccinated"] / n
                data["not_vaccinated_percentage"] = data["not_vaccinated"] / n
                data["vaccinated_by_sais_percentage"] = data["vaccinated_by_sais"] / n
                data["vaccinated_elsewhere_declared_percentage"] = (
                    data["vaccinated_elsewhere_declared"] / n
                )
                data["vaccinated_elsewhere_recorded_percentage"] = (
                    data["vaccinated_elsewhere_recorded"] / n
                )
                data["vaccinated_previously_percentage"] = (
                    data["vaccinated_previously"] / n
                )

            if "consent_given" in data:
                data["consent_given_percentage"] = data["consent_given"] / n
                data["consent_no_response_percentage"] = (
                    data["consent_no_response"] / n
                )
                data["consent_conflicts_percentage"] = data["consent_conflicts"] / n
                data["parent_refused_consent_percentage"] = (
                    data["parent_refused_consent"] / n
                )
                data["child_refused_vaccination_percentage"] = (
                    data["child_refused_vaccination"] / n
                )
                if "no_consent" in data:
                    data["no_consent_percentage"] = data["no_consent"] / n
                if "consent_requested" in data:
                    data["consent_requested_percentage"] = data["consent_requested"] / n
        else:
            if "vaccinated" in data:
                data["vaccinated_percentage"] = 0
                data["not_vaccinated_percentage"] = 0
                data["vaccinated_by_sais_percentage"] = 0
                data["vaccinated_elsewhere_declared_percentage"] = 0
                data["vaccinated_elsewhere_recorded_percentage"] = 0
                data["vaccinated_previously_percentage"] = 0

            if "consent_given" in data:
                data["consent_given_percentage"] = 0
                data["consent_no_response_percentage"] = 0
                data["consent_conflicts_percentage"] = 0
                data["parent_refused_consent_percentage"] = 0
                data["child_refused_vaccination_percentage"] = 0
                if "no_consent" in data:
                    data["no_consent_percentage"] = 0
                if "consent_requested" in data:
                    data["consent_requested_percentage"] = 0
        return data

    def get_vaccination_data(self, filters=None):
        params = {}

        if filters:
            filter_keys = [
                "programme",
                "gender",
                "year_group",
                "academic_year",
                "team_workgroup",
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

    def get_consent_data(self, filters=None):
        params = {}

        if filters:
            filter_keys = [
                "programme",
                "gender",
                "year_group",
                "academic_year",
                "team_workgroup",
                "local_authority",
                "school_local_authority",
            ]

            for key in filter_keys:
                if key in filters:
                    params[key] = filters[key]

        response = mavis_helper.api_call(
            self.app, self.session, "/api/reporting/totals", params=params
        )
        data = parse_json_response(response, "Consent data")

        if "cohort" not in data:
            raise MavisApiError(
                "Consent data response missing 'cohort' field",
                status_code=response.status_code,
                response_body=str(data),
            )

        data["no_consent"] = data["cohort"] - data["consent_given"]
        data["consent_requested"] = data["cohort"] - data["consent_no_response"]

        return self.add_percentages(data)

    def download_totals_csv(self, programme, team_workgroup, variables=None):
        params = {"programme": programme, "team_workgroup": team_workgroup}

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
            {"value": "td_ipv", "text": "Td/IPV"},
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
            {"value": "12", "text": "Year 12"},
            {"value": "13", "text": "Year 13"},
        ]

    def get_year_groups_for_programme(self, programme: str) -> list[dict]:
        all_year_groups = self.get_year_groups()
        eligible_values = PROGRAMME_YEAR_GROUPS.get(programme, [])
        return [yg for yg in all_year_groups if yg["value"] in eligible_values]

    # https://www.datadictionary.nhs.uk/attributes/person_gender_code.html
    def get_genders(self) -> list[dict]:
        return [
            {"value": "female", "text": "Female"},
            {"value": "male", "text": "Male"},
            {"value": "not known", "text": "Not known"},
            {"value": "not specified", "text": "Not specified"},
        ]
