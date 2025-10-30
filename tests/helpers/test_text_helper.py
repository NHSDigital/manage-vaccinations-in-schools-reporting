from mavis.reporting.helpers.text_helper import humanize


def test_humanize_converts_snake_case_to_human_readable():
    assert humanize("personal_choice") == "Personal choice"


def test_humanize_converts_lowercase_to_capitalized():
    assert humanize("website") == "Website"
