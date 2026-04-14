#!/usr/bin/env bash
# Engram uninstaller
# Removes hooks and LaunchAgent. Your memory repo is preserved.
#
# Usage: bash scripts/uninstall.sh

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
info() { echo -e "  ${YELLOW}·${NC} $1"; }
err()  { echo -e "  ${RED}✗${NC} $1"; }

echo ""
echo -e "${BOLD}Engram Uninstall${NC}"
echo ""

ENGRAM_DIR="${ENGRAM_DIR:-$HOME/engram-agent}"
CLAUDE_HOOKS="$HOME/.claude/settings.json"
LAUNCH_AGENT="$HOME/Library/LaunchAgents/com.engram-agent.plist"

# 1. Remove LaunchAgent
if [ -f "$LAUNCH_AGENT" ]; then
    launchctl unload "$LAUNCH_AGENT" 2>/dev/null || true
    rm -f "$LAUNCH_AGENT"
    ok "LaunchAgent removed"
else
    info "LaunchAgent not found (already removed)"
fi

# 2. Remove Claude Code hooks
if [ -f "$CLAUDE_HOOKS" ]; then
    python3 - <<PYEOF
import json, sys
path = "$CLAUDE_HOOKS"
try:
    with open(path) as f:
        cfg = json.load(f)
except Exception:
    sys.exit(0)

hooks = cfg.get("hooks", {})
changed = False

# Remove engram hooks from each hook type
for hook_type in list(hooks.keys()):
    if isinstance(hooks[hook_type], list):
        before = len(hooks[hook_type])
        hooks[hook_type] = [
            h for h in hooks[hook_type]
            if "engram" not in str(h).lower() and "mind_sync" not in str(h).lower()
        ]
        if len(hooks[hook_type]) < before:
            changed = True
        if not hooks[hook_type]:
            del hooks[hook_type]
            changed = True

if changed:
    cfg["hooks"] = hooks
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)
    print("  hooks cleaned")
PYEOF
    ok "Claude Code hooks removed"
else
    info "No Claude settings file found"
fi

# 3. Remove @engram agent
AGENT_FILE="$HOME/.claude/agents/engram.md"
if [ -f "$AGENT_FILE" ]; then
    rm -f "$AGENT_FILE"
    ok "@engram agent removed"
else
    info "@engram agent not found"
fi

echo ""
echo -e "${BOLD}Done.${NC}"
echo ""
echo "  Your memory repo is preserved at: $(python3 -c "
import os, configparser
cfg = configparser.ConfigParser()
cfg_file = os.path.expanduser('$ENGRAM_DIR/config.ini')
if os.path.exists(cfg_file):
    cfg.read(cfg_file)
    print(cfg.get('paths','memory_repo','~/mind-memory'))
else:
    print('~/mind-memory')
" 2>/dev/null || echo '~/mind-memory')"
echo ""
echo "  To fully remove everything:"
echo "    rm -rf $ENGRAM_DIR"
echo "    rm -rf ~/mind-memory   # or your configured memory repo"
echo ""
