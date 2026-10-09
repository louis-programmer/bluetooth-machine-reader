import re

from app.config import WEIGHT_UNIT


# -----------------------------------
# Reading parser
# -----------------------------------

def parse_reading(line):
    """
    Parse a machine reading using the configured weight unit.

    Example:
        36.75kg

    Returns a dictionary containing the numeric weight
    and configured unit.

    Returns None if the line is invalid.
    """

    pattern = re.compile(
        rf"^\s*(\d+(?:\.\d+)?)\s*{re.escape(WEIGHT_UNIT)}\s*$",
        re.IGNORECASE
    )

    match = pattern.match(line)

    if not match:
        return None

    weight = float(match.group(1))

    return {
        "weight": weight,
        "unit": WEIGHT_UNIT,
    }