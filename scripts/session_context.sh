#!/usr/bin/env bash
# SessionStart hook: inject behavioral context into every new Claude session.
# Reads: today's coaching prescription + open tasks + latest daily log.
# Must be synchronous (Claude waits for this before starting the session).

set -euo pipefail

MEMORY_REPO="${ENGRAM_MEMORY_REPO:-$HOME/mind-memory}"
MAX_CHARS=1000

context=""

# 1. Today's coaching prescription — shown first, highest priority
COACHING_FILE="$MEMORY_REPO/analysis/coaching_log.md"
if [ -f "$COACHING_FILE" ]; then
    # Extract latest prescription block (between first ## and second ##)
    prescription=$(awk '
        /^## [0-9]{4}-[0-9]{2}-[0-9]{2}/{
            if (found) exit
            found=1; next
        }
        found { print }
    ' "$COACHING_FILE" | head -12 | tr '\n' ' ' | sed "s/  */ /g")

    if [ -n "${prescription:-}" ]; then
        context="[Today's Coaching Prescription] $prescription"
    fi
fi

# 2. Open tasks (most actionable)
TASKS_FILE="$MEMORY_REPO/analysis/tasks.md"
if [ -f "$TASKS_FILE" ]; then
    tasks=$(grep -E "^\[ \]|^- \[ \]" "$TASKS_FILE" 2>/dev/null | head -5 | tr '\n' ' ' | cut -c1-250)
    if [ -n "${tasks:-}" ]; then
        context="$context [Open Tasks] $tasks"
    fi
fi

# 3. Latest daily log — most recent context (skip frontmatter)
LATEST_DAILY=$(ls -t "$MEMORY_REPO/daily/"*.md 2>/dev/null | head -1)
if [ -n "${LATEST_DAILY:-}" ] && [ -f "$LATEST_DAILY" ]; then
    daily_date=$(basename "$LATEST_DAILY" .md)
    daily_summary=$(awk 'NR>3 && /[A-Za-z]/{print; count++} count>=8{exit}' "$LATEST_DAILY" \
        | tr '\n' ' ' | cut -c1-300)
    if [ -n "${daily_summary:-}" ]; then
        context="$context [Last Sync ($daily_date)] $daily_summary"
    fi
fi

# 4. Trim to budget
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
        'additionalContext': '[engram] ' + ctx
    }
}
print(json.dumps(out))
" <<< "$context"
