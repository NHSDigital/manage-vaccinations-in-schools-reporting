from mavis.reporting.helpers.measure_faker_helper import MeasureFaker


class Organisation:
    def __init__(self, organisation: dict):
        self.name: str = organisation["name"]
        self.code: str = organisation["code"]

    def fake_measures(self, organisation_type: str) -> None:
        faker = MeasureFaker(self.name)
        self._fake_cohort_size: int = faker.eligible_cohort_size(organisation_type)
        self._measures: dict[str, int] = faker.measures(self._fake_cohort_size)

    def measure_value(self, measure: str) -> int | None:
        if measure == "eligible_cohort":
            return self._fake_cohort_size

        if measure in self._measures:
            return self._measures[measure]
        return None
