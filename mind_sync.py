#!/usr/bin/env python3
"""
Engram Agent — Daily memory, activity, and self-analysis system.
Runs daily via LaunchAgent. Collects → Analyzes → Synthesizes → Pushes to GitHub.

Usage:
  python mind_sync.py              # full daily sync
  python mind_sync.py --collect    # collect only
  python mind_sync.py --synthesize # synthesize only (uses last collected data)
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

    raw = {"date": TODAY}
    collectors = [
        ("claude_sessions", lambda: c1(CLAUDE_PROJECTS, TODAY)),
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

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--synthesize", action="store_true")
    parser.add_argument("--wiki", action="store_true", help="Wiki ingest only")
    parser.add_argument("--lint", action="store_true", help="Wiki health check")
    parser.add_argument("--weekly", action="store_true", help="Generate weekly synthesis")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--force", action="store_true", help="Run even if today already synced")
    args = parser.parse_args()

    bootstrap()

    # Validate config and warn about issues
    cfg.validate_or_warn()

    full_run = not any([args.collect, args.synthesize, args.wiki, args.lint, args.weekly, args.push])

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
