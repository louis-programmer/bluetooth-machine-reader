import re


# -----------------------------------
# Reading parser
# -----------------------------------

WEIGHT_PATTERN = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s*kg\s*$",
    re.IGNORECASE
)


def parse_reading(line):
    """
    Parse a machine reading such as:

        36.75kg

    Returns a dictionary containing the
    numeric weight and unit.

    Returns None if the line is invalid.
    """

    match = WEIGHT_PATTERN.match(line)

    if not match:
        return None

    weight = float(match.group(1))

    return {
        "weight": weight,
        "unit": "kg",
    }