"""
Synthesizer: Daily Behavioral Coach
Generates tomorrow's specific behavioral prescription from today's data.

A fitness coach doesn't just measure you — they tell you exactly what to do
tomorrow, track whether you did it, and adjust based on what worked.

This is the difference between engram as a mirror and engram as a coach.

Output: analysis/coaching_log.md
  - Today's prescription (1 specific behavior change, 1 specific action)
  - Yesterday's prescription outcome (did the user follow through?)
  - 30-day prescription effectiveness tracker

No API key required — heuristic-driven with optional Claude enhancement.
"""

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

TODAY = date.today().isoformat()
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()


# ── Core prescription logic ────────────────────────────────────────────────────

def synthesize(raw: dict, analysis_dir: Path, call_claude_fn=None) -> str:
    """
    Generate today's coaching prescription.
    Returns markdown section to prepend to coaching_log.md.

    call_claude_fn: optional callable(prompt) -> str for AI-enhanced coaching.
    If None, uses heuristic coaching only.
    """
    git = raw.get("git_activity", {})
    sessions = raw.get("claude_sessions", {})
    ctx = raw.get("claude_context", {})
    framework = _read_framework_state(analysis_dir)
    coaching_log = _read_coaching_log(analysis_dir)

    # Assess today's performance
    today_metrics = _assess_today(git, sessions, ctx)

    # Check follow-through on yesterday's prescription
    followthrough = _assess_followthrough(coaching_log, today_metrics)

    # Generate tomorrow's prescription
    if call_claude_fn:
        prescription = _ai_prescription(
            today_metrics, followthrough, framework, coaching_log, call_claude_fn
        )
    else:
        prescription = _heuristic_prescription(today_metrics, followthrough, framework)

    # Build the log entry
    entry = _format_entry(today_metrics, followthrough, prescription)
    return entry


def update_coaching_file(entry: str, analysis_dir: Path) -> None:
    """Prepend today's entry to coaching_log.md (newest first)."""
    coaching_file = analysis_dir / "coaching_log.md"
    header = "# Behavioral Coaching Log\n\n_Prescriptions + outcomes. Newest first._\n\n---\n\n"

    if coaching_file.exists():
        existing = coaching_file.read_text()
        # Remove header if already present
        existing = re.sub(r'^# Behavioral Coaching Log.*?---\n\n', '', existing,
                          flags=re.DOTALL)
        coaching_file.write_text(header + entry + "\n---\n\n" + existing)
    else:
        coaching_file.write_text(header + entry + "\n---\n\n")


# ── Assessment ─────────────────────────────────────────────────────────────────

def _assess_today(git: dict, sessions: dict, ctx: dict) -> dict:
    commits = git.get("total_commits", 0)
    repos = len(git.get("repos_touched", []))
    session_count = sessions.get("session_count", 0) or ctx.get("session_count", 0)
    avg_ctx = ctx.get("avg_context_pct", 0)
    overflow = ctx.get("overflow_sessions", [])

    # Derive focus signal
    if repos == 0 and commits == 0:
        focus_level = "zero"
        focus_note = "no activity detected"
    elif repos >= 5 or (repos > 0 and commits > 0 and commits / repos < 3):
        focus_level = "fragmented"
        focus_note = f"{commits} commits across {repos} repos — shallow touch pattern"
    elif commits >= 30:
        focus_level = "high"
        focus_note = f"{commits} commits, {repos} repos — concentrated output"
    elif commits >= 10:
        focus_level = "moderate"
        focus_note = f"{commits} commits — solid session"
    else:
        focus_level = "low"
        focus_note = f"{commits} commits — below demonstrated capacity"

    # Context depth signal
    if avg_ctx >= 80:
        context_signal = "overflow_risk"
    elif avg_ctx >= 60:
        context_signal = "heavy"
    elif session_count >= 6:
        context_signal = "many_sessions"
    else:
        context_signal = "normal"

    return {
        "date": TODAY,
        "commits": commits,
        "repos": repos,
        "session_count": session_count,
        "avg_context_pct": avg_ctx,
        "overflow_sessions": len(overflow),
        "focus_level": focus_level,
        "focus_note": focus_note,
        "context_signal": context_signal,
    }


def _assess_followthrough(coaching_log: list, today_metrics: dict) -> dict:
    """Check if today's behavior matches yesterday's prescription."""
    if not coaching_log:
        return {"status": "no_prior_prescription", "note": "first day tracked"}

    last = coaching_log[0]
    prescription = last.get("prescription", {})
    target = prescription.get("target_metric")
    target_value = prescription.get("target_value")
    action = prescription.get("action", "")

    if not target:
        return {"status": "no_measurable_target", "note": "prescription had no measurable target"}

    # Compare today's actual vs prescribed target
    actual = today_metrics.get(target, 0)
    if target_value is None:
        return {"status": "unmeasurable", "note": f"target {target} has no numeric goal"}

    if isinstance(target_value, str) and target_value.startswith("<="):
        threshold = float(target_value[2:])
        followed = actual <= threshold
        diff = f"actual {actual}, target {target_value}"
    elif isinstance(target_value, str) and target_value.startswith(">="):
        threshold = float(target_value[2:])
        followed = actual >= threshold
        diff = f"actual {actual}, target {target_value}"
    else:
        # Direction only
        followed = None
        diff = f"actual {actual}"

    return {
        "status": "followed" if followed else ("not_followed" if followed is False else "unknown"),
        "prescribed_action": action,
        "target_metric": target,
        "target_value": target_value,
        "actual_value": actual,
        "diff": diff,
        "note": f"prescribed: {action}",
    }


# ── Prescription generation ────────────────────────────────────────────────────

def _heuristic_prescription(metrics: dict, followthrough: dict, framework: str) -> dict:
    """
    Rule-based prescription. No API needed.
    Returns: {action, target_metric, target_value, rationale, law}
    """
    focus = metrics["focus_level"]
    repos = metrics["repos"]
    commits = metrics["commits"]
    ctx_signal = metrics["context_signal"]
    overflow = metrics["overflow_sessions"]

    # Priority 1: Context overflow — most damaging, fix first
    if overflow > 0 or ctx_signal == "overflow_risk":
        return {
            "action": f"Before opening Claude Code tomorrow: write a 3-sentence context brief in a scratch file. Use /compact at 60%, not 90%.",
            "target_metric": "overflow_sessions",
            "target_value": "<=0",
            "rationale": f"{overflow} sessions hit context overflow today. Overflow at 90% means last 30% of your session was operating on compressed, degraded context.",
            "law": "Make it Easy",
        }

    # Priority 2: Fragmented focus
    if focus == "fragmented" and repos >= 4:
        return {
            "action": f"Tomorrow: pick 2 repos max before 12pm. Write them down before opening the terminal. Close other repo tabs.",
            "target_metric": "repos",
            "target_value": f"<={min(repos - 1, 3)}",
            "rationale": f"Today: {commits} commits across {repos} repos. Pattern: shallow-touch fragmentation. Your 9x days are single-repo concentration events.",
            "law": "Make it Obvious",
        }

    # Priority 3: Zero day after active day
    if focus == "zero":
        return {
            "action": "Tomorrow: 1 commit before 10am. Any commit. Opens the loop and breaks the zero pattern.",
            "target_metric": "commits",
            "target_value": ">=1",
            "rationale": "Zero days compound. First commit of the day is the hardest — make it trivially small.",
            "law": "Make it Easy",
        }

    # Priority 4: Low output
    if focus == "low":
        return {
            "action": f"Tomorrow: identify your single highest-priority task tonight before you sleep. Write it as 1 sentence. Start there, not email.",
            "target_metric": "commits",
            "target_value": f">={max(commits + 5, 10)}",
            "rationale": f"Today: {commits} commits. Below your demonstrated capacity. The constraint is usually decision cost at session start, not energy.",
            "law": "Make it Obvious",
        }

    # Priority 5: Good day — maintain and improve
    if focus in ("high", "moderate"):
        return {
            "action": f"Tomorrow: protect the first 90 minutes. No meetings, no Slack until 10:30am. Today worked — replicate the conditions.",
            "target_metric": "commits",
            "target_value": f">={commits}",
            "rationale": f"Today: {commits} commits — solid. The goal tomorrow is to identify what made today work, then protect it.",
            "law": "Make it Satisfying",
        }

    return {
        "action": "Tomorrow: pick one thing to improve. Measure it.",
        "target_metric": "commits",
        "target_value": ">=1",
        "rationale": "Default prescription — more data needed.",
        "law": "Make it Easy",
    }


def _ai_prescription(metrics: dict, followthrough: dict, framework: str,
                     coaching_log: list, call_claude_fn) -> dict:
    """Claude-enhanced prescription using behavioral history."""
    recent = coaching_log[:7]  # Last 7 days
    recent_str = json.dumps(recent, ensure_ascii=False, indent=2) if recent else "none yet"

    prompt = f"""You are a behavioral coach analyzing a developer's work patterns.
Today: {TODAY}
Today's metrics: {json.dumps(metrics, indent=2)}
Yesterday's prescription follow-through: {json.dumps(followthrough, indent=2)}
Last 7 days prescriptions + outcomes: {recent_str}
Active project states: {framework[:600] if framework else "unknown"}

Generate ONE behavioral prescription for tomorrow. Be specific, not motivational.
The best prescriptions are environmental changes, not willpower demands.

Return JSON:
{{
  "action": "Specific thing to do tomorrow. One sentence. Concrete, not abstract.",
  "target_metric": "One of: commits | repos | overflow_sessions | session_count",
  "target_value": "Target as string: '>=N' or '<=N'",
  "rationale": "2 sentences max. Reference today's specific numbers.",
  "law": "One of: Make it Obvious | Make it Attractive | Make it Easy | Make it Satisfying"
}}

Return ONLY valid JSON."""

    try:
        response = call_claude_fn(prompt)
        if response:
            clean = response.strip()
            m = re.search(r'\{.*\}', clean, re.DOTALL)
            if m:
                return json.loads(m.group(0))
    except Exception:
        pass

    # Fallback to heuristic
    return _heuristic_prescription(metrics, followthrough, framework)


# ── Formatting ─────────────────────────────────────────────────────────────────

def _format_entry(metrics: dict, followthrough: dict, prescription: dict) -> str:
    ft_status = followthrough.get("status", "unknown")
    ft_icon = {"followed": "✓", "not_followed": "✗", "no_prior_prescription": "—",
               "no_measurable_target": "—", "unmeasurable": "—", "unknown": "?"}.get(ft_status, "?")

    lines = [
        f"## {TODAY}",
        "",
        f"**Today:** {metrics['focus_note']} · {metrics['session_count']} Claude sessions",
        "",
        f"**Yesterday's prescription:** {ft_icon} {followthrough.get('prescribed_action', '(none)')}",
    ]

    if ft_status not in ("no_prior_prescription", "no_measurable_target"):
        lines.append(f"  → {followthrough.get('diff', '')}")

    lines += [
        "",
        f"**Tomorrow's prescription** *(Atomic Habits: {prescription.get('law', '?')})*",
        "",
        f"> {prescription.get('action', '')}",
        "",
        f"*Why:* {prescription.get('rationale', '')}",
        "",
        f"*Measurable target:* `{prescription.get('target_metric', '?')}` `{prescription.get('target_value', '?')}`",
        "",
    ]
    return "\n".join(lines)


# ── File I/O ───────────────────────────────────────────────────────────────────

def _read_framework_state(analysis_dir: Path) -> str:
    p = analysis_dir / "framework_state.md"
    return p.read_text()[:800] if p.exists() else ""


def _read_coaching_log(analysis_dir: Path) -> list:
    """Parse coaching_log.md into list of prescription dicts (newest first)."""
    p = analysis_dir / "coaching_log.md"
    if not p.exists():
        return []
    content = p.read_text()
    entries = []
    # Find prescription blocks
    for m in re.finditer(
        r"## (\d{4}-\d{2}-\d{2}).*?"
        r"Tomorrow's prescription.*?\n>\s*(.*?)\n.*?"
        r"target_metric.*?`([^`]+)`.*?`([^`]+)`",
        content, re.DOTALL
    ):
        entries.append({
            "date": m.group(1),
            "prescription": {
                "action": m.group(2).strip(),
                "target_metric": m.group(3).strip(),
                "target_value": m.group(4).strip(),
            }
        })
    return entries
