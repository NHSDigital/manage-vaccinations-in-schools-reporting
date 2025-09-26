class MavisApiClient:
    def add_percentages(self, data: dict):
        n = data["cohort"]
        data["vaccinated_percentage"] = data["vaccinated"] / n
        data["not_vaccinated_percentage"] = data["not_vaccinated"] / n
        data["vaccinated_by_sais_percentage"] = data["vaccinated_by_sais"] / n
        data["vaccinated_elsewhere_declared_percentage"] = (
            data["vaccinated_elsewhere_declared"] / n
        )
        data["vaccinated_elsewhere_reported_percentage"] = (
            data["vaccinated_elsewhere_reported"] / n
        )
        data["vaccinated_previously_percentage"] = data["vaccinated_previously"] / n
        return data

    def get_vaccination_data(self):
        data = {
            "cohort": 546,
            "vaccinated": 456,
            "not_vaccinated": 90,
            "vaccinated_by_sais": 400,
            "vaccinated_elsewhere_declared": 32,
            "vaccinated_elsewhere_reported": 24,
            "vaccinated_previously": 0,
            "vaccinations_given": 402,
            "monthly_vaccinations_given": [
                {
                    "month": "September",
                    "year": 2025,
                    "vaccinations_given": 121,
                },
                {
                    "month": "October",
                    "year": 2025,
                    "vaccinations_given": 145,
                },
                {
                    "month": "November",
                    "year": 2025,
                    "vaccinations_given": 136,
                },
            ],
        }
        return self.add_percentages(data)

    def get_programmes(self) -> list[dict]:
        return [
            {"value": "flu", "text": "Flu"},
            {"value": "hpv", "text": "HPV", "checked": True},
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

    def get_genders(self) -> list[dict]:
        return [
            {"value": "female", "text": "Female"},
            {"value": "male", "text": "Male"},
            {"value": "other", "text": "Other"},
            {"value": "unknown", "text": "Unknown"},
        ]
