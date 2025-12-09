import os

ENVIRONMENT_COLOUR = {
    "production": "blue",
    "development": "white",
    "review": "purple",
    "test": "red",
    "qa": "orange",
    "preview": "yellow",
}

ENVIRONMENT_THEME_COLOUR = {
    "production": "#005eb8",
    "development": "#fff",
    "review": "#d6cce3",
    "test": "#f7d4d1",
    "qa": "#ffdc8e",
    "preview": "#fff59d",
}


class HostingEnvironment:
    @classmethod
    def name(cls) -> str:
        return os.environ["SENTRY_ENVIRONMENT"]

    @classmethod
    def colour(cls) -> str:
        return ENVIRONMENT_COLOUR.get(cls.name(), "white")

    @classmethod
    def theme_colour(cls) -> str:
        return ENVIRONMENT_THEME_COLOUR.get(cls.name(), "#fff")

    @classmethod
    def title(cls) -> str:
        if cls.name() == "qa":
            return "QA"
        return cls.name().capitalize()

    @classmethod
    def title_in_sentence(cls) -> str:
        if cls.name() == "qa":
            return "QA"
        return cls.name()

    @classmethod
    def is_production(cls) -> bool:
        return cls.name() == "production"
