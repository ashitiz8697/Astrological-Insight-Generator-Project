from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import logging

from zodiac import infer_zodiac
import generator
import cache

app = FastAPI(title="Astrological Insight Generator")
logger = logging.getLogger("aig")
logging.basicConfig(level=logging.INFO)


class PredictRequest(BaseModel):
    name: str
    birth_date: str  # YYYY-MM-DD
    birth_time: Optional[str] = None  # HH:MM (optional)
    birth_place: Optional[str] = None
    language: Optional[str] = "en"

    @validator("birth_date")
    def validate_birth_date(cls, v):
        import datetime
        try:
            datetime.date.fromisoformat(v)
        except Exception:
            raise ValueError("birth_date must be in YYYY-MM-DD format")
        return v

    @validator("birth_time")
    def validate_birth_time(cls, v):
        if v is None or v == "":
            return None
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("birth_time must be HH:MM")
        hh, mm = parts
        try:
            hh_i, mm_i = int(hh), int(mm)
        except Exception:
            raise ValueError("birth_time must be numeric HH:MM")
        if not (0 <= hh_i <= 23 and 0 <= mm_i <= 59):
            raise ValueError("birth_time must be a valid time")
        return v


class PredictResponse(BaseModel):
    zodiac: str
    insight: str
    language: str


@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    logger.info("Received predict request: %s", req.json())

    try:
        zodiac = infer_zodiac(req.birth_date, req.birth_time)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not infer zodiac: {e}")

    profile = cache.get_profile(req.name)

    insight = generator.generate_insight(
        name=req.name,
        zodiac=zodiac,
        birth_place=req.birth_place,
        birth_date=req.birth_date,
        birth_time=req.birth_time,
        profile=profile,
        language=req.language or "en",
    )

    cache.update_profile(req.name, {"last_used": req.birth_date})

    return PredictResponse(zodiac=zodiac, insight=insight, language=req.language or "en")


@app.get("/health")
async def health():
    return {"status": "ok"}
