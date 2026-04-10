"""
Collector: Input Habits
Analyzes typing patterns, shortcut usage, input velocity.
Uses ActivityWatch aw-watcher-input for keyboard/mouse stats.
Does NOT capture actual keystrokes — only counts and rhythms.

Also analyzes: terminal command patterns (with sensitive data redacted).
"""

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request

import config as cfg


AW_BASE = "http://localhost:5600/api/0"
SHELL_HISTORY = [
    Path("~/.zsh_history").expanduser(),
    Path("~/.bash_history").expanduser(),
    Path("~/.local/share/fish/fish_history").expanduser(),
]


def collect(today: str) -> dict:
    result = {
        "keyboard": _collect_keyboard(today),
        "shell_commands": _collect_shell_history(today),
        "patterns": {},
    }
    result["patterns"] = _analyze_patterns(result)
    return result


def _collect_keyboard(today: str) -> dict:
    """Get keyboard event stats from ActivityWatch aw-watcher-input."""
    try:
        req = Request(f"{AW_BASE}/buckets")
        with urlopen(req, timeout=3) as r:
            buckets = json.loads(r.read())

        input_bucket = next(
            (b for b in buckets if "input" in b.lower()), None
        )
        if not input_bucket:
            return {"note": "aw-watcher-input not found"}

        offset = datetime.now(timezone.utc).astimezone().utcoffset()
        total_sec = int(offset.total_seconds())
        h, r = divmod(abs(total_sec), 3600)
        tz = f"{'+' if total_sec >= 0 else '-'}{h:02d}:{r // 60:02d}"
        start = f"{today}T00:00:00{tz}"
        end = f"{today}T23:59:59{tz}"
        url = f"{AW_BASE}/buckets/{input_bucket}/events?start={start}&end={end}&limit=100000"
        with urlopen(Request(url), timeout=5) as r:
            events = json.loads(r.read())

        total_keys = sum(e.get("data", {}).get("presses", 0) for e in events)
        total_clicks = sum(e.get("data", {}).get("clicks", 0) for e in events)
        active_minutes = len([e for e in events if e.get("data", {}).get("presses", 0) > 0])
        wpm_estimate = round((total_keys / 5) / max(active_minutes, 1), 1)

        return {
            "total_keystrokes": total_keys,
            "total_clicks": total_clicks,
            "active_typing_minutes": active_minutes,
            "wpm_estimate": wpm_estimate,
            "intensity": _classify_intensity(total_keys),
        }
    except Exception as e:
        return {"note": str(e)}


def _collect_shell_history(today: str) -> dict:
    """Parse shell history for today's commands with date filtering."""
    today_commands = []
    all_tools = {}

    # Parse today date boundaries as epoch (explicit local timezone)
    local_tz = datetime.now(timezone.utc).astimezone().tzinfo
    today_dt = datetime.strptime(today, "%Y-%m-%d").replace(tzinfo=local_tz)
    today_start = int(today_dt.timestamp())
    today_end = today_start + 86400

    sensitive_patterns = cfg.sensitive_patterns()
    sensitive_re = re.compile("|".join(sensitive_patterns), re.IGNORECASE) if sensitive_patterns else None

    for history_file in SHELL_HISTORY:
        if not history_file.exists():
            continue
        try:
            lines = history_file.read_bytes().decode("utf-8", errors="replace").splitlines()
            for line in lines:
                cmd, ts = _parse_history_line(line)
                if not cmd:
                    continue

                # Track all-time tool usage (for top tools)
                tool = cmd.split()[0] if cmd.split() else ""
                if tool:
                    all_tools[tool] = all_tools.get(tool, 0) + 1

                # Date filter for today's commands
                if ts and today_start <= ts < today_end:
                    # Redact sensitive content
                    safe_cmd = _redact(cmd, sensitive_re) if sensitive_re else cmd
                    today_commands.append(safe_cmd)

        except Exception:
            continue

    top_tools = sorted(all_tools.items(), key=lambda x: x[1], reverse=True)[:20]

    return {
        "today_command_count": len(today_commands),
        "top_tools": [{"tool": t, "count": c} for t, c in top_tools],
        "unique_tools": len(all_tools),
        "today_sample": today_commands[-30:],  # last 30 of today
    }


def _parse_history_line(line: str) -> tuple:
    """Parse a zsh/bash history line. Returns (command, epoch_timestamp)."""
    # zsh extended history: ": 1712345678:0;actual command"
    if line.startswith(": "):
        m = re.match(r"^: (\d+):\d+;(.+)$", line)
        if m:
            return m.group(2).strip(), int(m.group(1))
    # Plain command (bash or simple zsh)
    cmd = line.strip()
    return (cmd, 0) if cmd else ("", 0)


def _redact(cmd: str, pattern: re.Pattern) -> str:
    """Replace sensitive tokens with [REDACTED]."""
    return pattern.sub("[REDACTED]", cmd)


def _analyze_patterns(data: dict) -> dict:
    patterns = {}
    kb = data.get("keyboard", {})
    shell = data.get("shell_commands", {})

    if "intensity" in kb:
        patterns["typing_intensity"] = kb["intensity"]

    top_tools = [t["tool"] for t in shell.get("top_tools", [])[:5]]
    patterns["primary_tools"] = top_tools

    unique = shell.get("unique_tools", 0)
    patterns["work_diversity"] = (
        "focused" if unique < 5
        else "balanced" if unique < 15
        else "scattered"
    )

    return patterns


def _classify_intensity(keystrokes: int) -> str:
    if keystrokes < 1000:
        return "light"
    elif keystrokes < 5000:
        return "moderate"
    elif keystrokes < 15000:
        return "heavy"
    else:
        return "extreme"
