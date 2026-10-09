import app.parser as parser


def test_valid_reading():
    result = parser.parse_reading("37.00kg")

    assert result == {
        "weight": 37.00,
        "unit": "kg",
    }


def test_valid_decimal_reading():
    result = parser.parse_reading("36.95kg")

    assert result == {
        "weight": 36.95,
        "unit": "kg",
    }


def test_valid_reading_with_spaces():
    result = parser.parse_reading("  36.75kg  ")

    assert result == {
        "weight": 36.75,
        "unit": "kg",
    }


def test_invalid_text():
    result = parser.parse_reading("hello")

    assert result is None


def test_missing_unit():
    result = parser.parse_reading("36.75")

    assert result is None


def test_empty_reading():
    result = parser.parse_reading("")

    assert result is None


def test_valid_reading_with_uppercase_unit():
    result = parser.parse_reading("36.75KG")

    assert result == {
        "weight": 36.75,
        "unit": "kg",
    }


def test_invalid_reading_with_unknown_unit():
    result = parser.parse_reading("36.75lb")

    assert result is None


def test_invalid_reading_with_extra_text():
    result = parser.parse_reading("Weight: 36.75kg")

    assert result is None



def test_parser_uses_configured_unit(monkeypatch):
    monkeypatch.setattr(parser, "WEIGHT_UNIT", "lb")

    result = parser.parse_reading("36.75lb")

    assert result == {
        "weight": 36.75,
        "unit": "lb",
    }


def test_rejects_negative_reading():
    result = parser.parse_reading("-5.00kg")

    assert result is None


def test_rejects_reading_with_multiple_decimal_points():
    result = parser.parse_reading("37.0.0kg")

    assert result is None


def test_rejects_reading_with_missing_numeric_value():
    result = parser.parse_reading("kg")

    assert result is None


def test_rejects_reading_with_trailing_characters():
    result = parser.parse_reading("37.00kgabc")

    assert result is None