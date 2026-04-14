"""
Synthesizer: Personal Behavioral Model
Builds a learning model of what conditions produce high-output days for THIS user.

Runs weekly (Sunday) after enough data accumulates (7+ days minimum).
Reads coaching_log.md + daily/ logs to find:
  - Which prescription types actually improved performance
  - What environmental conditions correlate with high output
  - Personal behavioral fingerprint (your specific patterns, not generic ones)

Output: analysis/behavioral_model.md
  - Your top 3 output triggers (data-backed)
  - Your top 3 output killers (data-backed)
  - Prescription effectiveness table (which coaching interventions worked)
  - Confidence level (how much data backs each claim)

This is the difference between a new coach and a coach who's worked with you for 6 months.
After 30 days, engram knows things about your work patterns you don't know yourself.
"""

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

TODAY = date.today().isoformat()
MIN_DAYS_FOR_MODEL = 7   # minimum before building model
STRONG_CONFIDENCE = 14   # days before "strong" confidence claims


def build_model(daily_dir: Path, analysis_dir: Path, call_claude_fn=None) -> str:
    """
    Build personal behavioral model from all available daily logs.
    Returns markdown section to write to behavioral_model.md.
    """
    # Load all daily logs
    daily_data = _load_daily_series(daily_dir)
    if len(daily_data) < MIN_DAYS_FOR_MODEL:
        return ""

    # Load coaching history
    coaching_log = _load_coaching_log(analysis_dir)

    # Compute correlations
    correlations = _compute_correlations(daily_data)

    # Analyze prescription effectiveness
    effectiveness = _analyze_effectiveness(coaching_log, daily_data)

    # Build or enhance model with Claude
    if call_claude_fn and len(daily_data) >= STRONG_CONFIDENCE:
        model = _ai_model(daily_data, correlations, effectiveness, call_claude_fn)
    else:
        model = _heuristic_model(daily_data, correlations, effectiveness)

    return _format_model(model, len(daily_data))


def update_model_file(content: str, analysis_dir: Path) -> None:
    model_file = analysis_dir / "behavioral_model.md"
    model_file.write_text(content)


# ── Data loading ───────────────────────────────────────────────────────────────

def _load_daily_series(daily_dir: Path) -> list[dict]:
    """Load all daily logs, extract key metrics per day."""
    entries = []
    for f in sorted(daily_dir.glob("*.md"), reverse=True)[:90]:  # Last 90 days max
        day_str = f.stem
        try:
            date.fromisoformat(day_str)
        except ValueError:
            continue
        content = f.read_text()
        entries.append({
            "date": day_str,
            "weekday": date.fromisoformat(day_str).strftime("%A"),
            "commits": _extract_int(content, r"(\d+)\s+commit"),
            "repos": _extract_int(content, r"(\d+)\s+repo"),
            "focus_score": _extract_int(content, r"[Ff]ocus[:\s]+(\d+)"),
            "sessions": _extract_int(content, r"(\d+)\s+[Cc]laude\s+session"),
            "has_meeting_mention": bool(re.search(r"\bmeeting|standup|sync\b", content, re.I)),
            "has_launch_mention": bool(re.search(r"\blaunch|deploy|ship\b", content, re.I)),
            "has_blocked_mention": bool(re.search(r"\bblocked|stuck|waiting\b", content, re.I)),
            "raw_length": len(content),
        })
    return entries


def _load_coaching_log(analysis_dir: Path) -> list[dict]:
    p = analysis_dir / "coaching_log.md"
    if not p.exists():
        return []
    content = p.read_text()
    entries = []
    for block in re.split(r"(?=^## \d{4}-\d{2}-\d{2})", content, flags=re.MULTILINE):
        if not block.strip():
            continue
        date_m = re.search(r"## (\d{4}-\d{2}-\d{2})", block)
        law_m = re.search(r"Atomic Habits:\s*([^\)]+)\)", block)
        action_m = re.search(r">\s*(.+)", block)
        followthrough_m = re.search(r"\*\*Yesterday.*?\*\*\s*(✓|✗)", block)
        target_m = re.search(r"target_metric.*?`([^`]+)`.*?`([^`]+)`", block)

        if date_m:
            entries.append({
                "date": date_m.group(1),
                "law": law_m.group(1).strip() if law_m else None,
                "action": action_m.group(1).strip() if action_m else None,
                "followed": followthrough_m.group(1) == "✓" if followthrough_m else None,
                "target_metric": target_m.group(1) if target_m else None,
                "target_value": target_m.group(2) if target_m else None,
            })
    return entries


# ── Correlation analysis ───────────────────────────────────────────────────────

def _compute_correlations(daily_data: list[dict]) -> dict:
    """Find what correlates with high-output days."""
    if not daily_data:
        return {}

    commits_series = [d["commits"] for d in daily_data if d["commits"] > 0]
    if not commits_series:
        return {}

    avg = sum(commits_series) / len(commits_series)
    p75 = sorted(commits_series)[int(len(commits_series) * 0.75)]

    high_days = [d for d in daily_data if d["commits"] >= p75 and p75 > 0]
    low_days = [d for d in daily_data if 0 < d["commits"] < avg * 0.5]
    zero_days = [d for d in daily_data if d["commits"] == 0]

    # Weekday distribution
    weekday_commits = {}
    for d in daily_data:
        wd = d["weekday"]
        weekday_commits.setdefault(wd, []).append(d["commits"])
    weekday_avg = {wd: sum(v)/len(v) for wd, v in weekday_commits.items() if v}
    best_day = max(weekday_avg, key=weekday_avg.get) if weekday_avg else None
    worst_day = min(weekday_avg, key=weekday_avg.get) if weekday_avg else None

    # Meeting correlation
    high_with_meetings = sum(1 for d in high_days if d["has_meeting_mention"])
    low_with_meetings = sum(1 for d in low_days if d["has_meeting_mention"])
    meeting_kills_output = (
        low_with_meetings / max(len(low_days), 1) >
        high_with_meetings / max(len(high_days), 1) + 0.2
    )

    # Launch/deploy effect
    launch_days = [d for d in daily_data if d["has_launch_mention"]]
    post_launch_crash = 0
    for i, d in enumerate(daily_data):
        if d["has_launch_mention"] and i > 0:
            next_day = daily_data[i - 1]  # sorted desc
            if next_day["commits"] < avg * 0.3:
                post_launch_crash += 1

    # Repo concentration
    high_repos_avg = sum(d["repos"] for d in high_days) / max(len(high_days), 1)
    low_repos_avg = sum(d["repos"] for d in low_days) / max(len(low_days), 1)
    focus_beats_spread = high_repos_avg < low_repos_avg - 1

    return {
        "avg_commits": round(avg, 1),
        "p75_commits": round(p75, 1),
        "high_days_count": len(high_days),
        "low_days_count": len(low_days),
        "zero_days_count": len(zero_days),
        "best_weekday": best_day,
        "worst_weekday": worst_day,
        "weekday_avgs": {k: round(v, 1) for k, v in sorted(weekday_avg.items(), key=lambda x: -x[1])},
        "meeting_kills_output": meeting_kills_output,
        "post_launch_crash_count": post_launch_crash,
        "focus_beats_spread": focus_beats_spread,
        "high_repos_avg": round(high_repos_avg, 1),
        "low_repos_avg": round(low_repos_avg, 1),
        "total_days": len(daily_data),
    }


def _analyze_effectiveness(coaching_log: list[dict], daily_data: list[dict]) -> dict:
    """Which prescription types actually improved performance?"""
    if not coaching_log or not daily_data:
        return {}

    daily_by_date = {d["date"]: d for d in daily_data}
    law_outcomes = {}

    for entry in coaching_log:
        if entry.get("followed") is None:
            continue
        law = entry.get("law", "unknown")
        date_str = entry["date"]

        # Check next day's performance
        entry_date = date.fromisoformat(date_str)
        next_date = (entry_date + timedelta(days=1)).isoformat()
        next_day = daily_by_date.get(next_date)

        if next_day:
            law_outcomes.setdefault(law, {"followed_commits": [], "ignored_commits": []})
            commits = next_day["commits"]
            if entry["followed"]:
                law_outcomes[law]["followed_commits"].append(commits)
            else:
                law_outcomes[law]["ignored_commits"].append(commits)

    effectiveness = {}
    for law, data in law_outcomes.items():
        f = data["followed_commits"]
        ig = data["ignored_commits"]
        if f:
            avg_followed = sum(f) / len(f)
            avg_ignored = sum(ig) / len(ig) if ig else 0
            lift = avg_followed - avg_ignored
            effectiveness[law] = {
                "avg_commits_when_followed": round(avg_followed, 1),
                "avg_commits_when_ignored": round(avg_ignored, 1),
                "lift": round(lift, 1),
                "sample_size": len(f) + len(ig),
                "follow_rate": round(len(f) / (len(f) + len(ig)), 2),
            }

    return effectiveness


# ── Model generation ───────────────────────────────────────────────────────────

def _heuristic_model(daily_data, correlations, effectiveness) -> dict:
    triggers = []
    killers = []
    c = correlations

    if c.get("best_weekday") and c.get("weekday_avgs"):
        best = c["best_weekday"]
        avg_best = c["weekday_avgs"].get(best, 0)
        triggers.append({
            "finding": f"{best} is your highest-output day",
            "data": f"avg {avg_best} commits vs overall avg {c['avg_commits']}",
            "confidence": "medium" if c["total_days"] < STRONG_CONFIDENCE else "high",
        })

    if c.get("focus_beats_spread"):
        triggers.append({
            "finding": "Single-repo focus days outperform multi-repo days",
            "data": f"high days avg {c['high_repos_avg']} repos, low days avg {c['low_repos_avg']} repos",
            "confidence": "medium" if c["total_days"] < STRONG_CONFIDENCE else "high",
        })

    if c.get("worst_weekday") and c.get("weekday_avgs"):
        worst = c["worst_weekday"]
        avg_worst = c["weekday_avgs"].get(worst, 0)
        killers.append({
            "finding": f"{worst} is consistently your lowest-output day",
            "data": f"avg {avg_worst} commits — suspect: scheduled meetings or context switching",
            "confidence": "medium" if c["total_days"] < STRONG_CONFIDENCE else "high",
        })

    if c.get("meeting_kills_output"):
        killers.append({
            "finding": "Days with meetings have lower commit output",
            "data": "Meeting mentions correlate with low-output pattern",
            "confidence": "medium",
        })

    if c.get("post_launch_crash_count", 0) >= 2:
        killers.append({
            "finding": "Post-launch crash pattern detected",
            "data": f"{c['post_launch_crash_count']} times: day after a launch had <30% of avg output",
            "confidence": "high" if c["post_launch_crash_count"] >= 3 else "medium",
        })

    return {
        "triggers": triggers,
        "killers": killers,
        "effectiveness": effectiveness,
        "total_days": c.get("total_days", 0),
        "avg_commits": c.get("avg_commits", 0),
        "p75_commits": c.get("p75_commits", 0),
    }


def _ai_model(daily_data, correlations, effectiveness, call_claude_fn) -> dict:
    prompt = f"""You are analyzing a developer's behavioral data to build a personal model of what drives high output.

Data summary ({correlations.get('total_days', 0)} days):
- Average commits/day: {correlations.get('avg_commits', 0)}
- Top 25% threshold: {correlations.get('p75_commits', 0)} commits
- High output days: {correlations.get('high_days_count', 0)}
- Zero days: {correlations.get('zero_days_count', 0)}
- Best weekday: {correlations.get('best_weekday')} (avg {correlations.get('weekday_avgs', {}).get(correlations.get('best_weekday',''), 0)})
- Worst weekday: {correlations.get('worst_weekday')}
- Meeting days kill output: {correlations.get('meeting_kills_output')}
- Focus (fewer repos) beats spread: {correlations.get('focus_beats_spread')}
- Post-launch crashes: {correlations.get('post_launch_crash_count', 0)}

Prescription effectiveness:
{json.dumps(effectiveness, indent=2)}

Generate a personal behavioral model. Return JSON:
{{
  "triggers": [
    {{"finding": "specific data-backed trigger", "data": "exact numbers", "confidence": "high|medium|low"}}
  ],
  "killers": [
    {{"finding": "specific data-backed output killer", "data": "exact numbers", "confidence": "high|medium|low"}}
  ],
  "insight": "The single most surprising non-obvious finding from this data. 2 sentences max.",
  "prescription_strategy": "Based on effectiveness data, which Atomic Habits law works best for this person and why."
}}

Return ONLY valid JSON. Be specific — real numbers, no generic advice."""

    try:
        response = call_claude_fn(prompt)
        if response:
            m = re.search(r'\{.*\}', response.strip(), re.DOTALL)
            if m:
                ai_result = json.loads(m.group(0))
                ai_result["total_days"] = correlations.get("total_days", 0)
                ai_result["avg_commits"] = correlations.get("avg_commits", 0)
                ai_result["p75_commits"] = correlations.get("p75_commits", 0)
                ai_result["effectiveness"] = effectiveness
                return ai_result
    except Exception:
        pass

    return _heuristic_model(daily_data, correlations, effectiveness)


# ── Formatting ─────────────────────────────────────────────────────────────────

def _format_model(model: dict, days: int) -> str:
    confidence_note = (
        f"High confidence ({days} days)" if days >= STRONG_CONFIDENCE
        else f"Building confidence ({days}/{STRONG_CONFIDENCE} days for strong claims)"
    )

    lines = [
        f"# Personal Behavioral Model",
        f"",
        f"_Generated {TODAY} · {confidence_note}_",
        f"_Based on {days} days of behavioral data. Updates weekly._",
        f"",
        f"avg output: **{model.get('avg_commits', '?')} commits/day** · top 25%: **{model.get('p75_commits', '?')}+**",
        f"",
        f"---",
        f"",
        f"## Output Triggers",
        f"",
    ]

    for t in model.get("triggers", []):
        conf_icon = {"high": "●●●", "medium": "●●○", "low": "●○○"}.get(t.get("confidence", "low"), "●○○")
        lines += [
            f"**{t['finding']}** `{conf_icon}`",
            f"→ {t['data']}",
            "",
        ]

    if not model.get("triggers"):
        lines.append("_Not enough data yet — needs 7+ days_\n")

    lines += [
        f"## Output Killers",
        f"",
    ]

    for k in model.get("killers", []):
        conf_icon = {"high": "●●●", "medium": "●●○", "low": "●○○"}.get(k.get("confidence", "low"), "●○○")
        lines += [
            f"**{k['finding']}** `{conf_icon}`",
            f"→ {k['data']}",
            "",
        ]

    if not model.get("killers"):
        lines.append("_Not enough data yet_\n")

    if model.get("insight"):
        lines += ["## Non-Obvious Finding", "", model["insight"], ""]

    effectiveness = model.get("effectiveness", {})
    if effectiveness:
        lines += [
            "## Prescription Effectiveness",
            "",
            "| Law | Avg commits (followed) | Avg commits (ignored) | Lift | Follow rate |",
            "|-----|------------------------|----------------------|------|-------------|",
        ]
        for law, data in sorted(effectiveness.items(), key=lambda x: -x[1].get("lift", 0)):
            lines.append(
                f"| {law} | {data['avg_commits_when_followed']} | "
                f"{data['avg_commits_when_ignored']} | "
                f"{'+' if data['lift'] >= 0 else ''}{data['lift']} | "
                f"{int(data['follow_rate']*100)}% |"
            )
        lines.append("")

    if model.get("prescription_strategy"):
        lines += ["## Coaching Strategy for You", "", model["prescription_strategy"], ""]

    return "\n".join(lines)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _extract_int(text: str, pattern: str) -> int:
    m = re.search(pattern, text)
    if m:
        try:
            return int(m.group(1))
        except (ValueError, IndexError):
            pass
    return 0
