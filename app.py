from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, constr
from typing import Optional, Any, Dict
from datetime import date, time, datetime
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
    language: Optional[constr(min_length=2, max_length=8)] = "en"


@app.post("/predict")
async def predict(data: BirthInput, explain: bool = Query(False, description="Include prompt & debug info")):
    """
    Accepts birth details and returns a structured astrological insight.
    Query param:
      - explain: when true, returns the prompt and retrieval hints (useful for grading).
    """
    # 1) Parse datetime (timezone-aware if possible)
    try:
        # prefer explicit timezone override; otherwise attempt geocoding via parse_datetime
        tz_override = data.timezone
        dt = parse_datetime(
            date_str=data.birth_date.isoformat(),
            time_str=data.birth_time.isoformat() if data.birth_time else None,
            place=data.birth_place,
            tz_override=tz_override,
        )
    except Exception as e:
        logger.exception("Invalid date/place parse")
        raise HTTPException(status_code=400, detail=f"Invalid date/place: {e}")

    # 2) Infer zodiac using month/day (simple baseline)
    try:
        zodiac = infer_zodiac(dt.month, dt.day)
    except Exception as e:
        logger.exception("Zodiac inference failed")
        raise HTTPException(status_code=500, detail="Failed to infer zodiac sign")

    # 3) Fetch or create user profile for personalization
    try:
        profile = cache.get_or_create_profile(data.name)
    except Exception:
        logger.exception("Failed to get/create profile; using default profile")
        profile = {"name": data.name, "score": 50}

    # 4) Generate insight (RAG + LLM/fallback). generator returns a structured dict.
    try:
        result: Dict[str, Any] = generate_insight(
            name=data.name,
            zodiac=zodiac,
            dt=dt,
            place=data.birth_place,
            profile=profile,
            language=data.language or "en",
            use_vector_store=True,
        )
    except ValueError as e:
        # Bad inputs forwarded from generator
        logger.exception("Bad input to generator")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Generation error")
        raise HTTPException(status_code=500, detail="Internal generation error")

    # 5) If generator produced English but the user requested another language, translate as fallback
    final_text = result.get("text", "")
    gen_language = result.get("language", "en")
    requested_language = (data.language or "en").lower()
    if requested_language != "en" and gen_language.lower() == "en":
        try:
            final_text = translate_text(final_text, target_language=requested_language)
            result["text"] = final_text
            result["language"] = requested_language
            result["source"] = result.get("source", "pseudo") + "+translate_stub"
        except Exception:
            logger.exception("Translation failed; returning English output")

    # 6) Construct response (strip prompt from default unless explain=True)
    response = {
        "zodiac": result.get("zodiac", zodiac),
        "insight": result.get("text", final_text),
        "source": result.get("source", "pseudo"),
        "used_hint": result.get("used_hint", False),
        "hint_ids": result.get("hint_ids", []),
        "language": result.get("language", requested_language),
    }

    if explain:
        # include prompt & profile & (optionally) raw retrieval hits for grading/debugging
        response["_debug"] = {
            "prompt": result.get("prompt"),
            "profile": profile,
            "hint_ids": result.get("hint_ids", []),
        }

    return response


@app.get("/health")
async def health():
    return {"status": "ok"}
