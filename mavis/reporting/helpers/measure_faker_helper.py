import random


class MeasureFaker:
    def __init__(self, seed: str = None):
        self.rng = random.Random(seed) if seed else random

    def eligible_cohort_size(self, type: str) -> int:
        match type:
            case "region":
                return self.rng.randint(85000, 150000)
            case "provider":
                return self.rng.randint(7500, 12500)
            case "school":
                return self.rng.randint(500, 2000)
            case _:
                raise ValueError(f"Invalid type: {type}")

    def measures(self, eligible_cohort_size: int) -> dict[str, int]:
        """
        Fakes a set of measure values for a given cohort size.
        """
        performance = self.rng.randint(85, 99)

        measures = {}

        sessions = round(eligible_cohort_size / 300)
        measures["sessions_completed"] = self.rng.randint(
            round(performance * sessions / 2 / 100),
            round(performance * sessions / 100),
        )

        measures["consent_offered"] = round(eligible_cohort_size * 0.99)
        consent_given = round(eligible_cohort_size * performance / 100)
        consent_refused = round((eligible_cohort_size - consent_given) / 3)
        measures["consent_given"] = consent_given
        measures["consent_refused"] = consent_refused
        measures["no_response"] = (
            eligible_cohort_size - consent_given - measures["consent_refused"]
        )

        measures["vaccinated"] = round(consent_given * performance / 100)
        measures["outstanding"] = round(
            measures["consent_given"] - measures["vaccinated"]
        )
        measures["vaccinations"] = round(measures["vaccinated"] * 1.1)
        measures["uptake"] = round(measures["vaccinated"] / eligible_cohort_size * 100)

        return measures
