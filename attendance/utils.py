def attendance_rate_percent(numerator, denominator, precision=1):
    """Return an attendance percentage capped between 0 and 100."""
    try:
        numerator = float(numerator)
        denominator = float(denominator)
    except (TypeError, ValueError):
        return 0

    if denominator <= 0:
        return 0

    rate = round((max(numerator, 0) / denominator) * 100, precision)
    return min(rate, 100)
