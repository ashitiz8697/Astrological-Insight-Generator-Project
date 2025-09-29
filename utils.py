"""
utils.py

Utility helpers for the Astrological Insight Generator.

Primary function:
- parse_datetime(date_str, time_str=None, place=None, tz_override=None)

Behavior:
- Accepts ISO-like date and time strings (or date/time objects), and returns a `datetime`.
- If tz_override is provided, sets tzinfo to that ZoneInfo.
- If place is provided, attempts geocoding -> timezone lookup and sets tzinfo.
- If timezone cannot be determined, returns a naive datetime (same behavior as before),
  but does so explicitly and without crashing.
"""

from typing import Optional, Union
from datetime import datetime, date, time
from dateutil import parser
from zoneinfo import ZoneInfo
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import logging
import re

logger = logging.getLogger(__name__)


def _to_str(obj: Union[str, date, time, datetime, None]) -> Optional[str]:
    """Convert date/time/datetime to ISO string, or return the string unchanged."""
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, time):
        # time.isoformat() may not include seconds; it's fine for parser
        return obj.isoformat()
    return str(obj)


def _sanitize_place(place: Optional[str]) -> Optional[str]:
    """Basic sanitization for place strings: strip extra whitespace and control chars."""
    if not place:
        return None
    # remove control characters and collapse whitespace
    cleaned = re.sub(r"[\r\n\t]+", " ", place).strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned if cleaned else None


def parse_datetime(
    date_str: Union[str, date, datetime],
    time_str: Optional[Union[str, time]] = None,
    place: Optional[str] = None,
    tz_override: Optional[str] = None,
) -> datetime:
    """
    Parse date and optional time into a datetime object, attempting to attach timezone info.

    Parameters
    ----------
    date_str : str|date|datetime
        Date component (e.g., "1995-08-20" or a date object). If it's a datetime, the time_str is ignored.
    time_str : str|time, optional
        Time component like "14:30" or a time object.
    place : str, optional
        Human-readable place (e.g., "Jaipur, India") used for geocoding -> timezone lookup.
    tz_override : str, optional
        Explicit timezone to use (e.g., "Asia/Kolkata"). If provided, this will be used instead of geocoding.

    Returns
    -------
    datetime
        A timezone-aware datetime if tz_override or place->timezone succeeded. Otherwise returns a naive datetime.

    Raises
    ------
    ValueError
        If parsing fails for the provided date/time strings.
    """
    # prepare strings
    date_part = _to_str(date_str)
    time_part = _to_str(time_str)
    place_clean = _sanitize_place(place)

    if date_part is None:
        raise ValueError("date_str is required")

    # build ISO-like combined string for parsing
    txt = f"{date_part}T{time_part}" if time_part else date_part

    try:
        dt = parser.isoparse(txt) if "T" in txt else parser.parse(txt)
    except Exception as e:
        logger.exception("Failed to parse date/time: %s", txt)
        raise ValueError(f"Could not parse date/time: {e}") from e

    # If explicit tz_override provided, attach it and return
    if tz_override:
        try:
            tz = ZoneInfo(tz_override)
            return dt.replace(tzinfo=tz)
        except Exception:
            logger.exception("Invalid tz_override provided: %s", tz_override)
            # continue to try geocoding if provided, otherwise return naive dt

    # If place provided, attempt geocoding -> timezone lookup
    if place_clean:
        try:
            geolocator = Nominatim(user_agent="astro_insight")
            location = geolocator.geocode(place_clean, timeout=10)
            if location:
                tf = TimezoneFinder()
                tz_name = tf.timezone_at(lat=location.latitude, lng=location.longitude)
                if tz_name:
                    try:
                        tz = ZoneInfo(tz_name)
                        return dt.replace(tzinfo=tz)
                    except Exception:
                        logger.exception("Failed to set ZoneInfo for tz: %s", tz_name)
                else:
                    logger.info("TimezoneFinder returned None for place: %s (lat=%s,lng=%s)",
                                place_clean, location.latitude, location.longitude)
            else:
                logger.info("Geocoding returned no results for place: %s", place_clean)
        except Exception:
            logger.exception("Error while geocoding/timezone lookup for place: %s", place_clean)

    # Fallback: return naive datetime if timezone cannot be determined
    return dt
