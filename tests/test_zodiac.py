import pytest
from zodiac import infer_zodiac

def test_infer_zodiac_known_dates():
    # Basic known-date check: Aug 20 should fall in Leo range
    assert infer_zodiac("1995-08-20") == "Leo"

def test_infer_zodiac_all_signs_present():
    # Ensure function returns one of the 12 zodiac names for many sample dates
    samples = {
        "1995-03-25": "Aries",
        "1995-04-25": "Taurus",
        "1995-06-01": "Gemini",
        "1995-07-10": "Cancer",
        "1995-08-10": "Leo",
        "1995-09-10": "Virgo",
        "1995-10-10": "Libra",
        "1995-11-01": "Scorpio",
        "1995-12-01": "Sagittarius",
        "1995-01-05": "Capricorn",
        "1995-02-05": "Aquarius",
        "1995-03-05": "Pisces",
    }
    for date_iso, expected in samples.items():
        assert infer_zodiac(date_iso) == expected
