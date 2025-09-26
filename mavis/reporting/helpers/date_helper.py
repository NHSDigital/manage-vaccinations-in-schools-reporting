from datetime import datetime

START_OF_SCHOOL_YEAR = 9


def get_current_academic_year(date: datetime = None):
    now = date or datetime.now()
    if now.month < START_OF_SCHOOL_YEAR:
        return now.year - 1
    return now.year


def get_current_academic_year_range(date: datetime = None):
    start_year = get_current_academic_year(date)
    end_year = start_year + 1
    return f"{start_year} to {end_year}"
