#!/bin/bash
# Engram Agent — Health Check
# Run anytime: bash scripts/verify.sh

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'
BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
err()  { echo -e "  ${RED}✗${NC} $1"; }

echo ""
echo -e "${BOLD}Engram Health Check${NC}"
echo ""

ERRORS=0

# 1. Config
if [ -f "$HOME/.mind/config.toml" ]; then
    ok "Config: ~/.mind/config.toml"
else
    err "Config not found. Run: bash scripts/install.sh"
    ERRORS=$((ERRORS+1))
fi

# 2. Memory repo
MEMORY_REPO=$(python3 -c "
import sys; sys.path.insert(0, '$SCRIPT_DIR')
import config as cfg
print(cfg.memory_repo())
" 2>/dev/null)

if [ -n "$MEMORY_REPO" ] && [ -d "$MEMORY_REPO/.git" ]; then
    DAILY_COUNT=$(ls "$MEMORY_REPO/daily/" 2>/dev/null | wc -l | tr -d ' ')
    ok "Memory repo: $MEMORY_REPO ($DAILY_COUNT daily logs)"
else
    err "Memory repo not found or not a git repo"
    ERRORS=$((ERRORS+1))
fi

# 3. Collectors
COLLECTOR_RESULT=$(cd "$SCRIPT_DIR" && python3 -c "
import sys; sys.path.insert(0, '.')
from datetime import date
names = []
today = date.today().isoformat()

try:
    from collectors.git_activity import collect
    d = collect(today)
    names.append(f'git({d.get(\"total_commits\",0)} commits)')
except: pass

try:
    from collectors.claude_sessions import collect
    d = collect(today)
    s = d.get('session_count', 0)
    names.append(f'claude({s} sessions)')
except: pass

try:
    from collectors.app_usage import collect
    d = collect(today)
    a = len(d.get('top_apps', []))
    names.append(f'apps({a} tracked)')
except: pass

try:
    from collectors.browser_tabs import collect
    d = collect(today)
    t = d.get('tab_count', 0)
    names.append(f'browser({t} tabs)')
except: pass

try:
    from collectors.shell_history import collect
    d = collect(today)
    c = d.get('command_count', 0)
    names.append(f'shell({c} cmds)')
except: pass

try:
    from collectors.recent_files import collect
    d = collect(today)
    f = d.get('file_count', 0)
    names.append(f'files({f})')
except: pass

try:
    from collectors.system_ops import collect
    d = collect(today)
    names.append('system')
except: pass

print(f'{len(names)}|{\"  \".join(names)}')
" 2>/dev/null)

COLLECTOR_COUNT=$(echo "$COLLECTOR_RESULT" | cut -d'|' -f1)
COLLECTOR_DETAIL=$(echo "$COLLECTOR_RESULT" | cut -d'|' -f2)

if [ -n "$COLLECTOR_COUNT" ] && [ "$COLLECTOR_COUNT" -gt 0 ]; then
    ok "Collectors: $COLLECTOR_COUNT active"
    echo "    $COLLECTOR_DETAIL"
else
    err "No collectors working"
    ERRORS=$((ERRORS+1))
fi

# 4. Synthesis engine
if command -v claude &>/dev/null; then
    ok "Synthesis: Claude CLI available"
else
    API_KEY=$(python3 -c "
import sys; sys.path.insert(0, '$SCRIPT_DIR')
import config as cfg
k = cfg.api_key()
print(k[:8] + '...' if k else '')
" 2>/dev/null)
    if [ -n "$API_KEY" ]; then
        ok "Synthesis: API key configured ($API_KEY)"
    else
        warn "Synthesis: no Claude CLI or API key — offline mode only"
    fi
fi

# 5. LaunchAgent
PLIST="$HOME/Library/LaunchAgents/com.engram-agent.plist"
if [ -f "$PLIST" ]; then
    if launchctl list | grep -q "com.engram-agent"; then
        ok "LaunchAgent: loaded (runs at 23:45)"
    else
        warn "LaunchAgent: plist exists but not loaded. Run: launchctl load $PLIST"
    fi
else
    err "LaunchAgent not installed. Run: bash scripts/install.sh"
    ERRORS=$((ERRORS+1))
fi

# 6. Claude Code hooks
SETTINGS="$HOME/.claude/settings.local.json"
if [ -f "$SETTINGS" ]; then
    HAS_HOOKS=$(python3 -c "
import json
d = json.load(open('$SETTINGS'))
h = d.get('hooks', {})
print(len(h))
" 2>/dev/null)
    if [ "$HAS_HOOKS" -gt 0 ]; then
        ok "Claude Code hooks: $HAS_HOOKS configured"
    else
        warn "Claude Code hooks: not configured"
    fi
else
    warn "Claude Code settings: not found"
fi

# 7. Last sync
if [ -d "$MEMORY_REPO/daily" ]; then
    LATEST=$(ls -1t "$MEMORY_REPO/daily/" 2>/dev/null | head -1)
    if [ -n "$LATEST" ]; then
        ok "Last sync: $LATEST"
    else
        echo "  - No daily logs yet (first sync runs tonight at 23:45)"
    fi
fi

# Summary
echo ""
if [ $ERRORS -eq 0 ]; then
    echo -e "  ${GREEN}${BOLD}All systems go.${NC} Engram is healthy."
else
    echo -e "  ${YELLOW}${BOLD}$ERRORS issue(s) found.${NC} See above."
fi
echo ""
