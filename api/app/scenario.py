import csv
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "scenarios"

SPECIAL_KEYS = {"none", "final"}


@lru_cache(maxsize=1)
def load_hint_messages() -> dict[str, str]:
    """Load hint messages from CSV. Returns dict[item_key, message]."""
    messages: dict[str, str] = {}
    with open(DATA_DIR / "hint_message.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                messages[row[0].strip()] = row[1].strip()
    return messages


def get_game_items() -> set[str]:
    """Return the set of detectable item keys (excluding none/final)."""
    return set(load_hint_messages().keys()) - SPECIAL_KEYS
