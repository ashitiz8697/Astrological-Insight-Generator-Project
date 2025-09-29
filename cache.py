import json
import os
from typing import Optional

_CACHE_FILE = ".user_profiles.json"

def _read_all() -> dict:
    if not os.path.exists(_CACHE_FILE):
        return {}
    try:
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _write_all(data: dict):
    with open(_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_profile(name: str) -> Optional[dict]:
    allp = _read_all()
    return allp.get(name)

def update_profile(name: str, patch: dict):
    allp = _read_all()
    p = allp.get(name, {})
    p.update(patch)
    allp[name] = p
    _write_all(allp)
