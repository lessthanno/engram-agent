#\!/usr/bin/env bash
# Lightweight hook: collect AI tool session data after each conversation.
# Called by Claude Code Stop hook. Runs async, no blocking.

set -euo pipefail

ENGRAM_DIR="${ENGRAM_DIR:-$HOME/engram-agent}"
export ENGRAM_MEMORY_REPO="${ENGRAM_MEMORY_REPO:-$HOME/mind-memory}"
export ENGRAM_TODAY=$(date +%Y-%m-%d)

mkdir -p "$ENGRAM_MEMORY_REPO/raw"

cd "$ENGRAM_DIR"
python3 -c '
import json, os, sys
from pathlib import Path

today = os.environ["ENGRAM_TODAY"]
raw_dir = Path(os.environ["ENGRAM_MEMORY_REPO"]) / "raw"
raw_path = raw_dir / f"{today}.json"

if raw_path.exists():
    raw = json.loads(raw_path.read_text())
else:
    raw = {"date": today}

claude_projects = Path("~/.claude/projects").expanduser()

collectors = []
try:
    from collectors.claude_sessions import collect as c1
    collectors.append(("claude_sessions", lambda: c1(claude_projects, today)))
except ImportError:
    pass
try:
    from collectors.codex_sessions import collect as c2
    collectors.append(("codex_sessions", lambda: c2(today)))
except ImportError:
    pass
try:
    from collectors.cursor_sessions import collect as c3
    collectors.append(("cursor_sessions", lambda: c3(today)))
except ImportError:
    pass

for name, fn in collectors:
    try:
        raw[name] = fn()
    except Exception as e:
        print(f"{name} failed: {e}", file=sys.stderr)

raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2))
'
