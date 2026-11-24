"""Save and load the high score (R10). Current chips are never saved."""

import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "highscore.json"


def load_high_score(path=DEFAULT_PATH):
    """Return the saved high score, or 0 if the file is missing or unreadable."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        score = data["high_score"]
    except (OSError, ValueError, KeyError, TypeError):
        return 0
    if isinstance(score, int) and not isinstance(score, bool) and score >= 0:
        return score
    return 0


def save_high_score(score, path=DEFAULT_PATH):
    Path(path).write_text(json.dumps({"high_score": score}) + "\n", encoding="utf-8")
