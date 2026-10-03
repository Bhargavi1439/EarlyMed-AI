from typing import Optional, Tuple

from src.config import FEATURE_COLUMNS, FEATURE_LABELS, FEATURE_RANGES


def parse_and_validate(form) -> Tuple[Optional[dict], dict]:
    """Return (values, errors). values is None if any field is invalid."""
    values = {}
    errors = {}
    for column in FEATURE_COLUMNS:
        raw = (form.get(column) or "").strip()
        label = FEATURE_LABELS[column]
        if raw == "":
            errors[column] = f"{label} is required."
            continue
        try:
            number = float(raw)
        except ValueError:
            errors[column] = f"{label} must be a number."
            continue
        low, high = FEATURE_RANGES[column]
        if number < low or number > high:
            errors[column] = f"{label} must be between {low} and {high}."
            continue
        values[column] = int(number) if column in {"Pregnancies", "Age"} else number
    if errors:
        return None, errors
    return values, errors
