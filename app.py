from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from zodiac import infer_zodiac
from generator import generate_insight
from translate_stub import translate_text
from cache import ProfileCache
from utils import parse_datetime
import logging
logger = logging.getLogger("astro")
logging.basicConfig(level=logging.INFO)


app = FastAPI(title="Astrological Insight Generator")
cache = ProfileCache(max_size=1000)


class BirthInput(BaseModel):
    name: str
    birth_date: date
    birth_time: Optional[time] = None
    birth_place: Optional[str] = None
    timezone: Optional[str] = None   # e.g., "Asia/Kolkata"
    language: Optional[constr(min_length=2, max_length=5)] = "en"



@app.post("/predict")
async def predict(data: BirthInput):
    try:
        dt = parse_datetime(data.birth_date.isoformat(), data.birth_time.isoformat() if data.birth_time else None, place=data.birth_place)
    except Exception as e:
        logger.exception("Invalid date/place parse")
        raise HTTPException(status_code=400, detail=f"Invalid date/place: {e}")

    try:
        insight = generate_insight(...)
    except Exception as e:
        logger.exception("Generation error")
        raise HTTPException(status_code=500, detail="Internal generation error")


zodiac = infer_zodiac(dt.month, dt.day)


# personalization vector: simple hash-based profile
profile = cache.get_or_create_profile(data.name)


insight = generate_insight(
name=data.name,
zodiac=zodiac,
dt=dt,
place=data.birth_place,
profile=profile,
)


if data.language and data.language.lower() != "en":
insight = translate_text(insight, target_language=data.language)


return {
"zodiac": zodiac,
"insight": insight,
"language": data.language or "en",
}


# health
@app.get("/health")
async def health():
return {"status": "ok"}
