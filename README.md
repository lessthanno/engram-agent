<div align="center">

# Engram

**Your AI tools forget everything every night. Engram fixes that.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://apple.com/macos)
[![Zero deps](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](#requirements)
[![Claude Code](https://img.shields.io/badge/Claude_Code-full_support-orange.svg)](https://claude.ai/code)

*Self-distillation for knowledge workers. Runs automatically every night. Nothing to click.*

[Quick Start](#quick-start) · [How It Works](#how-it-works) · [Skills](#skills----extend-engram) · [Privacy](#privacy----the-non-negotiable) · [中文文档](README.zh-CN.md)

</div>

---

## Before and After

**Without Engram — every single morning:**

```
You:    Help me finish the Q2 report
Claude: Sure! What's the report about? What format do you want?
        What have you done so far? Who's the audience?
```

**With Engram:**

```
You:    Help me finish the Q2 report
Claude: You started this last Thursday. Revenue section is done.
        The churn analysis is incomplete — you noted the data source
        was unreliable. Want me to pull from the updated dashboard?
```

**It notices what you don't:**

```
[Weekly pattern detected]

You context-switched between 8 projects on Tuesday.
On days with ≤3 switches, your output is 2.4x higher.
Your last 3 high-output days all started with 2h of focused work.
```

**It remembers what you forgot:**

```
You:    The deployment keeps failing with that auth error...
Claude: You hit this exact issue on March 15th. Root cause: misconfigured
        env variable. Fix was in deploy.yaml line 47 — check if it was reverted.
```

---

## How Engram Is Different

> *"Isn't this just mem0 / MemGPT / a CLAUDE.md file?"*

No. They solve different problems at different levels of the stack.

### The fundamental difference

Most "AI memory" tools work **inside conversations** — they remember what you *said* to the AI.

Engram works **outside conversations** — it observes what you *did* on your computer.

That's a completely different data layer.

```
mem0 / MemGPT / conversation memory:

  You tell Claude "my name is Alex"
       │
       ▼
  Tool stores: "user's name is Alex"
       │
       ▼
  Next session: Claude knows your name

─────────────────────────────────────────────

Engram:

  You spend 3 hours in VS Code, make 7 commits
  to auth.ts, run the test suite 4 times, then
  open 12 browser tabs about JWT refresh tokens
       │
       ▼
  Engram captures: what you actually did
       │
       ▼
  Claude synthesizes: "You're debugging a JWT
  refresh issue. Tests are still failing. You've
  been on this for 3 hours — likely the token
  expiry logic in auth.ts:142."
```

You didn't tell Claude any of that. Engram inferred it from your behavior.

### Side-by-side comparison

| | Engram | mem0 / MemGPT | CLAUDE.md |
|---|---|---|---|
| **What it captures** | Your actual behavior (git, apps, files, shell, browser) | What you explicitly tell the AI | What you manually write |
| **How it works** | Passive observation, runs overnight | Active: intercepts AI conversations | Static: you write and maintain it |
| **Requires your input?** | No — fully automatic | Yes — you interact with AI normally | Yes — you write and update manually |
| **Data source** | OS-level activity | Conversation content | Your own notes |
| **Finds patterns you didn't notice?** | Yes | No | No |
| **Identifies your weak spots?** | Yes | No | Only if you write them |
| **Works across AI tools?** | Yes — one memory, all tools | Tool-specific | Tool-specific |
| **Local / private?** | 100% local, no cloud | Usually cloud-dependent | Local |
| **Setup** | Install once, never touch again | Requires API integration | Manual ongoing maintenance |

### What they each do well

**Use mem0 / MemGPT if:** you want AI to remember facts you explicitly shared — your name, preferences, project names, instructions you've repeated.

**Use a CLAUDE.md file if:** you want to encode static rules, coding conventions, or project context that doesn't change often.

**Use Engram if:** you want AI to understand *how you actually work* — your rhythms, your recurring mistakes, your unfinished threads, the patterns in your behavior that you can't see yourself.

They solve different problems. Many people use all three.

### The insight Engram is built on

Most tools that call themselves "AI memory" are solving a narrower problem than they appear to be: they're extending the effective context window across sessions, using language as the medium.

Engram adds a new *channel of perception* — one that doesn't go through language at all. Your git history knows things about your work that you would never think to say. Your shell commands reveal priorities you haven't articulated. Your app usage patterns expose habits you haven't noticed.

**The most honest record of how you work isn't what you report — it's what you do.**

---

## How It Works

Think of it as a **daily journal that writes itself** -- and your AI reads it every morning.

```
                    You work normally
                          |
                          v
             Engram watches silently
          (git commits, AI sessions, shell history,
           browser tabs, app usage -- 7 sources)
                          |
                          v
             Every night at 23:45,
          Claude reads all the raw data and
            distills a personal "briefing":
                          |
          +---------------+---------------+
          |               |               |
     What you did    Your patterns   Open tasks
     today           & weak spots    for tomorrow
          |               |               |
          +---------------+---------------+
                          |
                          v
          Next morning, your AI tools
          read the briefing automatically.
          They know you. The loop repeats.
          You get distilled, day by day.
```

**That's it.** No dashboards to check. No notes to write. No buttons to click.

---

## Quick Start

Three commands. Two minutes.

```bash
git clone https://github.com/lessthanno/engram-agent.git ~/engram-agent
cd ~/engram-agent
bash scripts/install.sh
```

The installer asks 3 questions (where to store memory, your email, which folders to scan), then sets up everything automatically.

After install, **you don't need to do anything.** Engram runs on its own.

---

## What It Collects

Engram gathers context from 7 sources -- all local, nothing leaves your machine:

| Source | What it captures |
|--------|-----------------|
| **AI sessions** | What you discussed with Claude / Cursor / Codex |
| **Git activity** | What code you changed and how fast |
| **Shell history** | What commands you ran (passwords auto-redacted) |
| **Browser tabs** | What you were researching |
| **App usage** | Which apps you spent time in |
| **Recent files** | What documents you touched |
| **System state** | Running processes, active projects |

Not a programmer? That's fine -- browser tabs, app usage, recent files, and AI sessions capture your work regardless of what you do.

---

## What It Produces

Every night, Claude analyzes your day and writes:

| Output | Purpose |
|--------|---------|
| **Daily log** | A complete record of what you did today |
| **Open tasks** | Unfinished work extracted from your sessions |
| **Patterns** | Behavioral trends (e.g., "productive in mornings", "research-heavy Wednesdays") |
| **Weak spots** | Recurring problems (e.g., "context-switching too much", "leaving tasks 80% done") |
| **Weekly report** | Trends over the past 7 days |

All stored as plain Markdown files in a local git repo. Human-readable. Version-controlled. Yours.

---

## Supported Tools

| Tool | Status |
|------|--------|
| **Claude Code** | Full support -- reads sessions, writes back context, hooks installed |
| **Codex** | Collects session data, write-back coming soon |
| **Cursor** | Collects session data, write-back coming soon |

Missing tools are skipped gracefully. No errors, no broken setup.

---

## Privacy -- The Non-Negotiable

- **100% local.** Your data never leaves your machine.
- **No cloud.** No accounts. No servers. No subscriptions.
- **No telemetry.** We don't track anything. Not even anonymous usage stats.
- **Passwords scrubbed.** API keys, tokens, and secrets are automatically removed from collected data.
- **You own everything.** Plain files in a git repo. Delete them anytime.

---

## Ask Your Memory

Once Engram is running, you can query your own history from any Claude Code session:

```
> @memory-analyst What was I working on last Tuesday?
> @memory-analyst Have I seen this problem before?
> @memory-analyst What are my open tasks?
> @memory-analyst What patterns am I showing this week?
```

Like talking to a version of yourself that actually takes notes.

---

## Skills -- Extend Engram

Engram has a built-in skill system. Add custom collectors, synthesizers, or bridges without touching core code.

### Create a Skill

Drop a folder into `~/.mind/skills/` with two files:

```
~/.mind/skills/my-collector/
  SKILL.md      # metadata (name, type, description)
  skill.py      # your Python code
```

### SKILL.md Format

```yaml
---
name: notion-collector
description: Collects today's Notion page edits
type: collector          # collector | synthesizer | bridge
entry: skill.py          # optional, defaults to skill.py
function: collect        # optional, defaults based on type
enabled: true            # optional, defaults to true
---
```

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | Yes | -- | Unique skill identifier (alphanumeric + hyphens) |
| `type` | Yes | -- | `collector`, `synthesizer`, or `bridge` |
| `description` | No | -- | What this skill does |
| `entry` | No | `skill.py` | Python file containing the function |
| `function` | No | Based on type | Function name to call (see table below) |
| `enabled` | No | `true` | Can be overridden in `config.toml` |

### Function Signatures

| Type | Default function name | Signature |
|------|----------------------|-----------|
| collector | `collect` | `collect(today: str) -> dict` |
| synthesizer | `synthesize` | `synthesize(raw: dict, analysis_dir: Path)` |
| bridge | `bridge` | `bridge(analysis_dir: Path)` |

- **Collectors** receive an ISO date string (e.g. `"2026-04-10"`) and return a dict of collected data, which is merged into the raw data pipeline.
- **Synthesizers** receive the full raw data dict plus the analysis directory path. They write synthesized files (e.g. `tasks.md`, `patterns.md`) into the directory.
- **Bridges** receive the analysis directory path and push synthesized results to external systems (e.g. Obsidian, Notion).

You can override the default function name with the `function` field in SKILL.md:

```yaml
---
name: my-collector
type: collector
function: my_custom_collect
---
```

### Configuration

Configure per-skill settings in `~/.mind/config.toml`:

```toml
[skills.notion-collector]
api_key = "ntn_xxxxx"
database_ids = ["abc123"]
```

Access config inside your skill:

```python
import config as cfg

skill_cfg = cfg.skill_config("notion-collector")
api_key = skill_cfg.get("api_key", "")
```

Configuration priority (highest to lowest):
1. Environment variables (`MIND_SKILLS_NOTION_COLLECTOR_API_KEY`)
2. `~/.mind/config.toml`
3. Default values in code

#### Global Toggle

Disable all skills at once:

```toml
[skills]
enabled = false
```

Or disable a specific skill via config (overrides SKILL.md):

```toml
[skills.notion-collector]
enabled = false
```

### Error Handling

Skills are fault-tolerant by design. If a skill fails at any stage (discovery, loading, or execution), Engram logs a warning and continues normally. A broken skill will never crash the main pipeline.

### Example Skills

Included in [`examples/skills/`](./examples/skills/):

- **notion-collector** -- collect Notion page edits via API
- **obsidian-bridge** -- write daily insights to Obsidian vault as daily notes

### Auto-Discovery

Skills are auto-discovered at runtime. No registration needed -- just drop a folder into `~/.mind/skills/` and it works.

---

## Requirements

- **macOS** (Linux and Windows support coming)
- **Python 3.10+** (already on your Mac -- no installs needed)
- **Claude CLI** for AI-powered analysis (optional -- works without it, just less smart)

Zero external dependencies. No `pip install`. No `npm`. No Docker. Just Python.

---

## Uninstall

```bash
bash scripts/uninstall.sh
```

Removes everything except your memory repo. Your data is always preserved.

---

## Contributing

The codebase is intentionally simple -- plain Python, no frameworks, no build step.

Areas where help is welcome:
- **Linux / Windows support**
- **More AI tool integrations** (VS Code, JetBrains, Warp)
- **Local dashboard** for browsing your history visually
- **Team mode** for shared (anonymized) pattern insights

---

## FAQ

### How is Engram different from mem0?

mem0 remembers what you told the AI. Engram observes what you *did* -- git commits, shell commands, browser tabs, app usage. Different data layer entirely. Many people use both.

### Does Engram send data to the cloud?

No. Everything runs locally on your machine. No accounts, no servers, no telemetry. Your data never leaves your computer.

### Does it work without Claude?

Yes. Without the Claude CLI, Engram still collects data and stores structured daily logs. Claude adds AI-powered synthesis (pattern detection, task extraction, behavioral insights).

### What does Engram actually produce?

Daily activity logs, open task lists, behavioral pattern analysis, weak spot identification, and weekly trend reports. All stored as plain Markdown in a local git repo.

### Can I use Engram alongside CLAUDE.md?

Yes. CLAUDE.md encodes static rules and conventions. Engram captures dynamic, evolving context about how you work. They complement each other.

### What if I'm not a programmer?

Engram still captures browser tabs, app usage, recent files, and AI sessions -- enough to build a useful daily profile regardless of your work.

---

## License

MIT

---

<p align="center">
  <sub>Built by <a href="https://github.com/lessthanno">@lessthanno</a>.<br>Your AI should learn from you -- not start from scratch every time.</sub>
</p>
