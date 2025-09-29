from typing import Optional

def _naive_hi_conversion(text: str) -> str:
    if len(text) > 120:
        short = text[:117].rsplit(" ", 1)[0] + "..."
    else:
        short = text
    return f"[HI] {short}"

def translate_text(text: str, target_lang: Optional[str] = "en") -> str:
    if not target_lang:
        return text
    t = target_lang.lower()
    if t.startswith("hi"):
        return _naive_hi_conversion(text)
    return text

if __name__ == "__main__":
    print(translate_text("Your innate leadership will shine today.", "hi"))
