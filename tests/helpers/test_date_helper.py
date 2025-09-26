from datetime import datetime

from mavis.reporting.helpers.date_helper import get_current_academic_year_range


def test_get_current_academic_year_range_before_september_2025():
    assert get_current_academic_year_range(datetime(2025, 8, 31)) == "2024 to 2025"


def test_get_current_academic_year_range_start_of_september_2025():
    assert get_current_academic_year_range(datetime(2025, 9, 1)) == "2025 to 2026"


def test_get_current_academic_year_range_january_2025():
    assert get_current_academic_year_range(datetime(2025, 1, 15)) == "2024 to 2025"


def test_get_current_academic_year_range_december_2025():
    assert get_current_academic_year_range(datetime(2025, 12, 31)) == "2025 to 2026"
