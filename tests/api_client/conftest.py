import pytest


@pytest.fixture(autouse=True)
def _app_context(app_ctx):
    pass
