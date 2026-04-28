import json
import os
LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

# ── Default settings ──────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "music_volume": 40,         # 0-100
    "sfx_volume":   80,         # 0-100
    "car_color":    "default",  # "default" | "red" | "blue" | "green"
    "difficulty":   "normal",   # "easy" | "normal" | "hard"
    "username":     "",
}


# ── Settings ──────────────────────────────────────────────────────────────────

def load_settings() -> dict:
    """Load settings from disk; fall back to defaults for missing keys."""
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        # Merge with defaults so new keys are always present
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    """Write settings dict to disk."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


# ── Leaderboard ───────────────────────────────────────────────────────────────

def load_leaderboard() -> list:
    """Return the saved leaderboard as a list of dicts, newest-first."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_score(username: str, score: int, distance: int) -> None:
    """
    Append a new entry and keep only the top-10 by score.
    Each entry: {"name": str, "score": int, "distance": int}
    """
    board = load_leaderboard()
    board.append({"name": username, "score": score, "distance": distance})
    board.sort(key=lambda e: e["score"], reverse=True)
    board = board[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(board, f, indent=2)