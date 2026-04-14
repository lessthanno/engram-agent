#!/usr/bin/env bash
# Engram Preview — zero install, 30 seconds
# Shows what Engram finds about YOUR behavior this week.
# Nothing is installed. No files written. No accounts needed.
#
# curl -fsSL https://raw.githubusercontent.com/lessthanno/engram-agent/main/scripts/preview.sh | bash

set -euo pipefail

# Requires Python 3 (pre-installed on macOS)
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is required. Install from python.org"
    exit 1
fi

python3 - <<'PYEOF'
import subprocess
import os
import sys
from datetime import date, timedelta
from pathlib import Path

BOLD  = "\033[1m"
DIM   = "\033[2m"
GREEN = "\033[0;32m"
YELLOW= "\033[1;33m"
CYAN  = "\033[0;36m"
RESET = "\033[0m"
SEP   = "─" * 54

def p(s=""): print(s)
def pb(s): print(f"{BOLD}{s}{RESET}")
def pd(s): print(f"{DIM}{s}{RESET}")

print()
print(f"{BOLD}engram preview{RESET} {DIM}· scanning your git activity this week...{RESET}")
print()

# ── Week range ────────────────────────────────────────────────────────────────
today = date.today()
monday = today - timedelta(days=today.weekday())
week_days = [monday + timedelta(days=i) for i in range(today.weekday() + 1)]

# ── Git author (this machine's commits only) ─────────────────────────────────
def get_git_author():
    try:
        r = subprocess.run(["git", "config", "--global", "user.email"],
                           capture_output=True, text=True, timeout=3)
        email = r.stdout.strip()
        if email:
            return email
        r2 = subprocess.run(["git", "config", "--global", "user.name"],
                            capture_output=True, text=True, timeout=3)
        return r2.stdout.strip() or None
    except Exception:
        return None

GIT_AUTHOR = get_git_author()

# ── Find repos ────────────────────────────────────────────────────────────────
search_roots = [
    Path.home() / "Documents",
    Path.home() / "Projects",
    Path.home() / "code",
    Path.home() / "dev",
    Path.home() / "src",
    Path.home() / "work",
    Path.home(),
]

repos = set()
for root in search_roots:
    if not root.exists():
        continue
    try:
        result = subprocess.run(
            ["find", str(root), "-maxdepth", "6", "-name", ".git", "-type", "d"],
            capture_output=True, text=True, timeout=12
        )
        for line in result.stdout.splitlines():
            repos.add(str(Path(line).parent))
    except Exception:
        continue

repos = list(repos)[:60]

# ── Count commits per day ────────────────────────────────────────────────────
day_commits = {d.isoformat(): 0 for d in week_days}
repo_totals = {}

for repo in repos:
    repo_count = 0
    for day in week_days:
        day_str = day.isoformat()
        try:
            cmd = ["git", "-C", repo, "log", "--oneline", "--no-merges",
                   f"--since={day_str} 00:00",
                   f"--until={day_str} 23:59:59"]
            if GIT_AUTHOR:
                cmd += [f"--author={GIT_AUTHOR}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
            count = len([l for l in result.stdout.splitlines() if l.strip()])
            day_commits[day_str] += count
            repo_count += count
        except Exception:
            continue
    if repo_count > 0:
        repo_totals[Path(repo).name] = repo_count

# ── Stats ─────────────────────────────────────────────────────────────────────
total = sum(day_commits.values())
active_days = [d for d, c in day_commits.items() if c > 0]
zero_days   = [d for d, c in day_commits.items() if c == 0]
peak_day    = max(day_commits, key=day_commits.get) if day_commits else None
peak_count  = day_commits.get(peak_day, 0) if peak_day else 0
avg = round(total / max(len(active_days), 1), 1)

# ── Output ────────────────────────────────────────────────────────────────────
print(f"{BOLD}╔══ Your Week ({monday} → {today}) ══╗{RESET}")
print()

# Bar chart
print(f"{CYAN}Commits by day:{RESET}")
max_bar = 36
for day in week_days:
    d = day.isoformat()
    c = day_commits[d]
    label = day.strftime("%a %d")
    bar_len = min(round(c / max(peak_count, 1) * max_bar), max_bar) if c > 0 else 0
    bar = "█" * bar_len
    if c == 0:
        print(f"  {DIM}{label}  ·  0{RESET}")
    elif d == peak_day:
        print(f"  {BOLD}{label}  {GREEN}{bar}{RESET}{BOLD}  {c} ← peak{RESET}")
    else:
        print(f"  {label}  {GREEN}{bar}{RESET}  {c}")

print()
print(SEP)
print()

# Summary numbers
print(f"{BOLD}Total:{RESET}       {total} commits")
print(f"{BOLD}Repos:{RESET}       {len(repo_totals)} active")
print(f"{BOLD}Active days:{RESET} {len(active_days)} / {len(week_days)}")
if zero_days:
    print(f"{BOLD}Zero days:{RESET}   {YELLOW}{len(zero_days)}{RESET} — days under your potential")

if peak_count > 0 and avg > 0:
    ratio = round(peak_count / avg, 1)
    print()
    print(f"{BOLD}Peak day:{RESET}    {GREEN}{peak_count} commits{RESET} — {BOLD}{ratio}x your active-day average{RESET}")
    print( "             That's your demonstrated ceiling. How often do you hit it?")

# Repo breakdown
if repo_totals:
    print()
    print(f"{CYAN}Active repos:{RESET}")
    for name, count in sorted(repo_totals.items(), key=lambda x: -x[1])[:5]:
        print(f"  {name}  {DIM}({count} commits){RESET}")

print()
print(SEP)
print()

# Pattern insight
if len(zero_days) >= 3:
    print(f"{YELLOW}Pattern:{RESET} {len(zero_days)} zero days — output concentrated in {len(active_days)} day(s).")
    print( "Engram tracks whether this is a launch hangover, meetings, or something else.")
elif len(repo_totals) >= 5:
    print(f"{YELLOW}Pattern:{RESET} {len(repo_totals)} repos touched — high context-switching.")
    print( "Engram tracks whether single-repo days outperform multi-repo days for you.")
elif peak_count > 0:
    ratio = round(peak_count / max(avg, 1), 1)
    print(f"{YELLOW}Pattern:{RESET} Your peak was {peak_count} commits ({ratio}x average).")
    print( "Engram would track what made that day different — then help you repeat it.")

print()
print(SEP)
print()
print(f"{BOLD}This is ~10% of what Engram sees.{RESET}")
print()
print( "The full system also watches: Claude/Cursor/Codex sessions, app focus time,")
print( "context switches, shell patterns — and generates a weekly Atomic Habits")
print( "report with tomorrow's specific prescription.")
print()
print( "Install (3 questions, 2 min, runs nightly on its own):")
print()
print(f"  {BOLD}curl -fsSL https://raw.githubusercontent.com/lessthanno/engram-agent/main/scripts/quickstart.sh | bash{RESET}")
print()
print(f"  {DIM}github.com/lessthanno/engram-agent{RESET}")
print()
PYEOF
