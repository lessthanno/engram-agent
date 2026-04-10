#\!/usr/bin/env bash
# PreCompact hook: save key context before Claude compresses conversation.

set -euo pipefail

MEMORY_REPO="${ENGRAM_MEMORY_REPO:-$HOME/mind-memory}"
COMPACT_DIR="$MEMORY_REPO/raw/compactions"
mkdir -p "$COMPACT_DIR"

python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
except:
    data = {}

out = {
    'hookSpecificOutput': {
        'hookEventName': 'PreCompact',
        'additionalContext': 'Before compacting: preserve any key decisions, architectural choices, and unresolved questions in your summary. These will be synced to your memory repo.'
    }
}
print(json.dumps(out))
"
