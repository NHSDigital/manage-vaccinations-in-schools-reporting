class MavisApiClient:
    def add_percentages(self, data: dict):
        n = data["cohort"]
        data["vaccinated_percentage"] = data["vaccinated"] / n
        data["not_vaccinated_percentage"] = data["not_vaccinated"] / n
        data["vaccinated_by_sais_percentage"] = data["vaccinated_by_sais"] / n
        data["vaccinated_elsewhere_percentage"] = data["vaccinated_elsewhere"] / n
        data["vaccinated_previously_percentage"] = data["vaccinated_previously"] / n
        return data

    def get_vaccination_data(self):
        data = {
            "cohort": 546,
            "vaccinated": 456,
            "not_vaccinated": 90,
            "vaccinated_by_sais": 400,
            "vaccinated_elsewhere": 56,
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
