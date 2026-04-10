"""
Collector: Cursor Agent Sessions
Parses ~/.cursor/projects/*/agent-transcripts/*/*.jsonl for today's activity.
Cursor stores agent transcripts as JSONL with role/message/content structure.
"""

import json
import os
import re
from datetime import date, datetime
from pathlib import Path

CURSOR_DIR = Path("~/.cursor").expanduser()
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
    projects_dir = CURSOR_DIR / "projects"
    if not projects_dir.exists():
        return {"session_count": 0, "note": "~/.cursor/projects not found"}

    sessions = []
    topics = set()
    total_chars = 0
    files_touched = set()

    for transcript_dir in projects_dir.rglob("agent-transcripts"):
        for session_dir in transcript_dir.iterdir():
            if not session_dir.is_dir():
                continue
            for jsonl_file in session_dir.glob("*.jsonl"):
                # Quick date filter: check file modification time
                try:
                    mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)
                    if mtime.date().isoformat() != today:
                        continue
                except Exception:
                    continue

                session_data = _parse_transcript(jsonl_file, today)
                if session_data["turns"] > 0:
                    sessions.append(session_data)
                    total_chars += session_data["total_chars"]
                    topics.update(session_data["topics"])
                    files_touched.update(session_data.get("files", []))

    return {
        "tool": "cursor",
        "session_count": len(sessions),
        "total_tokens_approx": total_chars // 4,
        "topics": list(topics),
        "files_touched": list(files_touched)[:50],
        "sessions": sessions[:15],
    }


def _parse_transcript(path: Path, today: str) -> dict:
    """Parse a Cursor agent transcript JSONL file."""
    turns = 0
    total_chars = 0
    topics = set()
    files = set()
    user_messages = []

    # Extract project name from path
    # ~/.cursor/projects/Users-xiaozihao-Documents-...-projectname/agent-transcripts/...
    project = ""
    parts = path.parts
    for i, p in enumerate(parts):
        if p == "projects" and i + 1 < len(parts):
            # Last segment of the sanitized path is the project name
            project = parts[i + 1].split("-")[-1] if "-" in parts[i + 1] else parts[i + 1]
            break

    for line in path.read_text(errors="ignore").splitlines():
        try:
            obj = json.loads(line.strip())
        except Exception:
            continue

        role = obj.get("role", "")
        message = obj.get("message", {})
        content = message.get("content", "")

        if isinstance(content, list):
            texts = []
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text", "")
                    if text:
                        texts.append(text)
                    # Extract file paths from tool calls
                    if block.get("type") == "tool_use":
                        inp = block.get("input", {})
                        for k in ["path", "file_path", "filePath", "target_file"]:
                            if k in inp and isinstance(inp[k], str):
                                files.add(inp[k])
            content = " ".join(texts)
        elif not isinstance(content, str):
            content = str(content)

        if content.strip():
            turns += 1
            total_chars += len(content)

            if role == "user":
                user_messages.append(content[:300])

            # Topic detection
            snippet = content[:500]
            for topic, pattern in TOPIC_PATTERNS.items():
                if re.search(pattern, snippet, re.IGNORECASE):
                    topics.add(topic)

    return {
        "project": project,
        "file": path.name,
        "turns": turns,
        "total_chars": total_chars,
        "topics": list(topics),
        "files": list(files)[:20],
        "user_sample": user_messages[:5],
    }
