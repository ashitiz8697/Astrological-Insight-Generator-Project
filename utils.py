from datetime import datetime
from dateutil import parser




def parse_datetime(date_str: str, time_str: str = None) -> datetime:
if time_str:
txt = f"{date_str}T{time_str}"
else:
txt = date_str
# dateutil parser is flexible
dt = parser.isoparse(txt) if 'T' in txt else parser.parse(txt)
return dt
