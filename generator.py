from typing import Optional, List
from translate_stub import translate_text
from embeddings_stub import embed_texts
from vector_store import retrieve_similar
import datetime
import logging
import requests
from config import OPENAI_API_KEY, HF_API_KEY, USE_OPENAI, USE_HF

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _call_openai(prompt: str, max_tokens: int = 256, temperature: float = 0.8) -> str:
    try:
        import openai
    except Exception as e:
        raise RuntimeError("openai package not installed") from e
    openai.api_key = OPENAI_API_KEY
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # placeholder; change as needed
        messages=[{"role": "system", "content": "You are a helpful astrological assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp["choices"][0]["message"]["content"].strip()

def _call_hf_api(prompt: str, model: str = "google/flan-t5-small", max_length: int = 200) -> str:
    if not HF_API_KEY:
        raise RuntimeError("HF API key not configured")
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_length}}
    r = requests.post(api_url, headers=headers, json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    # HF returns a list with dicts; try to extract
    if isinstance(data, list) and isinstance(data[0], dict) and "generated_text" in data[0]:
        return data[0]["generated_text"].strip()
    # fallback to stringified JSON
    return str(data)

def _invoke_llm(prompt: str) -> str:
    # priority: OpenAI -> HF -> pseudo LLM
    if USE_OPENAI:
        try:
            return _call_openai(prompt)
        except Exception:
            logger.exception("OpenAI call failed, falling back")
    if USE_HF:
        try:
            return _call_hf_api(prompt)
        except Exception:
            logger.exception("HF call failed, falling back")
    return pseudo_llm_generate(prompt)
  
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


def pseudo_llm_generate(prompt: str, name_hint: str = None, birth_date_hint: str = None) -> str:
    """
    Lightweight, deterministic fallback LLM that uses:
      - name_hint and birth_date_hint (if provided) to make outputs unique per user
      - the prompt to detect zodiac and retrieved context
      - a small set of templates selected via a stable hash
    This avoids returning the exact same sentence for everyone.
    """
    import hashlib

    # detect zodiac token in the prompt (preserve previous behavior)
    zodiac = "your sign"
    zodiac_tokens = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    lower = prompt.lower()
    for token in zodiac_tokens:
        if token.lower() in lower:
            zodiac = token
            break

    # gather a short context hint from the prompt (first 140 chars)
    ctx_hint = (prompt[:140].replace("\n", " ").strip() or "general")

    # create a stable index from name+birth_date+ctx to choose a template
    key = (name_hint or "") + "|" + (birth_date_hint or "") + "|" + ctx_hint
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    idx = int(h[-8:], 16)

    TEMPLATES = [
        "{name}, today {zodiac}'s strength will help you cut through clutter. Tip: pick one priority and finish it.",
        "{name}, a short conversation can reveal a useful idea. Tip: ask a clarifying question.",
        "{name}, steady focus brings progress — small reps matter. Tip: schedule 25 minutes and start.",
        "{name}, creative momentum is possible — capture quick ideas before they float away. Tip: jot one idea down.",
        "{name}, kindness toward yourself opens better choices. Tip: take a brief pause before reacting."
    ]

    chosen = TEMPLATES[idx % len(TEMPLATES)]

    # fill in name if available otherwise fall back to generic phrasing
    name_for_template = name_hint if name_hint else "Friend"

    # attached zodiac-specific short sentence
    ZODIAC_EXTRA = {
        "Aries": "You may feel ready to lead — take the initiative carefully.",
        "Taurus": "Focus on durability and value today.",
        "Gemini": "A curious question may start an interesting chain.",
        "Cancer": "Tend to relationships — a small note will mean a lot.",
        "Leo": "Confidence helps — show warmth and listen too.",
        "Virgo": "Small improvements compound — polish one detail.",
        "Libra": "Balance choices with artful compromise.",
        "Scorpio": "Deep focus can produce meaningful results.",
        "Sagittarius": "Learning or exploring will refresh your viewpoint.",
        "Capricorn": "A steady milestone is within reach — aim for progress.",
        "Aquarius": "Share your ideas — they might find allies.",
        "Pisces": "Trust your intuition on something creative."
    }

    extra = ""
    if zodiac in ZODIAC_EXTRA:
        extra = " " + ZODIAC_EXTRA[zodiac]

    # Add a short mention of retrieved/context hint if present
    context_snippet = ""
    if "Context from astrology corpus:" in prompt:
        # crude extraction of the first context fragment if present
        try:
            after = prompt.split("Context from astrology corpus:", 1)[1]
            snippet = after.split("|", 1)[0].strip()
            if snippet:
                context_snippet = f" (Context note: {snippet[:90].strip()})"
        except Exception:
            context_snippet = ""

    now = datetime.date.today().isoformat()
    out = chosen.format(name=name_for_template, zodiac=zodiac) + extra + context_snippet
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

    # log prompts + retrieved for debugging (safe to remove later)
    logger.info("DEBUG prompt: %s", prompt)
    logger.info("DEBUG retrieved ctx: %s", retrieved)

    # invoke LLM; if falling back to pseudo_llm_generate, pass name and birth_date so fallback can personalize
    if USE_OPENAI or USE_HF:
        english_out = _invoke_llm(prompt)
    else:
        # call pseudo directly with hints to ensure personalization even when LLMs are disabled
        english_out = pseudo_llm_generate(prompt, name_hint=name, birth_date_hint=birth_date)

    if not language or language.startswith("en"):
        return english_out
    else:
        translated = translate_text(english_out, target_lang=language)
        return translated


if __name__ == "__main__":
    print(generate_insight("Ritika", "Leo", profile={"tone":"short","preference":"direct"}))
