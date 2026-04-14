"""
Collector: Claude Context Monitor
Reads ~/.claude/sessions/ state files written by the cpi/ct/cs tool suite.
Extracts per-session: context%, tool call depth, activity patterns, project mapping.
Detects: overflow sessions, shallow usage, project-specific patterns.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, date, timezone
from pathlib import Path


STATE_DIR = Path("~/.claude/sessions").expanduser()
MAX_CALLS = int(__import__("os").environ.get("CLAUDE_CTX_MAX_CALLS", "400"))


def collect(today: str = None) -> dict:
    today = today or date.today().isoformat()
    sessions = []
    overflow = []      # sessions that hit >90% context
    shallow = []       # sessions with <8 tool calls (likely throwaway)
    deep = []          # sessions with rich activity

    if not STATE_DIR.exists():
        return {"note": "~/.claude/sessions not found", "sessions": []}

    # Find all session UUIDs (have .count files)
    session_ids = set()
    for f in STATE_DIR.glob("*.count"):
        sid = f.stem
        if _looks_like_uuid(sid) or _looks_like_tmux_key(sid):
            session_ids.add(sid)

    for sid in session_ids:
        s = _parse_session(sid, today)
        if not s:
            continue
        sessions.append(s)

        ctx_pct = s.get("context_pct", 0)
        calls = s.get("tool_calls", 0)

        if ctx_pct >= 90:
            overflow.append({"session": sid[:8], "ctx_pct": ctx_pct,
                             "project": s.get("project", "?"), "calls": calls})
        elif calls < 8 and calls > 0:
            shallow.append({"session": sid[:8], "calls": calls,
                           "project": s.get("project", "?")})
        elif calls >= 20:
            deep.append({"session": sid[:8], "calls": calls,
                        "project": s.get("project", "?"), "ctx_pct": ctx_pct})

    # Aggregate stats
    all_ctx = [s["context_pct"] for s in sessions if s.get("context_pct", 0) > 0]
    all_calls = [s["tool_calls"] for s in sessions if s.get("tool_calls", 0) > 0]
    all_adds = sum(s.get("total_adds", 0) for s in sessions)
    all_dels = sum(s.get("total_dels", 0) for s in sessions)

    # Project breakdown
    project_map = {}
    for s in sessions:
        proj = s.get("project", "unknown")
        project_map.setdefault(proj, {"sessions": 0, "total_calls": 0,
                                       "max_ctx": 0, "edits": 0})
        project_map[proj]["sessions"] += 1
        project_map[proj]["total_calls"] += s.get("tool_calls", 0)
        project_map[proj]["max_ctx"] = max(
            project_map[proj]["max_ctx"], s.get("context_pct", 0))
        project_map[proj]["edits"] += s.get("total_adds", 0) + s.get("total_dels", 0)

    # Quality signals
    quality = _compute_quality(sessions, overflow, shallow, deep)

    return {
        "session_count": len(sessions),
        "avg_context_pct": round(sum(all_ctx) / len(all_ctx), 1) if all_ctx else 0,
        "avg_tool_calls": round(sum(all_calls) / len(all_calls), 1) if all_calls else 0,
        "total_file_adds": all_adds,
        "total_file_dels": all_dels,
        "overflow_sessions": overflow,         # hit >90% context
        "shallow_sessions": shallow,           # <8 tool calls
        "deep_sessions": deep,                 # ≥20 tool calls
        "project_breakdown": project_map,
        "quality": quality,
        "sessions": sessions[:30],
    }


def _parse_session(sid: str, today: str) -> dict | None:
    count_f = STATE_DIR / f"{sid}.count"
    level_f = STATE_DIR / f"{sid}.level"
    activity_f = STATE_DIR / f"{sid}.activity.jsonl"
    monitor_f = STATE_DIR / f"{sid}.monitor.log"

    try:
        count = int(count_f.read_text().strip()) if count_f.exists() else 0
        level = level_f.read_text().strip() if level_f.exists() else "?"
    except Exception:
        return None

    ctx_pct = round(count * 100 / MAX_CALLS, 1) if MAX_CALLS > 0 else 0

    # Activity log: tool calls with timestamps
    tool_calls = 0
    total_adds = 0
    total_dels = 0
    tools_used = {}
    project_cwd = None
    today_activity = False

    if activity_f.exists():
        for line in activity_f.read_text(errors="ignore").splitlines():
            try:
                ev = json.loads(line.strip())
                # Check if this activity is from today
                ts = ev.get("ts", "")
                if today in ts:
                    today_activity = True
                elif ts and today not in ts:
                    continue  # skip old activity

                tool = ev.get("tool", "")
                if tool:
                    tool_calls += 1
                    tools_used[tool] = tools_used.get(tool, 0) + 1
                total_adds += ev.get("add", 0)
                total_dels += ev.get("del", 0)
                if not project_cwd and ev.get("cwd"):
                    project_cwd = ev.get("cwd")
            except Exception:
                continue

    # Monitor log: extract project path from most recent entries
    if not project_cwd and monitor_f.exists():
        try:
            lines = monitor_f.read_text(errors="ignore").splitlines()
            # look for any path hints in monitor log
            for line in reversed(lines[-20:]):
                if today in line:
                    today_activity = True
                    break
        except Exception:
            pass

    # If no today activity but file was modified today, still include
    if not today_activity:
        try:
            mtime = activity_f.stat().st_mtime if activity_f.exists() else 0
            if mtime == 0:
                mtime = count_f.stat().st_mtime if count_f.exists() else 0
            file_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            if file_date != today:
                return None
        except Exception:
            return None

    # Derive project name from cwd
    project = "unknown"
    if project_cwd:
        project = Path(project_cwd).name

    # Estimate session depth quality
    depth = "shallow"
    if tool_calls >= 30:
        depth = "deep"
    elif tool_calls >= 15:
        depth = "medium"
    elif tool_calls >= 8:
        depth = "light"

    return {
        "session_id": sid[:16],
        "context_pct": ctx_pct,
        "context_level": level,
        "tool_calls": tool_calls,
        "depth": depth,
        "tools_used": tools_used,
        "total_adds": total_adds,
        "total_dels": total_dels,
        "project": project,
        "project_cwd": project_cwd,
    }


def _compute_quality(sessions, overflow, shallow, deep) -> dict:
    total = len(sessions)
    if total == 0:
        return {"score": 0, "signals": [], "recommendations": []}

    signals = []
    recommendations = []
    score = 100

    # Penalty: overflow sessions without enough deep work to justify it
    overflow_ratio = len(overflow) / total if total > 0 else 0
    if overflow_ratio > 0.3:
        score -= 20
        signals.append(f"{len(overflow)}/{total} sessions hit >90% context — likely not using /compact or subagents early enough")
        recommendations.append("Run /compact when context hits ~60%, not when it's already full")

    # Penalty: high shallow ratio
    shallow_ratio = len(shallow) / total if total > 0 else 0
    if shallow_ratio > 0.5:
        score -= 15
        signals.append(f"{len(shallow)}/{total} sessions had <8 tool calls — many throwaway conversations")
        recommendations.append("Consolidate quick questions into fewer, deeper sessions")

    # Bonus: deep sessions exist
    if len(deep) >= 2:
        score = min(score + 10, 100)
        signals.append(f"{len(deep)} deep sessions (≥20 tool calls) — good depth on some work")

    # Penalty: all sessions shallow (no deep work at all)
    if len(deep) == 0 and total > 5:
        score -= 10
        signals.append("No deep sessions today — all interactions were shallow")
        recommendations.append("For architecture/design work, commit to a single long session instead of many short ones")

    # Penalty: single project monopolizes context overflow
    if overflow:
        overflow_projects = [o["project"] for o in overflow]
        if len(set(overflow_projects)) == 1:
            proj = overflow_projects[0]
            score -= 10
            signals.append(f"All context overflows on project '{proj}' — this project needs subagent decomposition")
            recommendations.append(f"For {proj}: break large tasks into subagents with isolation:worktree")

    return {
        "score": max(score, 0),
        "signals": signals,
        "recommendations": recommendations,
        "overflow_count": len(overflow),
        "shallow_count": len(shallow),
        "deep_count": len(deep),
    }


def _looks_like_uuid(s: str) -> bool:
    return bool(re.match(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        s, re.IGNORECASE))


def _looks_like_tmux_key(s: str) -> bool:
    # tmux session keys like "cl-projectname-abc123"
    return bool(re.match(r'^cl-[a-z0-9-]+$', s))
