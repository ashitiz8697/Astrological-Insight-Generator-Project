# utils.py (add dependencies: geopy, timezonefinder)
from dateutil import parser
from zoneinfo import ZoneInfo
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

def parse_datetime(date_str: str, time_str: str = None, place: str = None):
    txt = f"{date_str}T{time_str}" if time_str else date_str
    dt = parser.parse(txt)              # naive
    if place:
        geo = Nominatim(user_agent="astro_insight")
        loc = geo.geocode(place, timeout=10)
        if loc:
            tz = TimezoneFinder().timezone_at(lat=loc.latitude, lng=loc.longitude)
            if tz:
                return dt.replace(tzinfo=ZoneInfo(tz))
    return dt

