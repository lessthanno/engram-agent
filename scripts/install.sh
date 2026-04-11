#\!/bin/bash
# Engram Agent — Interactive Setup
# Run once: bash scripts/install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
USERNAME=$(whoami)

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
err()  { echo -e "  ${RED}✗${NC} $1"; }
ask()  { echo -en "  ${BLUE}?${NC} $1"; }

echo ""
echo -e "${BOLD}═══════════════════════════════════════════${NC}"
echo -e "${BOLD}  Engram Agent — Self-Distillation Setup   ${NC}"
echo -e "${BOLD}═══════════════════════════════════════════${NC}"
echo ""
echo "  This will set up:"
echo "  1. A private memory repo (git)"
echo "  2. Configuration file (~/.mind/config.toml)"
echo "  3. Claude Code hooks (SessionStart, PreCompact, Stop)"
echo "  4. Claude Code agent (@engram)"
echo "  5. Daily LaunchAgent (23:45 auto-sync)"
echo ""

# ── Step 1: Memory repo ──────────────────────────────────────────────────────
echo -e "${BOLD}[1/7] Memory Repository${NC}"

DEFAULT_MEMORY="$HOME/mind-memory"
ask "Memory repo path [$DEFAULT_MEMORY]: "
read -r MEMORY_REPO
MEMORY_REPO="${MEMORY_REPO:-$DEFAULT_MEMORY}"
MEMORY_REPO=$(eval echo "$MEMORY_REPO")

if [ -d "$MEMORY_REPO/.git" ]; then
    ok "Existing repo found at $MEMORY_REPO"
elif [ -d "$MEMORY_REPO" ]; then
    echo "  Directory exists but is not a git repo. Initializing..."
    git init "$MEMORY_REPO"
    ok "Initialized git repo at $MEMORY_REPO"
else
    echo "  Creating new repo..."
    mkdir -p "$MEMORY_REPO"
    git init "$MEMORY_REPO"
    ok "Created and initialized $MEMORY_REPO"
fi

# Create directory structure
mkdir -p "$MEMORY_REPO"/{daily,weekly,analysis,raw/{claude-sessions,git-activity,app-usage,input-habits},wiki,reports}
for f in consciousness.md weaknesses.md patterns.md tasks.md; do
    if [ \! -f "$MEMORY_REPO/analysis/$f" ]; then
        echo "# ${f%.md}" > "$MEMORY_REPO/analysis/$f"
    fi
done
ok "Directory structure ready"

# ── Step 2: Configuration ────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[2/7] Configuration${NC}"

CONFIG_DIR="$HOME/.mind"
CONFIG_FILE="$CONFIG_DIR/config.toml"
mkdir -p "$CONFIG_DIR"
mkdir -p "$CONFIG_DIR/skills"

if [ -f "$CONFIG_FILE" ]; then
    ok "Config already exists at $CONFIG_FILE"
else
    # Git author email
    DEFAULT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")
    ask "Git author email (to filter your commits) [$DEFAULT_EMAIL]: "
    read -r GIT_EMAIL
    GIT_EMAIL="${GIT_EMAIL:-$DEFAULT_EMAIL}"

    # Scan roots
    DEFAULT_ROOTS='["~/Documents", "~/code", "~/projects", "~/dev"]'
    ask "Git scan roots (JSON array) [$DEFAULT_ROOTS]: "
    read -r SCAN_ROOTS
    SCAN_ROOTS="${SCAN_ROOTS:-$DEFAULT_ROOTS}"

    cat > "$CONFIG_FILE" << EOF
# Engram Agent — Configuration
# Docs: https://github.com/lessthanno/engram-agent

[api]
# Synthesis uses local \`claude\` CLI by default (no key needed).
# Uncomment below as fallback if CLI is unavailable:
# key = "sk-..."
# base_url = "https://api.anthropic.com"
model = "claude-sonnet-4-6"

[paths]
memory_repo = "$MEMORY_REPO"

[git]
author_email = "$GIT_EMAIL"
scan_roots = $SCAN_ROOTS

[privacy]
sensitive_patterns = ["sk-[a-zA-Z0-9]", "token=\\\\S+", "password[=:]\\\\S+", "secret[=:]\\\\S+"]

[skills]
enabled = true
# Per-skill config: [skills.<name>]
# Example:
# [skills.notion-collector]
# api_key = "ntn_xxxxx"
EOF
    ok "Config written to $CONFIG_FILE"
fi

# ── Step 3: Python check ─────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[3/7] Dependencies${NC}"

if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version 2>&1)
    ok "Python: $PY_VERSION"
else
    err "Python 3 not found. Install via: brew install python3"
    exit 1
fi

if command -v claude &>/dev/null; then
    CLAUDE_VERSION=$(claude --version 2>&1 | head -1)
    ok "Claude CLI: $CLAUDE_VERSION"
else
    warn "Claude CLI not found. Synthesis will use HTTP API fallback."
    warn "Install: https://docs.anthropic.com/en/docs/claude-code"
fi

for tool in codex cursor; do
    if command -v $tool &>/dev/null; then
        ok "$tool: detected"
    else
        echo "  - $tool: not installed (optional)"
    fi
done

# ── Step 4: Claude Code hooks ────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[4/7] Claude Code Hooks${NC}"

SETTINGS_LOCAL="$HOME/.claude/settings.local.json"
ENGRAM_SCRIPTS="$SCRIPT_DIR/scripts"

if [ -f "$SETTINGS_LOCAL" ]; then
    if python3 -c "import json; d=json.load(open('$SETTINGS_LOCAL')); assert 'SessionStart' in d.get('hooks',{})" 2>/dev/null; then
        ok "Hooks already configured"
    else
        echo "  Adding hooks to existing settings..."
        python3 << PYEOF
import json
from pathlib import Path

f = Path("$SETTINGS_LOCAL")
cfg = json.loads(f.read_text())

hooks = cfg.setdefault("hooks", {})
hooks["SessionStart"] = [{"hooks": [{"type": "command", "command": "bash $ENGRAM_SCRIPTS/session_context.sh 2>/dev/null || echo '{}'", "timeout": 5, "statusMessage": "Loading memory context..."}]}]
hooks["PreCompact"] = [{"hooks": [{"type": "command", "command": "bash $ENGRAM_SCRIPTS/pre_compact.sh 2>/dev/null || echo '{}'", "timeout": 5, "statusMessage": "Preserving context before compact..."}]}]
hooks["Stop"] = [{"hooks": [{"type": "command", "command": "bash $ENGRAM_SCRIPTS/session_sync.sh 2>/dev/null || true", "timeout": 15, "statusMessage": "Syncing session to memory...", "async": True}]}]

f.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
PYEOF
        ok "Hooks added (SessionStart, PreCompact, Stop)"
    fi
else
    mkdir -p "$HOME/.claude"
    python3 << PYEOF
import json
from pathlib import Path

cfg = {
    "hooks": {
        "SessionStart": [{"hooks": [{"type": "command", "command": "bash $ENGRAM_SCRIPTS/session_context.sh 2>/dev/null || echo '{}'", "timeout": 5, "statusMessage": "Loading memory context..."}]}],
        "PreCompact": [{"hooks": [{"type": "command", "command": "bash $ENGRAM_SCRIPTS/pre_compact.sh 2>/dev/null || echo '{}'", "timeout": 5, "statusMessage": "Preserving context before compact..."}]}],
        "Stop": [{"hooks": [{"type": "command", "command": "bash $ENGRAM_SCRIPTS/session_sync.sh 2>/dev/null || true", "timeout": 15, "statusMessage": "Syncing session to memory...", "async": True}]}]
    }
}
Path("$SETTINGS_LOCAL").write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
PYEOF
    ok "Created $SETTINGS_LOCAL with hooks"
fi

# ── Step 5: Claude Code agent ────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[5/7] Claude Code Agent${NC}"

AGENTS_DIR="$HOME/.claude/agents"
mkdir -p "$AGENTS_DIR"
cp "$SCRIPT_DIR/agents/engram.md" "$AGENTS_DIR/"
ok "@engram agent installed"

# ── Step 6: LaunchAgent ──────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[6/7] LaunchAgent (daily auto-sync at 23:45)${NC}"

PLIST_SRC="$SCRIPT_DIR/scripts/com.engram-agent.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.engram-agent.plist"

mkdir -p "$HOME/Library/LaunchAgents"

sed \
    -e "s|ENGRAM_DIR_PLACEHOLDER|$SCRIPT_DIR|g" \
    -e "s|MEMORY_REPO_PLACEHOLDER|$MEMORY_REPO|g" \
    -e "s|HOME_PLACEHOLDER|$HOME|g" \
    "$PLIST_SRC" > "$PLIST_DST"

# Unload old plist if exists
launchctl unload "$HOME/Library/LaunchAgents/com.mind-sync.plist" 2>/dev/null || true
launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load "$PLIST_DST"
ok "LaunchAgent loaded (daily at 23:45)"

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}═══════════════════════════════════════════${NC}"
echo -e "${BOLD}  Setup complete\!${NC}"
echo -e "${BOLD}═══════════════════════════════════════════${NC}"
echo ""
echo "  Test it now:"
echo -e "    ${BLUE}cd $SCRIPT_DIR && python3 mind_sync.py --force${NC}"
echo ""
echo "  Check logs:"
echo -e "    ${BLUE}tail -f /tmp/engram-agent.log${NC}"
echo ""
echo "  Your memory repo:"
echo -e "    ${BLUE}$MEMORY_REPO${NC}"
echo ""
echo "  Skills directory:"
echo -e "    ${BLUE}~/.mind/skills/${NC}"
echo ""
echo "  To push to GitHub (optional):"
echo -e "    ${BLUE}cd $MEMORY_REPO${NC}"
echo -e "    ${BLUE}gh repo create mind-memory --private --source=. --push${NC}"
echo ""
echo "  Restart Claude Code to activate the @engram agent."
echo ""

# ── Step 7: Post-install verification ────────────────────────────────────────
echo ""
echo -e "${BOLD}[7/7] Verification${NC}"

echo "  Running quick pipeline test..."
VERIFY_OUTPUT=$(cd "$SCRIPT_DIR" && python3 -c "
import json, sys
sys.path.insert(0, '.')
import config as cfg

errors = []

# 1. Config loads
try:
    repo = cfg.memory_repo()
    if not repo.exists():
        errors.append(f'Memory repo not found: {repo}')
    else:
        print(f'  memory_repo: {repo}')
except Exception as e:
    errors.append(f'Config error: {e}')

# 2. Check directory structure
from pathlib import Path
required = ['daily', 'analysis', 'raw']
for d in required:
    p = repo / d
    if p.exists():
        print(f'  {d}/: OK')
    else:
        errors.append(f'Missing directory: {d}/')

# 3. Try importing collectors
collector_names = []
try:
    from collectors.git_activity import collect as c2
    collector_names.append('git')
except: errors.append('git collector import failed')
try:
    from collectors.claude_sessions import collect as c1
    collector_names.append('claude')
except: errors.append('claude collector import failed')
try:
    from collectors.app_usage import collect as c3
    collector_names.append('app_usage')
except: errors.append('app_usage collector import failed')
try:
    from collectors.system_ops import collect as c5
    collector_names.append('system')
except: errors.append('system collector import failed')
print(f'  collectors: {len(collector_names)} loaded ({', '.join(collector_names)})')

# 4. Quick git data test
from datetime import date
today = date.today().isoformat()
try:
    git_data = c2(today)
    commits = git_data.get('total_commits', 0)
    repos = git_data.get('repos_active', 0)
    print(f'  git scan: {commits} commits today, {repos} repos active')
except Exception as e:
    errors.append(f'git scan failed: {e}')

# 5. Check Claude CLI
import shutil
claude_bin = shutil.which('claude')
if claude_bin:
    print(f'  claude CLI: {claude_bin}')
else:
    print('  claude CLI: not found (will use API fallback)')

# 6. Check API key
key = cfg.api_key()
if key:
    print(f'  API key: configured ({key[:8]}...)')
elif claude_bin:
    print('  API key: not set (using claude CLI)')
else:
    print('  API key: not set (offline mode — synthesis will be limited)')

if errors:
    print()
    for e in errors:
        print(f'  ERROR: {e}')
    sys.exit(1)
else:
    print()
    print('  All checks passed.')
" 2>&1)

echo "$VERIFY_OUTPUT"

if [ $? -eq 0 ]; then
    ok "Verification passed"
else
    warn "Some checks failed (see above). Engram will still work with reduced functionality."
fi

# ── Generate uninstall script ────────────────────────────────────────────────
cat > "$SCRIPT_DIR/scripts/uninstall.sh" << UNINSTALL
#\!/bin/bash
# Engram Agent — Uninstall
launchctl unload "$PLIST_DST" 2>/dev/null
rm -f "$PLIST_DST"
rm -f "$AGENTS_DIR/engram.md"
rm -f "$AGENTS_DIR/memory-analyst.md"  # cleanup legacy name
echo "Uninstalled. Your memory repo at $MEMORY_REPO is preserved."
echo "To remove hooks, edit $SETTINGS_LOCAL and delete the hooks section."
UNINSTALL
chmod +x "$SCRIPT_DIR/scripts/uninstall.sh"
