import pytest

from generator import generate_insight
from zodiac import infer_zodiac

def test_infer_zodiac_basic():
    z = infer_zodiac("1995-08-20", "14:30")
    assert isinstance(z, str)
    assert z.lower() in [s.lower() for s in ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]]

def test_generate_insight_en():
    insp = generate_insight(
        name="Ritika",
        zodiac="Leo",
        profile={"tone": "short", "preference": "direct"},
        birth_place="Jaipur, India",
        birth_date="1995-08-20",
        birth_time="14:30",
        language="en"
    )
    assert isinstance(insp, str)
    assert len(insp) > 10
    assert "(generated" in insp

def test_generate_insight_hi():
    insp_hi = generate_insight(
        name="Ritika",
        zodiac="Leo",
        profile={"tone": "short"},
        birth_place="Jaipur, India",
        birth_date="1995-08-20",
        birth_time="14:30",
        language="hi"
    )
    assert isinstance(insp_hi, str)
    assert insp_hi.startswith("[HI]") or "[HI]" in insp_hi

def test_generate_insight_empty_profile():
    insp = generate_insight(name="Alex", zodiac="Gemini", profile=None, language="en")
    assert isinstance(insp, str)
    assert len(insp) > 0
