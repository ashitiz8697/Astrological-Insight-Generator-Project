"""
translate_stub.py

A minimal translation stub used for demo/multilingual flow.

Behavior:
- If the target language starts with 'hi' (Hindi), it returns a clearly marked placeholder
  translation (so it's obvious in demos/tests).
- For other languages, it returns the original text unchanged.
- This is intentionally simple — replace with IndicTrans2, NLLB, googletrans, or an LLM-based
  translation when you integrate real models/APIs.

Functions
---------
translate_text(text: str, target_language: str = "hi") -> str
    Return a translated (or placeholder) version of `text`.
"""

from typing import Optional
import logging
import re

logger = logging.getLogger(__name__)


def _sanitize(text: str) -> str:
    """Basic sanitization: strip excessive whitespace and control chars."""
    if text is None:
        return ""
    txt = re.sub(r"[\r\n\t]+", " ", text).strip()
    txt = re.sub(r"\s{2,}", " ", txt)
    return txt


def translate_text(text: str, target_language: Optional[str] = "hi") -> str:
    """
    Dummy translation stub.

    Parameters
    ----------
    text : str
        The text to translate.
    target_language : str, optional
        Target language code (e.g., "hi" for Hindi, "en" for English).

    Returns
    -------
    str
        Translated text (placeholder for Hindi) or the original text for other languages.
    """
    txt = _sanitize(text)
    if not txt:
        return ""

    lang = (target_language or "en").lower().strip()

    # Simple Hindi placeholder translation
    if lang.startswith("hi"):
        # Return a clearly labelled placeholder so reviewers know translation was applied.
        return "[HI] " + txt + " [Translated to Hindi - stub]"

    # For other languages, we currently return the original text.
    # Integration note:
    # - To use an LLM to generate the output directly in the target language,
    #   prefer instructing the LLM (add language to the prompt) rather than translating
    #   the English output afterwards; this preserves nuance.
    #
    # - To plug a real translator (e.g., IndicTrans2 / NLLB / googletrans), replace this body
    #   with the appropriate API/model call.
    logger.debug("translate_text: returning original text for target_language=%s", lang)
    return txt

