#!/usr/bin/env python3
"""
Engram Agent — Daily memory, activity, and self-analysis system.
Runs daily via LaunchAgent. Collects → Analyzes → Synthesizes → Pushes to GitHub.

Usage:
  python mind_sync.py              # full daily sync
  python mind_sync.py --collect    # collect only
  python mind_sync.py --synthesize # synthesize only (uses last collected data)
  python mind_sync.py --weekly     # generate weekly report (any day)
  python mind_sync.py --model      # rebuild personal behavioral model
  python mind_sync.py --report     # print today's coaching summary (fast, no API)
  python mind_sync.py --push       # git push only
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import config as cfg

# ── Config ────────────────────────────────────────────────────────────────────

MEMORY_REPO = cfg.memory_repo()
CLAUDE_PROJECTS = Path("~/.claude/projects").expanduser()
TODAY = date.today().isoformat()
LOG_DIR = MEMORY_REPO / "daily"
RAW_DIR = MEMORY_REPO / "raw"
ANALYSIS_DIR = MEMORY_REPO / "analysis"
WEEKLY_DIR = MEMORY_REPO / "weekly"
WIKI_DIR = MEMORY_REPO / "wiki"

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/tmp/engram-agent.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("mind-sync")

# ── Bootstrap ─────────────────────────────────────────────────────────────────

def bootstrap():
    """Ensure memory repo structure exists."""
    for d in [LOG_DIR, RAW_DIR, ANALYSIS_DIR, WIKI_DIR,
              RAW_DIR / "claude-sessions",
              RAW_DIR / "git-activity",
              RAW_DIR / "app-usage",
              RAW_DIR / "input-habits"]:
        d.mkdir(parents=True, exist_ok=True)

# ── Collection ────────────────────────────────────────────────────────────────

def collect_all():
    log.info(f"collecting data for {TODAY}")
    from collectors.claude_sessions import collect as c1
    from collectors.git_activity import collect as c2
    from collectors.app_usage import collect as c3
    from collectors.input_habits import collect as c4
    from collectors.system_ops import collect as c5
    from collectors.codex_sessions import collect as c6
    from collectors.cursor_sessions import collect as c7
    from collectors.claude_context import collect as c8

    raw = {"date": TODAY}
    collectors = [
        ("claude_sessions", lambda: c1(CLAUDE_PROJECTS, TODAY)),
        ("claude_context", lambda: c8(TODAY)),
        ("codex_sessions", lambda: c6(TODAY)),
        ("cursor_sessions", lambda: c7(TODAY)),
        ("git_activity", lambda: c2(TODAY)),
        ("app_usage", lambda: c3(TODAY)),
        ("input_habits", lambda: c4(TODAY)),
        ("system_ops", lambda: c5(TODAY)),
    ]
    # Append skill-based collectors
    try:
        from skill_loader import discover, load_function
        for skill in discover():
            if skill["type"] == "collector":
                fn = load_function(skill)
                collectors.append((skill["name"], lambda f=fn: f(TODAY)))
                log.info(f"  skill loaded: {skill['name']}")
    except Exception as e:
        log.debug(f"skill discovery skipped: {e}")

    for name, fn in collectors:
        try:
            raw[name] = fn()
            log.info(f"  {name} OK")
        except Exception as e:
            log.error(f"  {name} FAILED: {e}")
            raw[name] = {"error": str(e)}

    raw_path = RAW_DIR / f"{TODAY}.json"
    raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2))
    log.info(f"raw data → {raw_path}")
    return raw

# ── Synthesis ─────────────────────────────────────────────────────────────────

def synthesize(raw: dict):
    log.info(f"synthesizing {TODAY}")
    from synthesizers.daily import synthesize as syn
    result = syn(raw, ANALYSIS_DIR, cfg.api_key(), cfg.api_base_url(), cfg.model())

    # Write daily log
    log_path = LOG_DIR / f"{TODAY}.md"
    log_path.write_text(result["daily_log"])
    log.info(f"daily log → {log_path}")

    # Update persistent analysis files
    for filename, content in result["analysis_updates"].items():
        if not content:
            continue
        path = ANALYSIS_DIR / filename
        path.write_text(content)
        log.info(f"updated → {path}")

    return result

# ── GitHub Sync ───────────────────────────────────────────────────────────────

def git_push():
    log.info("syncing to GitHub")

    # Check if remote exists before trying to push
    has_remote = subprocess.run(
        ["git", "-C", str(MEMORY_REPO), "remote"],
        capture_output=True, text=True
    ).stdout.strip()

    cmds = [
        ["git", "-C", str(MEMORY_REPO), "add", "-A"],
        ["git", "-C", str(MEMORY_REPO), "commit", "-m",
         f"sync: {TODAY} {datetime.now().strftime('%H:%M')}"],
    ]
    if has_remote:
        cmds.append(["git", "-C", str(MEMORY_REPO), "push", "origin", "main"])
    else:
        log.info("no git remote configured, skipping push (local commit only)")

    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout + result.stderr
        if result.returncode != 0 and "nothing to commit" not in output:
            log.warning(f"git: {output.strip()}")
        else:
            log.info(f"git {' '.join(cmd[2:])} OK")

# ── Report (--report flag) ────────────────────────────────────────────────────

def _print_report(analysis_dir: Path, weekly_dir: Path, daily_dir: Path) -> None:
    """Fast read-only terminal report. No API call. Pure file reads."""
    import re
    from datetime import date, timedelta

    today = date.today().isoformat()
    lines = []
    SEP = "─" * 56

    lines.append(f"\n╔══ engram · {today} ══╗\n")

    # 1. Today's prescription
    coaching_file = analysis_dir / "coaching_log.md"
    if coaching_file.exists():
        content = coaching_file.read_text()
        # Find latest entry's prescription
        presc_m = re.search(r"Tomorrow's prescription.*?\n>\s*(.+)", content)
        law_m = re.search(r"Atomic Habits:\s*([^\)]+)\)", content)
        target_m = re.search(r"Measurable target.*?`([^`]+)`.*?`([^`]+)`", content)
        ft_m = re.search(r"Yesterday's prescription\*\*\s*(✓|✗)", content)

        lines.append("▸ TODAY'S PRESCRIPTION")
        if ft_m:
            icon = ft_m.group(1)
            lines.append(f"  Yesterday: {icon}")
        if presc_m:
            lines.append(f"  → {presc_m.group(1).strip()}")
        if law_m:
            lines.append(f"  Law: {law_m.group(1).strip()}")
        if target_m:
            lines.append(f"  Target: {target_m.group(1)} {target_m.group(2)}")
        lines.append("")

    # 2. Open tasks (unchecked only)
    tasks_file = analysis_dir / "tasks.md"
    if tasks_file.exists():
        tasks_content = tasks_file.read_text()
        open_tasks = [
            l.strip() for l in tasks_content.splitlines()
            if re.match(r"[-*]?\s*\[ \]", l) and l.strip()
        ][:5]
        if open_tasks:
            lines.append("▸ OPEN TASKS")
            for t in open_tasks:
                clean = re.sub(r"[-*]?\s*\[ \]\s*", "", t)
                lines.append(f"  · {clean[:72]}")
            lines.append("")

    # 3. Latest weekly focus score
    if weekly_dir.exists():
        weekly_files = sorted(weekly_dir.glob("*.md"), reverse=True)
        if weekly_files:
            wf = weekly_files[0]
            wc = wf.read_text()
            score_m = re.search(r"\*\*Focus Score:\*\*\s*([^\s—]+)", wc)
            pattern_m = re.search(r"## Pattern Detected\s*\n+(.+?)(?:\n|$)", wc)
            one_m = re.search(r"## One Thing\s*\n+(.+?)(?:\n|$)", wc)
            week_label = wf.stem
            lines.append(f"▸ WEEK {week_label}")
            if score_m:
                lines.append(f"  Focus: {score_m.group(1)}")
            if pattern_m:
                lines.append(f"  Pattern: {pattern_m.group(1).strip()[:72]}")
            if one_m:
                lines.append(f"  One thing: {one_m.group(1).strip()[:72]}")
            lines.append("")

    # 4. Behavioral model — top trigger + killer
    model_file = analysis_dir / "behavioral_model.md"
    if model_file.exists():
        mc = model_file.read_text()
        trigger_m = re.search(r"## Output Triggers\s*\n+\*\*([^*]+)\*\*", mc)
        killer_m = re.search(r"## Output Killers\s*\n+\*\*([^*]+)\*\*", mc)
        if trigger_m or killer_m:
            lines.append("▸ YOUR MODEL")
            if trigger_m:
                lines.append(f"  + {trigger_m.group(1).strip()[:72]}")
            if killer_m:
                lines.append(f"  - {killer_m.group(1).strip()[:72]}")
            lines.append("")
    else:
        # Show data accumulation progress
        if daily_dir.exists():
            day_count = len(list(daily_dir.glob("*.md")))
            if day_count > 0:
                lines.append("▸ YOUR MODEL")
                lines.append(f"  Accumulating data: {day_count}/7 days — model unlocks after 7 days")
                lines.append("")

    # 5. Claude usage score (today)
    usage_file = analysis_dir / "claude_usage.md"
    if usage_file.exists():
        uc = usage_file.read_text()
        # Find today's entry
        today_usage = re.search(
            rf"## {today}.*?\n.*?Score:\s*(\d+)/100.*?(\d+) sessions",
            uc, re.DOTALL
        )
        if today_usage:
            lines.append("▸ CLAUDE USAGE TODAY")
            lines.append(f"  Quality: {today_usage.group(1)}/100 · {today_usage.group(2)} sessions")
            lines.append("")

    lines.append(SEP)
    lines.append("  @engram in Claude Code for deeper analysis")
    lines.append("")

    print("\n".join(lines))


def _print_share_card(analysis_dir: Path, weekly_dir: Path, daily_dir: Path) -> None:
    """Generate a shareable weekly summary card (plain text, no ANSI)."""
    import re
    from datetime import date, timedelta

    today = date.today()
    year, week_num, _ = today.isocalendar()

    # Find latest weekly report
    weekly_file = weekly_dir / f"{year}-W{week_num:02d}.md"
    if not weekly_file.exists():
        # Try previous week
        prev = today - timedelta(days=7)
        y2, w2, _ = prev.isocalendar()
        weekly_file = weekly_dir / f"{y2}-W{w2:02d}.md"

    if not weekly_file.exists():
        print("No weekly report yet. Run: python3 mind_sync.py --weekly")
        return

    wc = weekly_file.read_text()

    # Extract fields from frontmatter + body
    fs_m = re.search(r"focus_score:\s*(\d+)/10", wc)
    focus = fs_m.group(1) if fs_m else "?"

    # Total commits: "241 commits" in Focus Score line
    commits_m = re.search(r"(\d{3,})\s+commits", wc)
    total_commits = commits_m.group(1) if commits_m else "?"

    # Active days from frontmatter (days that had any data)
    days_m = re.search(r"days_with_data:\s*(\d+)", wc)
    active_days = days_m.group(1) if days_m else "7"

    # Peak day commit count — look for "N commits" preceded by a month/day name
    peak_m = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+\s+produced\s+(\d+)\s+commits", wc)
    peak_line = ""
    if peak_m:
        peak_month_day = peak_m.group(0).split(" produced")[0].strip()
        peak_count = peak_m.group(2)
        # Look for multiplier near this mention
        mult_m = re.search(r"(\d+)[–-](\d+)x\s+spike|(\d+\.?\d*)x\s+(?:daily|weekly|the)", wc)
        if mult_m:
            mult = mult_m.group(3) or f"{mult_m.group(1)}–{mult_m.group(2)}"
            peak_line = f"Peak: {peak_month_day} = {peak_count} commits ({mult}x avg)"
        else:
            peak_line = f"Peak: {peak_month_day} = {peak_count} commits"

    # Pattern: first sentence of Pattern Detected section
    pattern_m = re.search(r"## Pattern Detected\s*\n+([^\n]+)", wc)
    pattern = pattern_m.group(1).strip() if pattern_m else ""
    # Truncate at sentence boundary if too long
    if len(pattern) > 120:
        cut = pattern.rfind(". ", 0, 120)
        pattern = pattern[:cut + 1] if cut > 40 else pattern[:117] + "..."

    # One Thing section
    one_thing_m = re.search(r"## One Thing\s*\n+([^\n]+)", wc)
    one_thing = one_thing_m.group(1).strip() if one_thing_m else ""
    if len(one_thing) > 110:
        cut = one_thing.rfind(". ", 0, 110)
        one_thing = one_thing[:cut + 1] if cut > 30 else one_thing[:107] + "..."

    # Coaching prescription from coaching_log.md
    coaching_file = analysis_dir / "coaching_log.md"
    prescription = ""
    if coaching_file.exists():
        cc = coaching_file.read_text()
        presc_m = re.search(r"Tomorrow's prescription.*?>\s*(.+?)(?:\n\n|\Z)", cc, re.DOTALL)
        if presc_m:
            p = presc_m.group(1).strip().replace("\n", " ")
            prescription = p if len(p) <= 120 else p[:117] + "..."

    # Build share card
    week_label = f"{year}-W{week_num:02d}"
    lines = [
        f"Week {week_label} · engram behavioral report",
        f"Focus score: {focus}/10 · {total_commits} commits · {active_days}/7 days active",
    ]
    if peak_line:
        lines.append(peak_line)
    if pattern:
        lines.append(f"\nPattern: {pattern}")
    if one_thing:
        lines.append(f"\nOne thing: {one_thing}")
    if prescription:
        lines.append(f"\nCoach says: {prescription}")
    lines += [
        "",
        "Engram watches your work behavior automatically. Zero logging.",
        "Weekly Atomic Habits report. Runs while you sleep.",
        "",
        "→ github.com/lessthanno/engram-agent",
        "  (30s zero-install preview: curl -fsSL .../preview.sh | bash)",
    ]

    print("\n".join(lines))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--synthesize", action="store_true")
    parser.add_argument("--wiki", action="store_true", help="Wiki ingest only")
    parser.add_argument("--lint", action="store_true", help="Wiki health check")
    parser.add_argument("--weekly", action="store_true", help="Generate weekly synthesis")
    parser.add_argument("--model", action="store_true", help="Rebuild personal behavioral model")
    parser.add_argument("--report", action="store_true", help="Print today's coaching summary (fast, no API)")
    parser.add_argument("--share", action="store_true", help="Print shareable weekly card (copy-paste for Discussions/Twitter)")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--force", action="store_true", help="Run even if today already synced")
    args = parser.parse_args()

    bootstrap()

    # Validate config and warn about issues
    cfg.validate_or_warn()

    # --report: fast read-only summary, exits immediately
    if args.report:
        _print_report(ANALYSIS_DIR, WEEKLY_DIR, LOG_DIR)
        return

    # --share: shareable weekly card, exits immediately
    if args.share:
        _print_share_card(ANALYSIS_DIR, WEEKLY_DIR, LOG_DIR)
        return

    full_run = not any([args.collect, args.synthesize, args.wiki, args.lint, args.weekly, args.model, args.push])

    # Skip if already ran today (RunAtLoad guard) unless --force
    daily_log = LOG_DIR / f"{TODAY}.md"
    if full_run and not args.force and daily_log.exists():
        log.info(f"already synced today ({daily_log}), skipping. Use --force to re-run.")
        return

    try:
        if full_run or args.collect:
            raw = collect_all()
        else:
            raw_path = RAW_DIR / f"{TODAY}.json"
            raw = json.loads(raw_path.read_text()) if raw_path.exists() else {}

        if full_run or args.synthesize:
            synthesize(raw)

            # Run skill-based synthesizers
            try:
                from skill_loader import discover, load_function
                for skill in discover():
                    if skill["type"] == "synthesizer":
                        try:
                            fn = load_function(skill)
                            fn(raw, ANALYSIS_DIR)
                            log.info(f"skill synthesizer: {skill['name']} OK")
                        except Exception as e:
                            log.warning(f"skill synthesizer {skill['name']} failed: {e}")
            except Exception:
                pass

        if full_run or args.wiki:
            from synthesizers.wiki import ingest as wiki_ingest
            wiki_ingest(raw, WIKI_DIR)

        if args.lint:
            from synthesizers.wiki import lint_report
            report = lint_report(WIKI_DIR)
            print(report)
            lint_path = WIKI_DIR / "lint-report.md"
            lint_path.write_text(report)
            log.info(f"lint report → {lint_path}")

        # Weekly synthesis (Sunday or --weekly flag)
        if args.weekly or (full_run and date.today().weekday() == 6):
            try:
                from synthesizers.weekly import synthesize_weekly
                from synthesizers.daily import _call_claude_cli
                synthesize_weekly(LOG_DIR, ANALYSIS_DIR, WEEKLY_DIR, _call_claude_cli)
            except Exception as e:
                log.warning(f"weekly synthesis failed: {e}")

        # Personal behavioral model — --model flag or Sunday or --weekly
        if args.model or args.weekly or (full_run and date.today().weekday() == 6):
            try:
                from synthesizers.behavioral_model import build_model, update_model_file
                from synthesizers.daily import _call_claude_cli
                model_content = build_model(LOG_DIR, ANALYSIS_DIR, call_claude_fn=_call_claude_cli)
                if model_content:
                    update_model_file(model_content, ANALYSIS_DIR)
                    log.info("behavioral model → analysis/behavioral_model.md")
            except Exception as e:
                log.warning(f"behavioral model failed: {e}")

        # Claude usage quality coach (heuristic, no API needed)
        if full_run or args.synthesize:
            try:
                from synthesizers.claude_coach import synthesize as usage_coach, update_usage_file
                usage_section = usage_coach(raw, ANALYSIS_DIR)
                if usage_section:
                    update_usage_file(usage_section, ANALYSIS_DIR)
                    log.info("claude usage coach → analysis/claude_usage.md")
            except Exception as e:
                log.warning(f"claude usage coach failed: {e}")

        # Daily behavioral coaching prescription
        if full_run or args.synthesize:
            try:
                from synthesizers.coach import synthesize as coach_syn, update_coaching_file
                from synthesizers.daily import _call_claude_cli
                coach_entry = coach_syn(raw, ANALYSIS_DIR, call_claude_fn=_call_claude_cli)
                if coach_entry:
                    update_coaching_file(coach_entry, ANALYSIS_DIR)
                    log.info("coaching prescription → analysis/coaching_log.md")
            except Exception as e:
                log.warning(f"coach failed: {e}")

        # Bridge insights to Claude auto-memory
        if full_run or args.synthesize:
            try:
                from bridge_memory import bridge
                bridge(ANALYSIS_DIR)
                log.info("bridged insights → Claude auto-memory")
            except Exception as e:
                log.warning(f"bridge failed: {e}")

            # Run skill-based bridges
            try:
                from skill_loader import discover, load_function
                for skill in discover():
                    if skill["type"] == "bridge":
                        try:
                            fn = load_function(skill)
                            fn(ANALYSIS_DIR)
                            log.info(f"skill bridge: {skill['name']} OK")
                        except Exception as e:
                            log.warning(f"skill bridge {skill['name']} failed: {e}")
            except Exception:
                pass

        if full_run or args.push:
            git_push()

        # macOS notification on first successful sync
        first_run_marker = MEMORY_REPO / ".engram-first-run-done"
        if full_run and not first_run_marker.exists():
            try:
                git = raw.get("git_activity", {})
                sessions = raw.get("claude_sessions", {})
                msg = (f"First sync complete! "
                       f"{git.get('total_commits', 0)} commits, "
                       f"{sessions.get('session_count', 0)} sessions collected.")
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{msg}" with title "Engram Agent" sound name "Glass"'
                ], capture_output=True, timeout=5)
                first_run_marker.write_text(datetime.now().isoformat())
            except Exception:
                pass

        log.info(f"done {datetime.now().isoformat()}")

    except Exception as e:
        log.error(f"pipeline failed: {e}", exc_info=True)
        # macOS notification on failure
        try:
            subprocess.run([
                "osascript", "-e",
                f'display notification "Mind Sync failed: {e}" with title "Engram"'
            ], capture_output=True, timeout=5)
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
