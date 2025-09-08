# Import sys module for modifying Python's runtime environment
# Import os module for interacting with the operating system
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from mavis.reporting import create_app
from tests.helpers import create_random_token


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "MAVIS_ROOT_URL": "http://mavis-root.localhost/",
            "TESTING": True,
            "CLIENT_ID": create_random_token(),
            "CLIENT_SECRET": create_random_token(),
        }
    )
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
