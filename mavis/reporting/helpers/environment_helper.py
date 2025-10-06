from enum import Enum


class EnvType(Enum):
    PROD = "production"
    DEV = "development"
    REVIEW = "review"
    STAGING = "staging"
    TEST = "test"
    QA = "qa"
    PREVIEW = "preview"

    def __str__(self):
        return str(self.value)


ENV_COLOUR = {
    EnvType.PROD: "blue",
    EnvType.DEV: "white",
    EnvType.REVIEW: "purple",
    EnvType.STAGING: "purple",
    EnvType.TEST: "red",
    EnvType.QA: "orange",
    EnvType.PREVIEW: "yellow",
}


class Environment:
    def __init__(self, type: EnvType):
        self.type = type

    def is_production(self):
        return self.type == EnvType.PROD

    @property
    def colour(self):
        return ENV_COLOUR[self.type]

    @property
    def title(self):
        return str(self.type).capitalize()

    @property
    def title_in_sentence(self):
        return (
            f"This is a {self.type} environment."
            + " Do not use it to make clinical decisions."
        )
