# 🐾 Pet Protocol

> Your AI twin lives in your browser.

A pixel cat Chrome extension that reads your actual work memory, generates its own personality, and interacts with your teammates' pets — all in real time.

![demo](website/preview.gif)

## What it does

- **Memory-driven**: Reads your `zihao-mind` memory files + git history → auto-generates the pet's emotional state, message, and contextual quick-replies. No manual config.
- **Multi-pet**: When teammates install the extension and run the same bridge, their cats appear as ghost pets on your page at different heights.
- **AI chat**: Talk to your pet via Claude Code, Codex CLI, or Anthropic API directly. Multi-turn context preserved.
- **Non-intrusive**: Peeks from the right edge. Slides out with a spring animation when you click. Retreats automatically.

## Setup

### 1. Clone

```bash
git clone https://github.com/xiaozihao/pet-protocol
cd pet-protocol
```

### 2. Start pet-bridge

The bridge wraps local CLIs and reads memory files.

```bash
cd bridge
go build -o pet-bridge .
./pet-bridge
# → 🐾 pet-bridge :19099
```

**Endpoints:**
- `POST /claude` — wraps `claude --print`
- `POST /codex` — wraps `codex exec`
- `GET /context` — reads memory → generates pet state via Claude
- `POST /presence/heartbeat` — register peer on page
- `GET /presence/peers` — list teammates on same page
- `GET /health`

### 3. Load the Chrome extension

1. Open `chrome://extensions`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked**
4. Select the `pet-protocol` directory (root, where `manifest.json` lives)

### 4. Configure

Click the extension icon → choose Agent mode → set pet name → **SAVE**.

Your pet appears. Click it to chat.

## Agent modes

| Mode | Requires | Notes |
|------|----------|-------|
| `Claude Code` | `pet-bridge` running | Uses `claude --print` |
| `Codex` | `pet-bridge` running | Uses `codex exec` |
| `API Key` | Anthropic API key | Direct API, no bridge needed |

## Multi-pet (team presence)

When multiple teammates run `pet-bridge` on their machines and are on the same webpage, their pets appear as semi-transparent ghost cats on your page.

For team use over the network:
```bash
# Option A: ngrok (quick)
ngrok http 19099
# Share the ngrok URL — teammates update BRIDGE_URL in src/background.js

# Option B: deploy bridge to a shared server
# The bridge is a single Go binary, no dependencies
```

## Memory integration

By default, the bridge reads from:
```
~/.claude/projects/-Users-xiaozihao-Documents-01-Projects-Work-Code-persion-zihao-mind/memory/
```

To customize for your own memory path, edit `MEMORY_DIR` in `bridge/main.go`.

The bridge reads `MEMORY.md` (index) + up to 3 memory files, then sends them to Claude to generate the pet's current state.

## Cat types

Three pixel art variants selectable in popup:

| Type | Filter |
|------|--------|
| White | Default |
| Black | `brightness(0.25) contrast(2.5)` |
| Orange | `sepia(1) saturate(3) hue-rotate(340deg)` |

Ghost teammates get hue-rotated variants (200°, 280°, 60°, ...) so you can visually distinguish them.

## States

| State | Trigger | Animation |
|-------|---------|-----------|
| `idle` | Default | Slow blink |
| `peek` | Edge peeking | Slow sway |
| `jump` | Sliding out | Fast jump frames |
| `sleep` | Late night / rest | Zzz bubbles |
| `worried` | Deadline / alert memory | Sweat drops |
| `celebrate` | Ship / milestone | Sparkles |
| `hungry` | Lunch time | Drool pixel |

## File structure

```
pet-protocol/
├── manifest.json          # Chrome MV3 manifest
├── src/
│   ├── content.js         # Main pet logic (canvas, chat, presence)
│   ├── content.css        # Minimal reset
│   ├── background.js      # Service worker (agent routing)
│   ├── popup.html         # Settings UI
│   └── popup.js           # Settings logic
├── bridge/
│   └── main.go            # Go HTTP bridge (port 19099)
├── assets/
│   └── icon32.png
└── website/
    └── index.html         # Landing page
```

## Requirements

- Chrome 110+
- Go 1.21+ (for bridge)
- `claude` CLI in PATH (for Claude Code mode)
- `codex` CLI in PATH (for Codex mode)

## License

MIT — do whatever you want with it.

---

Built by [ZIHAO](https://github.com/xiaozihao) · Powered by Claude
