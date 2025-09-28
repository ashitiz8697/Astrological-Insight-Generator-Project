from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from zodiac import infer_zodiac
from generator import generate_insight
from translate_stub import translate_text
from cache import ProfileCache
from utils import parse_datetime


app = FastAPI(title="Astrological Insight Generator")
cache = ProfileCache(max_size=1000)


class BirthInput(BaseModel):
name: str
birth_date: str # YYYY-MM-DD
birth_time: Optional[str] = None # HH:MM (24h)
birth_place: Optional[str] = None
language: Optional[str] = "en"


@app.post("/predict")
async def predict(data: BirthInput):
# Parse & validate
try:
dt = parse_datetime(data.birth_date, data.birth_time)
except Exception as e:
raise HTTPException(status_code=400, detail=str(e))


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
