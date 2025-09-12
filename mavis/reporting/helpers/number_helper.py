def thousands(value: int | None) -> str:
    """
    Format an integer with thousands separators.

    Args:
        value: The integer value to format

    Returns:
        str: The formatted string with thousands separators
    """
    if value is None:
        return ""

    try:
        # Convert to int and format with thousands separators
        return f"{int(value):,}"
    except (ValueError, TypeError):
        # Return original value if it can't be converted to int
        return str(value)


def percentage(value: float | None) -> str:
    """
    Format a decimal proportion as a percentage.
    """
    if value is None:
        return ""
    percentage = round(value * 100, 1)
    return f"{percentage}%"
