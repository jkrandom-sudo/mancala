"""Persistent settings (~/.mancala_settings.json)."""
import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_PATH = Path.home() / ".mancala_settings.json"

DIFFICULTY = {
    "easy":   {"depth": 2, "label": "lvl_easy"},
    "normal": {"depth": 4, "label": "lvl_normal"},
    "hard":   {"depth": 7, "label": "lvl_hard"},
}
DIFFICULTY_ORDER = ["easy", "normal", "hard"]

DEFAULTS: Dict[str, Any] = {
    "lang": "zh",
    "sound": True,
    "volume": 1,
    "difficulty": "normal",
}


def load(path: Path = None) -> Dict[str, Any]:
    if path is None:
        path = DEFAULT_PATH
    s = dict(DEFAULTS)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for k in DEFAULTS:
                    if k in data:
                        s[k] = data[k]
        except (OSError, json.JSONDecodeError):
            pass
    if s["lang"] not in {"zh", "en"}:
        s["lang"] = DEFAULTS["lang"]
    if not isinstance(s["sound"], bool):
        s["sound"] = DEFAULTS["sound"]
    if not isinstance(s["volume"], int) or isinstance(s["volume"], bool):
        s["volume"] = DEFAULTS["volume"]
    else:
        s["volume"] = max(0, min(3, s["volume"]))
    if s["difficulty"] not in DIFFICULTY:
        s["difficulty"] = DEFAULTS["difficulty"]
    return s


def save(settings: Dict[str, Any], path: Path = None) -> None:
    if path is None:
        path = DEFAULT_PATH
    try:
        path.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def cycle_lang(lang: str) -> str:
    return "en" if lang == "zh" else "zh"


def cycle_volume(v: int) -> int:
    return (v + 1) % 4


def cycle_difficulty(d: str) -> str:
    if d not in DIFFICULTY_ORDER:
        return DIFFICULTY_ORDER[0]
    i = DIFFICULTY_ORDER.index(d)
    return DIFFICULTY_ORDER[(i + 1) % len(DIFFICULTY_ORDER)]
