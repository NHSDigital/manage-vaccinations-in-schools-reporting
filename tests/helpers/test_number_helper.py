from mavis.reporting.helpers.number_helper import percentage


def test_percentage_zero():
    assert percentage(0) == "0.0%"


def test_percentage_one():
    assert percentage(1) == "100%"


def test_percentage_half():
    assert percentage(0.5) == "50.0%"


def test_percentage_almost_zero():
    assert percentage(0.0001) == "0.0%"


def test_percentage_almost_one():
    assert percentage(0.999999) == "100%"


def test_percentage_one_decimal_place():
    assert percentage(0.123) == "12.3%"


def test_percentage_rounds_up():
    assert percentage(0.4566) == "45.7%"


def test_percentage_none():
    assert percentage(None) == ""
