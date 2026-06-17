"""Persistent leaderboard (~/.mancala_scores.json)."""
import json
from pathlib import Path
from typing import Dict, List

DEFAULT_PATH = Path.home() / ".mancala_scores.json"
MAX_ENTRIES = 10


def load(path: Path = None) -> List[Dict]:
    if path is None:
        path = DEFAULT_PATH
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [d for d in data if isinstance(d, dict) and "score" in d]
    except (OSError, json.JSONDecodeError):
        pass
    return []


def save(scores: List[Dict], path: Path = None) -> None:
    if path is None:
        path = DEFAULT_PATH
    try:
        path.write_text(json.dumps(scores, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def add_score(scores: List[Dict], entry: Dict) -> List[Dict]:
    out = list(scores) + [entry]
    out.sort(key=lambda e: e.get("score", 0), reverse=True)
    return out[:MAX_ENTRIES]


def compute_score(result: str, diff: int, depth: int) -> int:
    """Score = base by result + capture diff bonus + AI depth bonus.

    win: 100, tie: 30, loss: 0
    + diff seeds (your store - their store, signed)
    + depth * 10 (AI difficulty)
    Clamped to >= 0.
    """
    base = {"win": 100, "tie": 30, "loss": 0}.get(result, 0)
    return max(0, base + diff + depth * 10)
