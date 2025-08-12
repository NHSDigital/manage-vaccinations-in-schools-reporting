import os
from dotenv import load_dotenv

load_dotenv()


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
    MAVIS_ROOT_URL = os.environ.get("MAVIS_ROOT_URL") or "http://localhost:4000/"

    # Flask config
    # Flask-internal secret
    SECRET_KEY = os.environ.get("SECRET_KEY")
    TEMPLATES_AUTO_RELOAD = True
    SESSION_TTL_SECONDS = int(os.environ.get("SESSION_TTL_SECONDS") or "600")

    # If this is set to True, you will always have a session as user_id 1,
    # nurse.joy@example.com, org: R1L, role: S8000:G8000:R8001
    # (the default user from db/seeds.rb on the main mavis app)
    FAKE_LOGIN_ENABLED = str2bool(os.environ.get("FAKE_LOGIN_ENABLED"))

    ROOT_URL = os.environ.get("ROOT_URL")


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    TESTING = False
    LOG_LEVEL = "DEBUG"
    # Uncomment this line to allow developing locally without having
    # the main Mavis running:
    # FAKE_LOGIN_ENABLED = True


class ProductionConfig(Config):
    """Production configuration"""

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
    "default": DevelopmentConfig,
}
