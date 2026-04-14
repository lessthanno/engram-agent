"""
Synthesizer: Weekly Analysis
Aggregates 7 daily logs into a weekly report with trend analysis.
Runs Sunday 23:50 via LaunchAgent (or manually with --weekly).
"""

import json
import logging
import re
import subprocess
from datetime import date, timedelta
from pathlib import Path

import config as cfg

log = logging.getLogger("mind-sync")


def _scan_git_week(monday: date) -> list:
    """Fallback: scan raw git history for the week when daily logs are sparse.

    Returns list of day-summary strings covering Mon–Sun, ready to feed into
    the prompt the same way daily_logs does.
    """
    try:
        author = cfg.git_author_email()
    except Exception:
        author = ""

    # Find all repos (reuse logic from git_activity collector)
    try:
        from collectors.git_activity import _find_repos
        repos = _find_repos()
    except Exception:
        return []

    # Per-day commit counts across all repos
    day_counts: dict[str, list] = {}
    for i in range(7):
        day = monday + timedelta(days=i)
        day_counts[day.isoformat()] = []

    for repo in repos:
        for day_str in day_counts:
            try:
                cmd = [
                    "git", "log", "--oneline", "--no-merges",
                    f"--since={day_str} 00:00",
                    f"--until={day_str} 23:59:59",
                    "--format=%s",
                ]
                if author:
                    cmd.append(f"--author={author}")
                result = subprocess.run(
                    cmd, cwd=repo, capture_output=True, text=True, timeout=5
                )
                messages = [l.strip() for l in result.stdout.splitlines() if l.strip()]
                day_counts[day_str].extend(messages)
            except Exception:
                continue

    # Format into daily summaries
    summaries = []
    for day_str, messages in sorted(day_counts.items()):
        if messages:
            preview = ", ".join(messages[:5])
            if len(messages) > 5:
                preview += f" (+{len(messages)-5} more)"
            summaries.append(
                f"### {day_str} (git)\n"
                f"commits: {len(messages)}\n"
                f"sample: {preview}"
            )
        else:
            summaries.append(f"### {day_str} (git)\ncommits: 0")

    return summaries


def synthesize_weekly(daily_dir: Path, analysis_dir: Path, weekly_dir: Path,
                      call_claude_fn) -> dict:
    """Aggregate this week's daily logs into a weekly report.

    Args:
        daily_dir: Path to daily/ directory
        analysis_dir: Path to analysis/ directory
        weekly_dir: Path to weekly/ directory (will be created)
        call_claude_fn: callable(prompt) -> str, the LLM call function
    """
    weekly_dir.mkdir(parents=True, exist_ok=True)

    today = date.today()
    # Get Monday of this week
    monday = today - timedelta(days=today.weekday())
    week_label = f"{monday.year}-W{monday.isocalendar()[1]:02d}"

    # Collect this week's daily logs
    daily_logs = []
    for i in range(7):
        day = monday + timedelta(days=i)
        day_file = daily_dir / f"{day.isoformat()}.md"
        if day_file.exists():
            content = day_file.read_text()
            # Trim to 600 chars per day to stay within budget
            daily_logs.append(f"### {day.isoformat()}\n{content[:600]}")

    # Fallback: if fewer than 3 daily logs exist, supplement with raw git history
    # This makes --weekly useful from day 1, not just after a week of daily syncs
    if len(daily_logs) < 3:
        git_summaries = _scan_git_week(monday)
        if git_summaries:
            # Merge: replace any day we have a full log, fill the rest from git
            logged_days = {s.split("\n")[0].replace("### ", "").strip() for s in daily_logs}
            for gs in git_summaries:
                day = gs.split("\n")[0].replace("### ", "").split(" ")[0].strip()
                if day not in logged_days:
                    daily_logs.append(gs)
            log.info(f"supplemented with git history: {len(daily_logs)} days total")
        if not daily_logs:
            log.info("no daily logs and no git history found for this week, skipping")
            return {}

    # Load current analysis files for context
    tasks = _read_file(analysis_dir / "tasks.md", 500)
    patterns = _read_file(analysis_dir / "patterns.md", 800)
    weaknesses = _read_file(analysis_dir / "weaknesses.md", 800)

    user_name = cfg.user_name()
    user_ctx = cfg.user_context()
    ctx_line = f"\n{user_ctx}\n" if user_ctx else ""

    prompt = f"""You are analyzing {user_name}'s weekly behavior data to produce an Atomic Habits-framed weekly report.
{ctx_line}

## This week's daily logs ({week_label})

{chr(10).join(daily_logs)}

## Current analysis context

### Patterns
{patterns}

### Weaknesses
{weaknesses}

### Open Tasks
{tasks}

---

Produce a JSON response with this structure:

{{
  "focus_score": "X/10",
  "focus_reason": "One sharp sentence explaining the score — high output but fragmented? consistent but low velocity? The score alone means nothing without this.",

  "pattern_detected": "The single most statistically surprising pattern from this week's data. Real numbers. Not vibes. Example: 'Apr 13 produced 9.2x your daily average — the prior 4 days averaged 8 commits/day. Something unlocked.' If no spike, find the inverse: the consistent floor that's lower than expected.",

  "atomic_habits_lens": {{
    "law": "One of: Make it Obvious | Make it Attractive | Make it Easy | Make it Satisfying",
    "insight": "Apply that law to the most important pattern detected this week. Concrete, specific, not generic. 2-3 sentences max.",
    "action": "The single most important behavior change to engineer this coming week. Not 'work harder' — a specific environmental or system change."
  }},

  "open_loops": "Count of unfinished threads detected. List 3 most significant ones (project + last known state).",

  "one_thing": "The single highest-leverage action for next week. Based on the data, not intuition. 1-2 sentences.",

  "weekly_summary": "Markdown overview (200-300 words). Data-first. What actually happened, what the numbers say, what to change."
}}

Return ONLY valid JSON. Be ruthlessly specific. Avoid motivational language. The data speaks — let it."""

    response = call_claude_fn(prompt)
    if not response:
        return _offline_weekly(daily_logs, week_label)

    parsed = _parse_json(response)
    if not parsed:
        return _offline_weekly(daily_logs, week_label)

    # Write weekly report
    ah = parsed.get('atomic_habits_lens', {})
    report = f"""---
week: {week_label}
days_with_data: {len(daily_logs)}
generated: {today.isoformat()}
focus_score: {parsed.get('focus_score', '?/10')}
---

# Weekly Report — {week_label}

**Focus Score:** {parsed.get('focus_score', '?/10')} — {parsed.get('focus_reason', '')}

---

## Pattern Detected

{parsed.get('pattern_detected', '')}

---

## Atomic Habits Lens · {ah.get('law', '')}

{ah.get('insight', '')}

**Action:** {ah.get('action', '')}

---

## Open Loops

{parsed.get('open_loops', '')}

---

## One Thing

{parsed.get('one_thing', '')}

---

## Weekly Summary

{parsed.get('weekly_summary', 'No summary generated.')}
"""
    report_path = weekly_dir / f"{week_label}.md"
    report_path.write_text(report)
    log.info(f"weekly report → {report_path}")

    return {"report_path": str(report_path), "week": week_label}


def _read_file(path: Path, max_chars: int) -> str:
    if path.exists():
        return path.read_text()[:max_chars]
    return "(empty)"


def _parse_json(response: str) -> dict:
    clean = response.strip()
    # Direct parse
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass
    # Extract from markdown fences
    m = re.search(r"```(?:json)?\s*\n(\{.*?\})\s*\n```", clean, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # Find first { ... } block
    first = clean.find("{")
    last = clean.rfind("}")
    if first != -1 and last > first:
        try:
            return json.loads(clean[first:last + 1])
        except json.JSONDecodeError:
            pass
    return None


def _offline_weekly(daily_logs: list, week_label: str) -> dict:
    return {
        "report_path": None,
        "week": week_label,
        "note": f"offline — {len(daily_logs)} daily logs collected but not synthesized",
    }
