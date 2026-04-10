#\!/usr/bin/env bash
# SessionStart hook: inject recent memory context into new Claude conversations.
# Reads tasks.md + latest daily log, outputs hookSpecificOutput JSON.
# Must be synchronous (Claude waits for this before starting).

set -euo pipefail

MEMORY_REPO="${ENGRAM_MEMORY_REPO:-$HOME/mind-memory}"
MAX_CHARS=800

context=""

# 1. Current open tasks (most actionable)
TASKS_FILE="$MEMORY_REPO/analysis/tasks.md"
if [ -f "$TASKS_FILE" ]; then
    tasks=$(head -20 "$TASKS_FILE" | tr '\n' ' ' | cut -c1-300)
    if [ -n "$tasks" ]; then
        context="[Open Tasks] $tasks"
    fi
fi

# 2. Latest daily log summary (what happened recently)
LATEST_DAILY=$(ls -t "$MEMORY_REPO/daily/"*.md 2>/dev/null | head -1)
if [ -n "${LATEST_DAILY:-}" ] && [ -f "$LATEST_DAILY" ]; then
    daily_date=$(basename "$LATEST_DAILY" .md)
    daily_summary=$(awk 'BEGIN{c=0} /^---$/{c++;next} c==0 && NR>5{print; next} c>=2{print}' "$LATEST_DAILY" | head -15 | tr '\n' ' ' | cut -c1-400)
    if [ -n "$daily_summary" ]; then
        context="$context [Last Session ($daily_date)] $daily_summary"
    fi
fi

# 3. Trim to budget
context=$(echo "$context" | cut -c1-$MAX_CHARS)

if [ -z "$context" ]; then
    echo '{}'
    exit 0
fi

# Output hook JSON
python3 -c "
import json, sys
ctx = sys.stdin.read().strip()
out = {
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': f'[engram-agent memory] {ctx}'
    }
}
print(json.dumps(out))
" <<< "$context"
