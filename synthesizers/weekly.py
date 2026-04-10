"""
Synthesizer: Weekly Analysis
Aggregates 7 daily logs into a weekly report with trend analysis.
Runs Sunday 23:50 via LaunchAgent (or manually with --weekly).
"""

import json
import logging
import re
from datetime import date, timedelta
from pathlib import Path

import config as cfg

log = logging.getLogger("mind-sync")


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

    if not daily_logs:
        log.info("no daily logs found for this week, skipping weekly synthesis")
        return {}

    # Load current analysis files for context
    tasks = _read_file(analysis_dir / "tasks.md", 500)
    patterns = _read_file(analysis_dir / "patterns.md", 800)
    weaknesses = _read_file(analysis_dir / "weaknesses.md", 800)

    user_name = cfg.user_name()
    user_ctx = cfg.user_context()
    ctx_line = f"\n{user_ctx}\n" if user_ctx else ""

    prompt = f"""You are analyzing {user_name}'s weekly activity to produce a structured weekly review.
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

Produce a JSON response:

{{
  "weekly_summary": "Markdown weekly review (300-500 words). Include: main themes of the week, progress vs stuck areas, energy trajectory (improving/declining/stable), top achievement, biggest time sink. Chinese+English mixed.",

  "trend_analysis": "Markdown section analyzing trends across the week: commit velocity trend, topic consistency vs scatter, tool usage shifts, focus score trajectory. Compare to any patterns.md observations.",

  "recommendations": "3-5 specific, actionable recommendations for next week based on this week's patterns. Not generic advice — rooted in the data."
}}

Return ONLY valid JSON."""

    response = call_claude_fn(prompt)
    if not response:
        return _offline_weekly(daily_logs, week_label)

    parsed = _parse_json(response)
    if not parsed:
        return _offline_weekly(daily_logs, week_label)

    # Write weekly report
    report = f"""---
week: {week_label}
days_with_data: {len(daily_logs)}
generated: {today.isoformat()}
---

# Weekly Review — {week_label}

{parsed.get('weekly_summary', 'No summary generated.')}

## Trend Analysis

{parsed.get('trend_analysis', '')}

## Recommendations

{parsed.get('recommendations', '')}
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
