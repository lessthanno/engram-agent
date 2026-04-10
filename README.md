<p align="center">
  <h1 align="center">Engram</h1>
  <p align="center">
    <strong>Your AI coding tools forget everything between sessions.<br>Engram makes them remember.</strong>
  </p>
  <p align="center">
    <a href="#quick-start">Quick Start</a> &bull;
    <a href="#how-it-works">How It Works</a> &bull;
    <a href="#supported-tools">Supported Tools</a> &bull;
    <a href="https://github.com/lessthanno/engram-agent/issues">Issues</a>
  </p>
</p>

---

Every time you start a new Claude Code / Cursor / Codex session, your AI assistant starts from zero. It doesn't know what you worked on yesterday, what decisions you made, or what patterns you're repeating.

**Engram fixes this.** It automatically collects your dev activity, synthesizes daily self-analysis with Claude, and writes insights back into `~/.claude/`, `~/.codex/`, and `~/.cursor/`. Your AI tools wake up smarter every morning. Self-distillation for developers.

- **Zero effort** -- hooks + LaunchAgent, fully automatic
- **Zero cloud** -- all data stays on your machine
- **Zero deps** -- Python stdlib only, no pip install needed
- **Cross-tool** -- Claude Code, Codex, Cursor, Claude Code Router

## What It Feels Like

**Monday morning, without Engram:**
```
You: Fix the payment webhook handler
Claude: Sure, what framework are you using? What's the current implementation?
        (starts from zero, asks 10 questions you answered last week)
```

**Monday morning, with Engram:**
```
[SessionStart hook injects context]

You: Fix the payment webhook handler
Claude: Based on your session history, you were working on the Stripe dispute
        webhook last Friday. 3 events still need implementation:
        charge.dispute.funds_withdrawn, funds_reinstated, and
        radar.early_fraud_warning.created. Your FujiPay project uses Go + the
        stripe-go SDK. Want me to continue from where you left off?
```

**Your AI notices patterns you don't:**
```
[From daily analysis]

Weakness detected: You context-switched between 8 projects yesterday.
On days with <3 switches, your commit output is 2.4x higher.
Recommendation: Block 2 hours for FujiPay webhook before opening other projects.
```

**Your AI remembers what you forgot:**
```
You: I'm seeing Redis connection timeouts again
Claude: You debugged this exact issue on March 15th. Root cause was pool.MaxIdle
        set to 10 (too low for your connection volume). The fix was in
        cmd/server/redis.go:47. Check if someone reverted that change.
```

## Quick Start

```bash
git clone https://github.com/lessthanno/engram.git ~/engram
bash ~/engram/scripts/install.sh
```

The interactive installer asks 3 questions (memory repo path, git email, scan roots), then sets up everything:

- Private memory repo with daily/weekly/analysis structure
- Config at `~/.mind/config.toml`
- Claude Code hooks (SessionStart, PreCompact, Stop)
- `memory-analyst` agent for querying your history
- LaunchAgent for daily auto-sync at 23:45

## How It Works

```
 You start a new Claude Code session
        |
        v
 +----------------------------------+
 |  SessionStart Hook               |  Injects yesterday's tasks +
 |  "Loading memory context..."     |  last session summary into context
 +----------------------------------+
        |
        v
   You work normally. Claude Code / Cursor / Codex.
        |
        v
 +----------------------------------+
 |  Stop Hook (async)               |  Captures session data:
 |  "Syncing session to memory..."  |  decisions, topics, files touched
 +----------------------------------+
        |
        v
 +----------------------------------+
 |  Daily Sync (23:45 LaunchAgent)  |
 |                                  |
 |  Collect --> 7 collectors run    |
 |  Synthesize --> Claude analyzes  |
 |  Bridge --> writes back to       |
 |    ~/.claude/memory/             |
 |    ~/.codex/                     |
 |    ~/.cursor/                    |
 |  Git commit --> version history  |
 +----------------------------------+
        |
        v
  Next morning: your AI tools know what you did.
  They see your open tasks, patterns, and weak spots.
  The loop repeats. They get smarter every day.
```

## The Feedback Loop

This is what makes Engram different from static memory tools:

```
              +---------------------+
              |   Your AI Sessions  |
              |  Claude / Codex /   |
              |     Cursor          |
              +---------+-----------+
                        | sessions, decisions
                        v
              +---------------------+
              |     Collectors      |
              |  7 data sources     |
              +---------+-----------+
                        | raw JSON
                        v
              +---------------------+
              |    Synthesizer      |
              |  Claude AI analysis |
              +---------+-----------+
                        | daily log + analysis
                        v
              +---------------------+
              |      Bridge         |--> ~/.claude/memory/
              |  Write insights     |--> ~/.codex/
              |  back to tools      |--> ~/.cursor/
              +---------+-----------+
                        |
                        v
              Your AI tools are now smarter.
              Loop repeats tomorrow.
```

## Supported Tools

| Tool | Collection | Write-back | Hooks |
|------|-----------|------------|-------|
| **Claude Code** | Session transcripts, decisions, topics | Auto-memory bridge | SessionStart, PreCompact, Stop |
| **Codex (OpenAI)** | History, archived rollouts | Planned | -- |
| **Cursor** | Agent transcripts | Planned | -- |
| **Claude Code Router** | Synthesis via local proxy | -- | -- |

Missing a tool? Collectors auto-detect what's installed. Missing tools are skipped gracefully.

## What Gets Collected

| Collector | Source | Data |
|-----------|--------|------|
| `claude_sessions` | `~/.claude/projects/*.jsonl` | Decisions, topics, files, open questions |
| `codex_sessions` | `~/.codex/history.jsonl` + `archived_sessions/` | Prompts, rollout sessions |
| `cursor_sessions` | `~/.cursor/projects/*/agent-transcripts/` | Agent transcripts, files |
| `git_activity` | Local git repos | Commits, velocity, changed files |
| `app_usage` | ActivityWatch / macOS | App time, focus score |
| `input_habits` | ActivityWatch + shell history | Top tools, command patterns |
| `system_ops` | macOS | Recent files, browser tabs, processes |

## What Gets Synthesized

Every night, Claude analyzes your raw data and produces:

| File | Purpose | Update Mode |
|------|---------|-------------|
| `daily/YYYY-MM-DD.md` | Full day log with stats | New file each day |
| `analysis/consciousness.md` | Insights, mental model shifts | Prepend (newest first) |
| `analysis/weaknesses.md` | Recurring problems, anti-patterns | Prepend |
| `analysis/patterns.md` | Behavioral and work patterns | Prepend |
| `analysis/tasks.md` | Open tasks extracted from sessions | Replace (current state) |
| `weekly/YYYY-WNN.md` | Weekly trend report | Sunday |

## Claude Code Agent: memory-analyst

Query your personal memory repo from any Claude Code session:

```
> @memory-analyst What patterns am I showing this week?
> @memory-analyst Have I dealt with this auth issue before?
> @memory-analyst What are my current open tasks?
> @memory-analyst What did I work on last Tuesday?
```

## Configuration

```toml
# ~/.mind/config.toml

[api]
model = "claude-sonnet-4-6"
# key = "sk-..."          # only if claude CLI unavailable
# base_url = "https://openrouter.ai/api"

[paths]
memory_repo = "~/mind-memory"

[git]
author_email = "you@email.com"
scan_roots = ["~/code", "~/projects"]

[privacy]
# Regex patterns -- matching shell commands will be redacted
sensitive_patterns = ["sk-[a-zA-Z0-9]", "token=\\S+", "password[=:]\\S+"]
```

## Synthesis Priority

Engram tries multiple strategies to synthesize your data:

1. `claude --print` CLI (uses your existing OAuth auth)
2. Claude Code Router local proxy (`localhost:3456`)
3. HTTP API (Anthropic / OpenRouter, if key configured)
4. Offline mode (raw data log, no AI analysis)

## Privacy

- **100% local.** No data leaves your machine unless you choose to push to GitHub.
- **Sensitive data redacted.** API keys, tokens, passwords are scrubbed from shell history.
- **Private by default.** Memory repo is local git. Push to a private GitHub repo for backup.
- **No telemetry.** No analytics. No phone home. Ever.

## CLI

```bash
python3 mind_sync.py              # full daily sync
python3 mind_sync.py --collect    # collect only
python3 mind_sync.py --synthesize # synthesize only
python3 mind_sync.py --weekly     # weekly report
python3 mind_sync.py --push       # git push
python3 mind_sync.py --force      # re-run today
```

## Uninstall

```bash
bash scripts/uninstall.sh
```

Removes LaunchAgent and Claude Code agent. Your memory repo is preserved.

## Requirements

- macOS (LaunchAgent, AppleScript fallbacks)
- Python 3.10+ (stdlib only, no pip packages)
- `claude` CLI for AI synthesis (optional)
- [ActivityWatch](https://activitywatch.net) for detailed tracking (optional)

## Contributing

Issues and PRs welcome. The codebase is intentionally simple -- Python stdlib only, no frameworks, no build step.

Key areas for contribution:
- **Linux support** -- systemd timer, replace AppleScript
- **Windows support** -- Task Scheduler, replace AppleScript
- **Codex/Cursor write-back** -- bridge insights into their config systems
- **New collectors** -- VS Code sessions, Warp terminal, JetBrains, etc.
- **Dashboard** -- local web UI for trends over time
- **Team mode** -- anonymized pattern sharing across a team

## License

MIT

---

<p align="center">
  <sub>Built by <a href="https://github.com/lessthanno">@lessthanno</a>.<br>Your AI tools should learn from you, not start from scratch every time.</sub>
</p>
