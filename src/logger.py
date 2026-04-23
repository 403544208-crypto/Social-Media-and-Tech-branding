"""Appends conversation turns to a JSONL log file."""
import json
import datetime
from pathlib import Path


LOGS_DIR = Path(__file__).parent.parent / "logs"


def _log_path() -> Path:
    LOGS_DIR.mkdir(exist_ok=True)
    date_str = datetime.date.today().isoformat()
    return LOGS_DIR / f"{date_str}.jsonl"


def append_turn(role: str, content: str, session_id: str):
    entry = {
        "session_id": session_id,
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "role": role,
        "content": content,
    }
    with _log_path().open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_session(session_id: str) -> list[dict]:
    """Return all turns for a given session_id from today's log."""
    path = _log_path()
    if not path.exists():
        return []
    turns = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        if entry["session_id"] == session_id:
            turns.append({"role": entry["role"], "content": entry["content"]})
    return turns
