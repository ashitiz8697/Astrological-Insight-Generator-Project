# config.py
import os
from typing import Optional

def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.environ.get(name, default)
    if v is not None and isinstance(v, str) and v.strip() == "":
        return default
    return v

# API Keys (keep these out of source control; set via env or CI secrets)
OPENAI_API_KEY = _env("OPENAI_API_KEY")
HF_API_KEY = _env("HF_API_KEY")
PANCHANG_API_KEY = _env("PANCHANG_API_KEY")

# Feature flags (booleans based on env presence)
USE_OPENAI = bool(OPENAI_API_KEY)
USE_HF = bool(HF_API_KEY)
USE_PANCHANG = bool(PANCHANG_API_KEY)

# Runtime / server defaults
APP_HOST = _env("APP_HOST", "0.0.0.0")
APP_PORT = int(_env("APP_PORT", "8000"))
