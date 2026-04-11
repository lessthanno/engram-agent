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
