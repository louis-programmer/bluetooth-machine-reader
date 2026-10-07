from app.formatter import format_reading


def test_format_reading():
    reading = {
        "weight": 31.0,
        "unit": "kg",
    }

    assert format_reading(reading) == "31.00kg"


def test_format_reading_decimal():
    reading = {
        "weight": 36.95,
        "unit": "kg",
    }

    assert format_reading(reading) == "36.95kg"


def test_format_reading_trailing_zero():
    reading = {
        "weight": 37.5,
        "unit": "kg",
    }

    assert format_reading(reading) == "37.50kg"