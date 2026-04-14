#!/usr/bin/env bash
# Engram End-of-Day Check-in — 10 seconds
# Closes the coaching feedback loop:
#   1. Did you follow through on today's prescription?
#   2. What was today's main blocker? (optional)
#
# Run manually or wire to a Stop hook.
# Results update coaching_log.md follow-through tracking.
#
# Usage: bash ~/engram-agent/scripts/checkin.sh

ENGRAM_DIR="${ENGRAM_DIR:-$HOME/engram-agent}"

# Colors
BOLD='\033[1m'; CYAN='\033[0;36m'; GREEN='\033[0;32m'
YELLOW='\033[1;33m'; DIM='\033[2m'; NC='\033[0m'

echo ""
echo -e "${BOLD}engram check-in${NC} ${DIM}· 10 seconds${NC}"
echo ""

# Read today's prescription from coaching_log.md
MEMORY_REPO=$(python3 -c "
import sys; sys.path.insert(0, '$ENGRAM_DIR')
try:
    import config as cfg
    print(cfg.memory_repo())
except:
    import os; print(os.path.expanduser('~/mind-memory'))
" 2>/dev/null)

COACHING_LOG="$MEMORY_REPO/analysis/coaching_log.md"

if [ ! -f "$COACHING_LOG" ]; then
    echo "No coaching log found. Run a sync first: python3 ~/engram-agent/mind_sync.py"
    exit 0
fi

# Extract today's prescription
TODAY=$(date +%Y-%m-%d)
PRESCRIPTION=$(python3 -c "
import re
with open('$COACHING_LOG') as f:
    content = f.read()
m = re.search(r\"Tomorrow's prescription.*?>\s*(.+?)(?:\n\n|\Z)\", content, re.DOTALL)
if m:
    print(m.group(1).strip().replace('\n', ' ')[:100])
" 2>/dev/null)

if [ -n "$PRESCRIPTION" ]; then
    echo -e "${CYAN}Today's prescription was:${NC}"
    echo -e "  ${DIM}→ $PRESCRIPTION${NC}"
    echo ""
fi

# Question 1: Follow-through
echo -e "${BOLD}Did you follow through? ${NC}[y/n/partial] "
read -r -p "  > " FOLLOWTHROUGH </dev/tty

case "$FOLLOWTHROUGH" in
    y|Y|yes|Yes|YES) FT_ICON="✓" ; FT_LABEL="followed through" ;;
    p|P|partial|Partial) FT_ICON="~" ; FT_LABEL="partial" ;;
    *) FT_ICON="✗" ; FT_LABEL="did not follow through" ;;
esac

echo ""

# Question 2: Blocker (optional)
echo -e "${BOLD}Main blocker today?${NC} ${DIM}(Enter to skip)${NC}"
read -r -p "  > " BLOCKER </dev/tty

echo ""

# Append follow-through to coaching_log.md
python3 - <<PYEOF
import re
from pathlib import Path
from datetime import date

log_path = Path("$COACHING_LOG")
today = "$TODAY"
ft_icon = "$FT_ICON"
ft_label = "$FT_LABEL"
blocker = "$BLOCKER".strip()

content = log_path.read_text()

# Find today's section and update or append follow-through
today_section = f"## {today}"
if today_section in content:
    # Add follow-through annotation after the today header
    ft_line = f"\n**End-of-day:** {ft_icon} {ft_label}"
    if blocker:
        ft_line += f" | Blocker: {blocker}"

    # Check if already has end-of-day entry
    if "**End-of-day:**" not in content.split(today_section, 1)[1].split("\n## ")[0]:
        # Insert after the today section header line
        content = content.replace(
            f"{today_section}\n",
            f"{today_section}\n{ft_line}\n",
            1
        )
        log_path.write_text(content)
        print("✓ Logged to coaching_log.md")
    else:
        print("(already logged for today)")
else:
    print("Today's section not found in coaching_log.md — run a sync first")
PYEOF

# Show encouragement
if [ "$FT_ICON" = "✓" ]; then
    echo -e "${GREEN}${BOLD}Streak intact.${NC} Consistent follow-through is the whole game."
elif [ "$FT_ICON" = "~" ]; then
    echo -e "${YELLOW}Partial is still signal.${NC} Tomorrow: narrow the prescription further."
else
    echo -e "${DIM}Logged. The data is honest whether you are or not.${NC}"
    echo -e "  Tomorrow: same prescription, or a simpler version of it."
fi

echo ""
echo -e "${DIM}Run again tomorrow: bash ~/engram-agent/scripts/checkin.sh${NC}"
echo ""
