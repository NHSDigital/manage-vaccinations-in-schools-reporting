# Import sys module for modifying Python's runtime environment
import sys

# Import os module for interacting with the operating system
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from mavis.reporting import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "MAVIS_ROOT_URL": "http://mavis-root.localhost/",
            "TESTING": True,
        }
    )

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
