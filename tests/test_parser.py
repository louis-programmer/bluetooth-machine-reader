from app.parser import parse_reading


def test_valid_reading():
    result = parse_reading("37.00kg")

    assert result == {
        "weight": 37.00,
        "unit": "kg",
    }


def test_valid_decimal_reading():
    result = parse_reading("36.95kg")

    assert result == {
        "weight": 36.95,
        "unit": "kg",
    }


def test_valid_reading_with_spaces():
    result = parse_reading("  36.75kg  ")

    assert result == {
        "weight": 36.75,
        "unit": "kg",
    }


def test_invalid_text():
    result = parse_reading("hello")

    assert result is None


def test_missing_unit():
    result = parse_reading("36.75")

    assert result is None


def test_empty_reading():
    result = parse_reading("")

    assert result is None