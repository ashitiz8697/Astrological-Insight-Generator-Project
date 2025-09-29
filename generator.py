"""
generator.py

Responsible for:
- building prompts
- optional retrieval-augmented hints (RAG) using vector_store + embeddings_stub
- calling a real LLM (guarded by env) or a deterministic pseudo-LLM fallback
- post-processing & personalization
- returning a structured result (text + metadata)
"""

import os
import logging
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

from embeddings_stub import embed_text
from vector_store import VectorStore

# try to import an OpenAI stub if present; if not, we'll fall back gracefully
try:
    from openai_stub import call_openai  # optional; implement if you want real LLM calls
except Exception:
    call_openai = None  # type: ignore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- small mock corpus used to personalize output (kept as in-memory demo) ---
CORPUS = [
    ("leadership", "Advice on leading teams gracefully."),
    ("work", "Handling unexpected work pressure."),
    ("relationships", "Nurture close relationships today."),
    ("health", "Small health checks make a big difference."),
]

# initialize an in-memory vector store (this is safe to keep at module load)
vector_store = VectorStore()
for doc_id, (k, txt) in enumerate(CORPUS):
    vector_store.add(doc_id, txt)


# --- helpers -----------------------------------------------------------------
def _name_personalization(name: str) -> int:
    """Deterministic small score (0-99) based on name hashing."""
    h = hashlib.sha256(name.encode()).hexdigest()
    return int(h[:8], 16) % 100


def _choose_tone_from_score(score: int) -> str:
    """Map a numeric score to a short tone description for prompt instruction."""
    if score >= 75:
        return "bold and encouraging"
    if score <= 25:
        return "calm and cautious"
    return "balanced and empathetic"


# --- prompt builder ----------------------------------------------------------
def build_prompt(
    name: str,
    zodiac: str,
    dt: datetime,
    place: Optional[str],
    profile: Dict[str, Any],
    hint: Optional[str] = None,
    language: str = "en",
) -> str:
    """
    Build a structured prompt composed of a system persona, concise context, and an instruction.
    The prompt is purposely short (1-2 sentences requested) for easy substitution with real LLMs.
    """
    score = profile.get("score", _name_personalization(name))
    tone = _choose_tone_from_score(score)
    system = f"You are a compassionate astrological assistant. Tone: {tone}."
    now_str = dt.strftime("%b %d")
    context_lines = [
        f"Name: {name}",
        f"Birth Place: {place or 'unknown'}",
        f"Zodiac: {zodiac}",
        f"Date: {now_str}",
        f"ProfileScore: {score}",
    ]
    if hint:
        context_lines.append(f"ContextHint: {hint}")

    context = "\n".join(context_lines)
    instruction = (
        "Generate a concise, actionable daily insight (1-2 sentences)."
        + (f" Produce the response in {language}." if language and language.lower() != "en" else "")
    )

    prompt = f"{system}\n\n{context}\n\n{instruction}"
    logger.debug("Built prompt: %s", prompt.replace("\n", " | "))
    return prompt


# --- pseudo-LLM (deterministic, testable) -----------------------------------
def _pseudo_llm_generate(prompt: str) -> str:
    """
    Deterministic fallback generator used when real LLM is not configured.
    This inspects the prompt for simple keywords and returns a short sentence.
    """
    p = prompt.lower()
    if "work" in p or "pressure" in p:
        return "Your grounded nature will help you handle unexpected work pressure."
    if "leadership" in p or "leo" in p:
        return "Your leadership and warmth will shine today; embrace spontaneity."
    if "relationship" in p or "nurture" in p:
        return "Small gestures will deepen an important bond."
    if "health" in p:
        return "Small health checks will pay off — listen to your body's signals."
    # default
    return "Stay present and take small, steady actions."


def _call_llm_or_fallback(prompt: str) -> Dict[str, Any]:
    """
    Attempt to call a real LLM (if OPENAI_API_KEY set and openai_stub available).
    Otherwise, return the deterministic pseudo-LLM output.

    Returns a dict with keys:
      - text: str
      - source: "openai" | "pseudo"
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and call_openai is not None:
        try:
            resp_text = call_openai(prompt)
            logger.info("LLM call succeeded; source=openai")
            return {"text": resp_text, "source": "openai"}
        except Exception:
            logger.exception("OpenAI call failed; falling back to pseudo-LLM.")
            # fall through to pseudo
    # pseudo fallback
    logger.info("Using pseudo-LLM fallback (deterministic).")
    return {"text": _pseudo_llm_generate(prompt), "source": "pseudo"}


# --- main generate_insight ---------------------------------------------------
def generate_insight(
    name: str,
    zodiac: str,
    dt: datetime,
    place: Optional[str],
    profile: Optional[Dict[str, Any]] = None,
    language: str = "en",
    use_vector_store: bool = True,
    rag_k: int = 3,
    rag_threshold: float = 0.35,
) -> Dict[str, Any]:
    """
    Orchestrates prompt building, optional RAG retrieval, LLM call/fallback, and postprocessing.

    Returns a structured dictionary:
      {
        "text": "<final insight text>",
        "zodiac": "<zodiac>",
        "source": "pseudo"|"openai",
        "used_hint": True|False,
        "hint_ids": [int,...] | [],
        "language": "<language>",
        "prompt": "<the prompt sent to LLM>"  # optional, helpful for debugging
      }
    """
    if not name or not zodiac or not dt:
        raise ValueError("name, zodiac, and dt are required inputs for generate_insight")

    profile = profile or {"score": _name_personalization(name)}
    # --- retrieval (RAG) ----------------------------------------------------
    hint = ""
    used_hint = False
    hint_ids = []

    if use_vector_store and vector_store is not None:
        try:
            q_text = f"{name} {zodiac}"
            q_emb = embed_text(q_text)
            hits = vector_store.similarity_search(q_emb, k=rag_k)
            # hits expected to be a list of dicts with 'score', 'text', 'id'
            strong_hits = [h for h in hits if h.get("score", 0.0) >= rag_threshold]
            if strong_hits:
                # combine top two strong hits into a short hint context
                top_hits = strong_hits[:2]
                hint = " ".join(h.get("text", "") for h in top_hits)
                used_hint = True
                hint_ids = [h.get("id") for h in top_hits if h.get("id") is not None]
            logger.debug("RAG hits: %s", hits)
        except Exception:
            logger.exception("Vector store retrieval failed; continuing without hint.")
            hint = ""
            used_hint = False
            hint_ids = []

    # --- build prompt & call LLM/fallback ----------------------------------
    prompt = build_prompt(name=name, zodiac=zodiac, dt=dt, place=place, profile=profile, hint=hint, language=language)
    llm_resp = _call_llm_or_fallback(prompt)
    out_text = llm_resp.get("text", "").strip()
    source = llm_resp.get("source", "pseudo")

    # --- personalization tweaks -------------------------------------------
    # Use profile score to slightly modify tone or append a short clause.
    score = int(profile.get("score", _name_personalization(name)))
    if score >= 85:
        out_text += " You may find bold action especially rewarding today."
    elif score <= 15:
        out_text += " Consider prioritizing rest and avoiding big decisions today."

    # final composed text: keep it short and prefixed by the name & zodiac context
    final_text = f"{name}, your {zodiac} qualities will be highlighted today. {out_text}"

    result = {
        "text": final_text,
        "zodiac": zodiac,
        "source": source,
        "used_hint": used_hint,
        "hint_ids": hint_ids,
        "language": language,
        "prompt": prompt,  # useful for debugging / review; can be removed in prod
    }

    logger.info("Generated insight for %s (zodiac=%s, source=%s, used_hint=%s)", name, zodiac, source, used_hint)
    return result


# If you want a quick demo when running generator.py directly:
if __name__ == "__main__":
    # quick local demo
    demo_profile = {"score": 72}
    demo_dt = datetime.strptime("1995-08-20", "%Y-%m-%d")
    out = generate_insight("Ritika", "Leo", demo_dt, "Jaipur, India", demo_profile, language="en")
    print(out["text"])
