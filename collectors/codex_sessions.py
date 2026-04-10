"""
Collector: Codex (OpenAI) Sessions
Parses ~/.codex/history.jsonl and ~/.codex/archived_sessions/ for today's activity.
Codex stores: history.jsonl (user prompts with timestamps) and archived rollout JSONL files.
"""

import json
import re
from datetime import date, datetime
from pathlib import Path

CODEX_DIR = Path("~/.codex").expanduser()
TOPIC_PATTERNS = {
    "api": r"\bapi\b|endpoint|rest\b",
    "database": r"\bdatabase\b|postgres|redis|sql\b|migration",
    "docker": r"\bdocker\b|container|dockerfile",
    "testing": r"\btest\b|jest|pytest|spec\b",
    "debug": r"\bbug\b|debug|fix\b|error",
    "agent": r"\bagent\b|multi.agent|orchestrat",
    "frontend": r"\breact\b|next\.?js\b|component|css|tailwind",
    "python": r"\bpython\b|pip\b|venv|fastapi",
    "go": r"\bgo\b.*func|goroutine|gin\b",
    "typescript": r"\btypescript\b|interface\s+\w+",
    "refactor": r"\brefactor\b|cleanup|restructur",
    "deploy": r"\bdeploy\b|ci\b|pipeline|coolify",
}


def collect(today: str) -> dict:
    if not CODEX_DIR.exists():
        return {"session_count": 0, "note": "~/.codex not found"}

    sessions = []
    prompts = []
    topics = set()
    total_chars = 0

    # 1. Parse history.jsonl (user prompts)
    history_file = CODEX_DIR / "history.jsonl"
    if history_file.exists():
        for line in history_file.read_text(errors="ignore").splitlines():
            try:
                obj = json.loads(line.strip())
                ts = obj.get("ts", 0)
                if not _is_today(ts, today):
                    continue
                text = obj.get("text", "")
                session_id = obj.get("session_id", "")
                if text:
                    prompts.append({"session_id": session_id, "text": text[:300]})
                    total_chars += len(text)
            except Exception:
                continue

    # 2. Parse archived sessions (full rollout JSONL)
    archive_dir = CODEX_DIR / "archived_sessions"
    if archive_dir.exists():
        for f in archive_dir.iterdir():
            if not f.name.endswith(".jsonl"):
                continue
            # Filename: rollout-YYYY-MM-DDTHH-MM-SS-uuid.jsonl
            if today.replace("-", "") not in f.name.replace("-", "")[:8]:
                # Quick date filter from filename
                date_part = f.name.replace("rollout-", "")[:10]
                if date_part != today:
                    continue
            try:
                session_data = _parse_rollout(f, today)
                if session_data["turns"] > 0:
                    sessions.append(session_data)
                    total_chars += session_data["total_chars"]
                    topics.update(session_data["topics"])
            except Exception:
                continue

    # Topic detection from prompts
    all_text = " ".join(p["text"] for p in prompts)
    for topic, pattern in TOPIC_PATTERNS.items():
        if re.search(pattern, all_text, re.IGNORECASE):
            topics.add(topic)

    # Deduplicate session IDs from prompts
    unique_sessions = len(set(p["session_id"] for p in prompts if p["session_id"]))

    return {
        "tool": "codex",
        "session_count": max(unique_sessions, len(sessions)),
        "prompt_count": len(prompts),
        "archived_sessions": len(sessions),
        "total_tokens_approx": total_chars // 4,
        "topics": list(topics),
        "prompts_sample": prompts[-15:],
        "sessions": sessions[:10],
    }


def _is_today(ts: int, today: str) -> bool:
    """Check if Unix timestamp falls on today."""
    if ts == 0:
        return False
    try:
        dt = datetime.fromtimestamp(ts)
        return dt.date().isoformat() == today
    except Exception:
        return False


def _parse_rollout(path: Path, today: str) -> dict:
    """Parse a Codex archived rollout JSONL file."""
    turns = 0
    total_chars = 0
    topics = set()
    model = ""
    cwd = ""

    for line in path.read_text(errors="ignore").splitlines():
        try:
            obj = json.loads(line.strip())
        except Exception:
            continue

        msg_type = obj.get("type", "")

        if msg_type == "session_meta":
            payload = obj.get("payload", {})
            model = payload.get("model_provider", "")
            cwd = payload.get("cwd", "")
            continue

        # Count conversation turns
        if msg_type in ("user_message", "assistant_message", "message"):
            turns += 1
            content = ""
            payload = obj.get("payload", obj)
            if isinstance(payload, dict):
                content = payload.get("text", "") or payload.get("content", "")
                if isinstance(content, list):
                    content = " ".join(
                        b.get("text", "") for b in content if isinstance(b, dict)
                    )
            total_chars += len(str(content))

            # Topic detection on first 500 chars
            snippet = str(content)[:500]
            for topic, pattern in TOPIC_PATTERNS.items():
                if re.search(pattern, snippet, re.IGNORECASE):
                    topics.add(topic)

    project = Path(cwd).name if cwd else path.stem
    return {
        "project": project,
        "file": path.name,
        "turns": turns,
        "total_chars": total_chars,
        "model": model,
        "topics": list(topics),
    }
