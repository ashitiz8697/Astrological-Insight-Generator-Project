from typing import Optional, List
from translate_stub import translate_text
from embeddings_stub import embed_texts
from vector_store import retrieve_similar
import datetime
import logging

logger = logging.getLogger("generator")
logging.basicConfig(level=logging.INFO)


def build_prompt(name: str,
                 zodiac: str,
                 profile_text: Optional[str] = "",
                 retrieved_ctx: Optional[List[str]] = None,
                 birth_place: Optional[str] = None,
                 birth_date: Optional[str] = None,
                 birth_time: Optional[str] = None) -> str:
    parts = []
    parts.append(f"{name}, your zodiac sign is {zodiac}.")
    if birth_date:
        parts.append(f"Birth date: {birth_date}.")
    if birth_time:
        parts.append(f"Birth time: {birth_time}.")
    if birth_place:
        parts.append(f"Birth place: {birth_place}.")
    if profile_text:
        parts.append(f"Profile: {profile_text}")
    if retrieved_ctx:
        parts.append("Context from astrology corpus: " + " | ".join(retrieved_ctx[:3]))

    parts.append("Write a short (1-2 sentence) daily astrological insight and one actionable tip.")
    parts.append("Keep tone positive and concise.")

    prompt = " ".join(parts)
    logger.debug("Built prompt: %s", prompt)
    return prompt


def pseudo_llm_generate(prompt: str) -> str:
    zodiac = "your sign"
    for token in ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]:
        if token.lower() in prompt.lower():
            zodiac = token
            break

    insight = f"Today, {zodiac}'s inherent strengths will be highlighted; focus on clear priorities."
    tip = "Actionable tip: take one small step toward your most important task."

    if "short" in prompt.lower() or "concise" in prompt.lower():
        out = f"{insight} {tip}"
    else:
        out = f"{insight} {tip} Keep an open mind and be kind to yourself."

    now = datetime.date.today().isoformat()
    return f"{out} (generated {now})"


def generate_insight(name: str,
                     zodiac: str,
                     profile: Optional[dict] = None,
                     birth_place: Optional[str] = None,
                     birth_date: Optional[str] = None,
                     birth_time: Optional[str] = None,
                     language: str = "en") -> str:
    profile_text = ""
    if isinstance(profile, dict):
        keys = ["tone", "last_used", "preference"]
        parts = []
        for k in keys:
            if k in profile:
                parts.append(f"{k}:{profile[k]}")
        profile_text = "; ".join(parts)
    elif isinstance(profile, str):
        profile_text = profile

    seed_query = f"{name} {zodiac} daily advice"
    query_embedding = embed_texts([seed_query])[0]
    retrieved = retrieve_similar(query_embedding, k=3)

    prompt = build_prompt(name=name,
                          zodiac=zodiac,
                          profile_text=profile_text,
                          retrieved_ctx=retrieved,
                          birth_place=birth_place,
                          birth_date=birth_date,
                          birth_time=birth_time)

    english_out = pseudo_llm_generate(prompt)

    if not language or language.startswith("en"):
        return english_out
    else:
        translated = translate_text(english_out, target_lang=language)
        return translated


if __name__ == "__main__":
    print(generate_insight("Ritika", "Leo", profile={"tone":"short","preference":"direct"}))
