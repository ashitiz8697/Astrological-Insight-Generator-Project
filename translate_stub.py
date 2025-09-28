# Dummy translation stub. Replace with IndicTrans2 / NLLB / googletrans later.


def translate_text(text: str, target_language: str = "hi") -> str:
# Very naive: tag the text and return
if target_language.lower().startswith('hi'):
return "[HI] " + text + " [Translated to Hindi - stub]"
return text
