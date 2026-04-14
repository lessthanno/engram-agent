#!/bin/bash
# Engram Agent — One-line quickstart
# curl -fsSL https://raw.githubusercontent.com/lessthanno/engram-agent/main/scripts/quickstart.sh | bash

set -e

INSTALL_DIR="$HOME/engram-agent"

echo ""
echo "Installing Engram Agent..."
echo ""

if [ -d "$INSTALL_DIR" ]; then
    echo "Updating existing installation at $INSTALL_DIR..."
    cd "$INSTALL_DIR"
    git pull --quiet
else
    git clone --quiet https://github.com/lessthanno/engram-agent.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

bash scripts/install.sh

echo ""
echo "─────────────────────────────────────────────"
echo "  Running your first behavioral snapshot..."
echo "─────────────────────────────────────────────"
echo ""

cd "$INSTALL_DIR"
python3 mind_sync.py --collect --force 2>/dev/null && {
    echo ""
    echo "  Data collected. Generating weekly report..."
    echo ""
    python3 mind_sync.py --weekly 2>/dev/null && echo "  Done! Check your memory repo for the weekly report." || {
        echo "  (Synthesis skipped — Claude CLI not found)"
        echo "  Install Claude Code to enable AI analysis:"
        echo "  https://claude.ai/code"
    }
} || {
    echo "  Could not collect data. Try running manually:"
    echo "  cd ~/engram-agent && python3 mind_sync.py --force"
}

echo ""
echo "─────────────────────────────────────────────"
echo "  Next: open Claude Code and type @engram"
echo "─────────────────────────────────────────────"
echo ""
