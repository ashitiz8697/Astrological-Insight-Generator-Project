import datetime
from typing import Optional

# Basic sun-sign date ranges (no precession, tropical zodiac)
# Each entry: (month, day) inclusive start
_ZODIAC_RANGES = [
    ("Capricorn", (12,22), (1,19)),
    ("Aquarius", (1,20), (2,18)),
    ("Pisces", (2,19), (3,20)),
    ("Aries", (3,21), (4,19)),
    ("Taurus", (4,20), (5,20)),
    ("Gemini", (5,21), (6,20)),
    ("Cancer", (6,21), (7,22)),
    ("Leo", (7,23), (8,22)),
    ("Virgo", (8,23), (9,22)),
    ("Libra", (9,23), (10,22)),
    ("Scorpio", (10,23), (11,21)),
    ("Sagittarius", (11,22), (12,21)),
]

def _in_range(month:int, day:int, start:tuple, end:tuple) -> bool:
    # start and end are (m,d)
    start_m, start_d = start
    end_m, end_d = end
    if start_m <= end_m:
        # same-year range (e.g., Mar 21 - Apr 19)
        start_date = (start_m, start_d)
        end_date = (end_m, end_d)
        return (month, day) >= start_date and (month, day) <= end_date
    else:
        # wraps year (e.g., Dec 22 - Jan 19)
        return (month, day) >= start or (month, day) <= end

def infer_zodiac(birth_date: str, birth_time: Optional[str] = None) -> str:
    """
    Infer the sun-sign (zodiac) from birth_date (YYYY-MM-DD). birth_time is optional;
    cusp handling is simplified (we do NOT compute astronomical positions).
    Returns: one of the 12 zodiac names.
    Assumptions: tropical zodiac date ranges (fixed calendar ranges).
    """
    dt = datetime.date.fromisoformat(birth_date)
    month = dt.month
    day = dt.day

    for name, start, end in _ZODIAC_RANGES:
        if _in_range(month, day, start, end):
            return name
    # fallback
    return "Capricorn"
