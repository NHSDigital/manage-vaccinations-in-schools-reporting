import os

from mavis.reporting.helpers.environment_helper import EnvType


def str2bool(v):
    return v is not None and v.lower() in ("yes", "true", "t", "1")


class Config:
    """Base configuration"""

    # used for verifying signature of Mavis-issued JWTs
    CLIENT_SECRET = os.environ["CLIENT_SECRET"]
    # used to identify this app in the OAuth Authorization Code request
    CLIENT_ID = os.environ["CLIENT_ID"]
    # Used as the base for constructing URLs to
    # exchange auth codes, and request data
    MAVIS_ROOT_URL = os.environ["MAVIS_ROOT_URL"]

    # Flask config
    # Flask-internal secret
    SECRET_KEY = os.environ["SECRET_KEY"]
    TEMPLATES_AUTO_RELOAD = True
    SESSION_TTL_SECONDS = int(os.environ["SESSION_TTL_SECONDS"])

    ROOT_URL = os.environ["ROOT_URL"]


class DevelopmentConfig(Config):
    """Development configuration"""

    ENVIRONMENT = EnvType.DEV
    DEBUG = True
    TESTING = False
    LOG_LEVEL = "DEBUG"
    MAVIS_BACKEND_URL = os.environ["MAVIS_BACKEND_URL"]


class ProductionConfig(Config):
    """Production configuration"""

    ENVIRONMENT = EnvType.PROD
    DEBUG = False
    TESTING = False
    LOG_LEVEL = "INFO"


class StagingConfig(Config):
    """Staging configuration - for sandbox-alpha/-beta"""

    ENVIRONMENT = EnvType.STAGING
    DEBUG = False
    TESTING = False
    LOG_LEVEL = "INFO"


class TestingConfig(Config):
    """Testing configuration"""

    ENVIRONMENT = EnvType.TEST
    TESTING = True
    DEBUG = True


config = {
    EnvType.DEV.value: DevelopmentConfig,
    EnvType.PROD.value: ProductionConfig,
    EnvType.STAGING.value: StagingConfig,
    EnvType.TEST.value: TestingConfig,
    "default": ProductionConfig,
}
