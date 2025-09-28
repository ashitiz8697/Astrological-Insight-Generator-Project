# Simplified zodiac inference based on month/day (no time/ascendant logic)


ZODIAC_RANGES = [
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




def _in_range(month, day, start, end):
sm, sd = start
em, ed = end
if sm < em or (sm == em and sd <= ed):
# same-year range
return (month > sm or (month == sm and day >= sd)) and (month < em or (month == em and day <= ed))
else:
# wraps year (eg Capricorn)
return (month > sm or (month == sm and day >= sd)) or (month < em or (month == em and day <= ed))




def infer_zodiac(month: int, day: int) -> str:
for name, start, end in ZODIAC_RANGES:
if _in_range(month, day, start, end):
return name
return "Unknown"
