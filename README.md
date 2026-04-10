<p align="center">
  <h1 align="center">Engram</h1>
  <p align="center">
    <strong>Your AI coding tools forget everything between sessions.<br>Engram makes them remember.</strong>
  </p>
  <p align="center">
    <a href="#the-problem">The Problem</a> &bull;
    <a href="#quick-start">Quick Start</a> &bull;
    <a href="#how-it-works">How It Works</a> &bull;
    <a href="./README.zh-CN.md">中文文档</a> &bull;
    <a href="https://github.com/lessthanno/engram-agent/issues">Issues</a>
  </p>
</p>

---

## The Problem

Imagine hiring a brilliant assistant who gets amnesia every night.

Every morning, you walk in and they ask: *"Hi, who are you? What are we working on?"* You explain everything again. They do great work. Then they go home, forget it all, and the cycle repeats.

**That's how AI coding tools work today.** Claude Code, Cursor, Codex -- they're incredibly capable, but every session starts from zero. No memory of yesterday's decisions. No awareness of your habits. No continuity.

**Engram gives them a memory.**

It runs quietly in the background, observing what you work on each day. At night, it writes a "briefing" for your AI tools. The next morning, they already know your open tasks, your patterns, even your blind spots.

No cloud. No setup. No maintenance. Just smarter AI, every day.

---

## What Changes

**Without Engram -- every morning:**
```
You:    Fix the payment webhook
Claude: Sure! What framework are you using? What's the current setup?
        (asks 10 questions you answered last week)
```

**With Engram -- every morning:**
```
You:    Fix the payment webhook
Claude: You were working on the Stripe dispute webhook last Friday.
        3 events still need implementation. Your project uses Go + stripe-go SDK.
        Want me to continue where you left off?
```

**It notices things you don't:**
```
[From daily analysis]

You context-switched between 8 projects yesterday.
On days with <3 switches, your output is 2.4x higher.
Suggestion: Block 2 focused hours before opening other projects.
```

**It remembers what you forgot:**
```
You:    Redis connection timeouts again...
Claude: You fixed this exact issue on March 15th. Root cause was pool.MaxIdle
        set too low. The fix was in cmd/server/redis.go line 47.
        Check if someone reverted that change.
```

---

## How It Works

Think of it as a **daily journal that writes itself** -- and your AI reads it every morning.

```
                    You work normally
                          |
                          v
             Engram watches silently
          (git commits, sessions, shell history,
           browser tabs, app usage -- 7 sources)
                          |
                          v
             Every night at 23:45,
          Claude reads all the raw data and
            writes a daily "briefing":
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
| **Git commits** | What code you changed and how fast |
| **Shell history** | What commands you ran (passwords auto-redacted) |
| **Browser tabs** | What you were researching |
| **App usage** | Which apps you spent time in |
| **Recent files** | What documents you touched |
| **System state** | Running processes, active projects |

---

## What It Produces

Every night, Claude analyzes your day and writes:

| Output | Purpose |
|--------|---------|
| **Daily log** | A complete record of what you did today |
| **Open tasks** | Unfinished work extracted from your sessions |
| **Patterns** | Behavioral trends (e.g., "productive in mornings") |
| **Weak spots** | Recurring problems (e.g., "context-switching too much") |
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
> @memory-analyst Have I seen this bug before?
> @memory-analyst What are my open tasks?
> @memory-analyst What patterns am I showing this week?
```

Like talking to a version of yourself that actually takes notes.

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

## License

MIT

---

<p align="center">
  <sub>Built by <a href="https://github.com/lessthanno">@lessthanno</a>.<br>Your AI should learn from you -- not start from scratch every time.</sub>
</p>
