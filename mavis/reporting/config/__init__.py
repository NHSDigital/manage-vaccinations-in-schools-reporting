import os


def str2bool(v):
    return v is not None and v.lower() in ("yes", "true", "t", "1")


class Config:
    """Base configuration"""

    # used for verifying signature of Mavis-issued JWTs
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    # used to identify this app in the OAuth Authorization Code request
    CLIENT_ID = os.environ.get("CLIENT_ID")
    # Used as the base for constructing URLs to
    # exchange auth codes, and request data
    MAVIS_ROOT_URL = os.environ.get("MAVIS_ROOT_URL")

    # Flask config
    # Flask-internal secret
    SECRET_KEY = os.environ.get("SECRET_KEY")
    TEMPLATES_AUTO_RELOAD = True
    SESSION_TTL_SECONDS = int(os.environ.get("SESSION_TTL_SECONDS") or "600")

    ROOT_URL = os.environ.get("ROOT_URL")


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    TESTING = False
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False
    LOG_LEVEL = "INFO"


class StagingConfig(Config):
    """Staging configuration - for sandbox-alpha/-beta"""

    DEBUG = False
    TESTING = False
    LOG_LEVEL = "INFO"


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    DEBUG = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "default": DevelopmentConfig,
}
