import re
from datetime import datetime, timedelta

def parse_unlock_time(user_input: str) -> datetime:
    """
    Accepts:
    - Absolute date/time in ISO format: 2025-08-09 14:00
    - Relative format: 1h, 3d, 2w, 10m
    """
    match = re.match(r"(\d+)([smhdw])", user_input.lower())
    if match:
        value, unit = match.groups()
        value = int(value)
        if unit == "s": return datetime.now() + timedelta(seconds=value)
        if unit == "m": return datetime.now() + timedelta(minutes=value)
        if unit == "h": return datetime.now() + timedelta(hours=value)
        if unit == "d": return datetime.now() + timedelta(days=value)
        if unit == "w": return datetime.now() + timedelta(weeks=value)

    # Assume absolute datetime
    try:
        return datetime.fromisoformat(user_input)
    except ValueError:
        raise ValueError("Invalid unlock time format.")
