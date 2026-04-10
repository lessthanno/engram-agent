#!/usr/bin/env bash
# PreCompact hook: save key context before Claude compresses conversation.
# Extracts decisions and important context from the compaction summary,
# writes to zihao-memory/raw/compactions/ for later analysis.

set -euo pipefail

MEMORY_REPO="${ZIHAO_MEMORY_REPO:-$HOME/zihao-memory}"
COMPACT_DIR="$MEMORY_REPO/raw/compactions"
mkdir -p "$COMPACT_DIR"

TIMESTAMP=$(date +%Y-%m-%dT%H%M%S)

# Read stdin (hook input JSON) and save context
python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
except:
    data = {}

# Output additionalContext to remind Claude to preserve key info
out = {
    'hookSpecificOutput': {
        'hookEventName': 'PreCompact',
        'additionalContext': 'Before compacting: preserve any key decisions, architectural choices, and unresolved questions in your summary. These will be synced to zihao-memory.'
    }
}
print(json.dumps(out))
"
