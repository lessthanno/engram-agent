"""
Synthesizer: Daily Analysis
Uses Claude API to turn raw collected data into structured self-analysis.
Produces: daily log, weakness updates, pattern evolution, task extraction.

Supports direct Anthropic API and OpenRouter via ANTHROPIC_BASE_URL.
"""

import json
import logging
import re
import time
from datetime import date, datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

log = logging.getLogger("mind-sync")

TODAY = date.today().isoformat()


def synthesize(raw: dict, analysis_dir: Path, api_key: str = "",
               base_url: str = "https://api.anthropic.com",
               model: str = "claude-sonnet-4-6") -> dict:
    """Main synthesis entry point.
    Tries: claude CLI → CCR local proxy → HTTP API → offline."""
    existing = _load_existing(analysis_dir)
    prompt = _build_prompt(raw, existing)

    # Strategy 1: Use local claude CLI (no API key needed if authenticated)
    response = _call_claude_cli(prompt)

    # Strategy 2: Try Claude Code Router local proxy (localhost:3456)
    if not response:
        response = _call_ccr_proxy(prompt, model)

    # Strategy 3: Fall back to remote HTTP API
    if not response and api_key:
        response = _call_claude_with_retry(prompt, api_key, base_url, model)

    # Strategy 4: Offline
    if not response:
        return _offline_synthesis(raw, existing)

    return _parse_response(response, raw, existing)


def _load_existing(analysis_dir: Path) -> dict:
    files = ["consciousness.md", "weaknesses.md", "patterns.md", "tasks.md", "framework_state.md"]
    existing = {}
    for f in files:
        path = analysis_dir / f
        existing[f] = path.read_text() if path.exists() else ""
    return existing


def _build_prompt(raw: dict, existing: dict) -> str:
    return f"""You are analyzing the user's daily activity data to update their personal memory system.
Be specific, honest, and actionable. Focus on patterns, decisions, and open work.

## Today's raw data ({raw['date']})

### Claude Code Sessions
{_safe_truncate(raw.get('claude_sessions', {}), 2000)}

### Codex (OpenAI) Sessions
{_safe_truncate(raw.get('codex_sessions', {}), 1500)}

### Cursor Sessions
{_safe_truncate(raw.get('cursor_sessions', {}), 1500)}

### Git Activity
{_safe_truncate(raw.get('git_activity', {}), 1500)}

### App Usage
{_safe_truncate(raw.get('app_usage', {}), 1000)}

### Input Habits
{_safe_truncate(raw.get('input_habits', {}), 800)}

### Browser / System
{_safe_truncate(raw.get('system_ops', {}), 800)}

## Existing persistent analysis (for continuity)

### Current consciousness.md (last state)
{existing.get('consciousness.md', 'empty')[:1500]}

### Current weaknesses.md
{existing.get('weaknesses.md', 'empty')[:1000]}

### Current tasks.md
{existing.get('tasks.md', 'empty')[:1000]}

### Current framework_state.md (project development modes)
{existing.get('framework_state.md', 'empty')[:800]}

---

## Framework Reference (apply when analyzing today's activity)

Each active project is in one of these development modes. Detect and update accordingly:

- **quantum mode**: exploring N hypotheses in parallel, no winner yet, measurement criteria not defined
- **atomic mode**: one direction locked, making single-variable changes and observing convergence
- **superposition stall**: stuck between decisions for 2+ days — blocked by missing measurement criteria

Signal → Framework mapping (use these to diagnose observed behavior):
- Task stalled 2+ days → PID integral overload: systemic blocker exists, not just procrastination
- Context window overflow → phase transition warning: approaching cliff, compress or split now
- Multiple options, no decision → Pareto front: identify the one dimension that cannot be compromised
- High output variance for same prompt → Shannon entropy: add output format constraints
- New project/feature → start quantum: list hypotheses + measurement criteria before writing code
- Winner hypothesis identified → switch to atomic: lock direction, one variable at a time
- Architecture decision pending → maximum entropy principle: only add necessary constraints

---

Produce a JSON response with exactly this structure:

{{
  "daily_log": "Full markdown daily log (500-800 words). Include: what was worked on, key decisions made, energy/focus quality, open questions. Write in first person as the user reflecting on their day.",

  "consciousness_update": "Markdown section to ADD to consciousness.md. Capture: new insights, mental model shifts, things that clicked today, things that confused. Be honest about uncertainty. Apply skepticism to any conclusions that feel too obvious.",

  "weaknesses_update": "Markdown section to ADD to weaknesses.md. Identify: what slowed the user down today, repeated mistakes, gaps in knowledge revealed, decision anti-patterns observed. Be specific, not generic.",

  "tasks_update": "Markdown section to REPLACE tasks.md content. Extract from today's data: open questions as actionable tasks, unfinished work, next steps mentioned. Format as: [ ] task (project) [priority: H/M/L]",

  "patterns_update": "Markdown section to ADD to patterns.md. Note: input rhythm patterns, time of day productivity, app switching behavior, coding velocity vs cognitive work ratio.",

  "framework_state": "Markdown table to REPLACE framework_state.md. One row per active project (worked on in last 3 days). Columns: Project | Mode (quantum/atomic/stalled) | Observed Signal | Recommended Next Action. Be specific — name actual tasks and blockers, not generic advice."
}}

Return ONLY valid JSON. No preamble, no markdown fences."""


def _safe_truncate(data: dict, max_chars: int) -> str:
    """Truncate JSON by removing items from lists/dicts to fit within max_chars,
    keeping the JSON structure valid."""
    full = json.dumps(data, ensure_ascii=False, indent=2)
    if len(full) <= max_chars:
        return full

    # Strategy: progressively remove the largest list items
    trimmed = _trim_data(data, max_chars)
    result = json.dumps(trimmed, ensure_ascii=False, indent=2)
    if len(result) <= max_chars:
        return result

    # Final fallback: hard truncate at a safe boundary
    result = result[:max_chars]
    # Find last complete line
    last_newline = result.rfind("\n")
    if last_newline > max_chars * 0.5:
        result = result[:last_newline]
    return result + '\n  "...": "truncated"'


def _trim_data(data, max_chars: int):
    """Recursively trim lists and long strings to fit budget."""
    if isinstance(data, str):
        return data[:max_chars] if len(data) > max_chars else data
    if isinstance(data, list):
        # Keep reducing list until it fits
        result = list(data)
        while len(json.dumps(result, ensure_ascii=False)) > max_chars and len(result) > 1:
            result = result[:len(result) // 2]
        return [_trim_data(item, max_chars // max(len(result), 1)) for item in result]
    if isinstance(data, dict):
        result = {}
        budget_per_key = max_chars // max(len(data), 1)
        for k, v in data.items():
            result[k] = _trim_data(v, budget_per_key)
        return result
    return data


def _call_claude_cli(prompt: str) -> str:
    """Call local claude CLI with --print (non-interactive, stdout only)."""
    import shutil
    import subprocess

    # Try known paths (LaunchAgent may not have full PATH)
    claude_bin = shutil.which("claude")
    if not claude_bin:
        for p in [Path("~/.local/bin/claude").expanduser(),
                  Path("/usr/local/bin/claude")]:
            if p.exists():
                claude_bin = str(p)
                break
    if not claude_bin:
        log.info("claude CLI not found, skipping")
        return ""

    try:
        # --print: output only, no interactive UI
        # Pass prompt via stdin to avoid ARG_MAX limits on large prompts
        result = subprocess.run(
            [claude_bin, "--print", "-p", "-"],
            input=prompt,
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode == 0 and result.stdout.strip():
            log.info("synthesis via claude CLI OK")
            return result.stdout.strip()
        log.warning(f"claude CLI returned {result.returncode}: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        log.warning("claude CLI timed out after 300s")
    except Exception as e:
        log.warning(f"claude CLI failed: {e}")
    return ""


def _call_ccr_proxy(prompt: str, model: str) -> str:
    """Try Claude Code Router local proxy at localhost:3456.
    CCR acts as a local proxy that routes to configured LLM providers."""
    import subprocess as sp

    # Quick check: is CCR running?
    try:
        req = Request("http://localhost:3456/health", method="GET")
        urlopen(req, timeout=2)
    except Exception:
        return ""  # CCR not running, skip silently

    log.info("CCR proxy detected, trying local synthesis")
    url = "http://localhost:3456/v1/messages"
    payload = json.dumps({
        "model": model,
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }

    try:
        req = Request(url, data=payload, headers=headers)
        with urlopen(req, timeout=180) as r:
            data = json.loads(r.read())
        if "error" in data:
            log.warning(f"CCR error: {data['error']}")
            return ""
        text = data["content"][0]["text"]
        log.info("synthesis via CCR proxy OK")
        return text
    except Exception as e:
        log.warning(f"CCR proxy failed: {e}")
        return ""


def _call_claude_with_retry(prompt: str, api_key: str, base_url: str,
                             model: str, max_retries: int = 3) -> str:
    """Call Claude API with exponential backoff retry."""
    url = f"{base_url.rstrip('/')}/v1/messages"

    payload = json.dumps({
        "model": model,
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }

    # Support both direct Anthropic and OpenRouter auth
    if "openrouter" in base_url.lower():
        headers["Authorization"] = f"Bearer {api_key}"
    else:
        headers["x-api-key"] = api_key

    last_error = None
    for attempt in range(max_retries):
        try:
            req = Request(url, data=payload, headers=headers)
            with urlopen(req, timeout=90) as r:
                data = json.loads(r.read())
            if "error" in data:
                raise RuntimeError(f"API error: {data['error']}")
            return data["content"][0]["text"]
        except Exception as e:
            last_error = e
            wait = 2 ** attempt
            log.warning(f"API attempt {attempt + 1}/{max_retries} failed: {e}, retry in {wait}s")
            time.sleep(wait)

    log.error(f"API failed after {max_retries} attempts: {last_error}")
    return ""


def _parse_response(response: str, raw: dict, existing: dict) -> dict:
    if not response:
        return _offline_synthesis(raw, existing)

    clean = response.strip()

    # Try direct JSON parse first
    parsed = None
    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON from markdown fences
    if parsed is None:
        m = re.search(r"```(?:json)?\s*\n(\{.*?\})\s*\n```", clean, re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group(1))
            except json.JSONDecodeError:
                pass

    # Try finding the first { ... } block (handles preamble text before JSON)
    if parsed is None:
        first_brace = clean.find("{")
        last_brace = clean.rfind("}")
        if first_brace != -1 and last_brace > first_brace:
            try:
                parsed = json.loads(clean[first_brace:last_brace + 1])
            except json.JSONDecodeError:
                pass

    if parsed is None:
        log.warning("failed to parse JSON from response, using raw text")
        parsed = {
            "daily_log": response,
            "consciousness_update": "",
            "weaknesses_update": "",
            "tasks_update": "",
            "patterns_update": "",
        }

    date_str = raw.get("date", TODAY)
    header = f"\n## {date_str}\n\n"

    framework_content = parsed.get("framework_state", "")
    if framework_content.strip():
        framework_md = f"# Framework State\n\nLast updated: {date_str}\n\n{framework_content}\n"
    else:
        framework_md = existing.get("framework_state.md", "")

    return {
        "daily_log": _build_daily_log(parsed, raw),
        "analysis_updates": {
            "consciousness.md": _prepend_section(
                existing.get("consciousness.md", ""),
                parsed.get("consciousness_update", ""),
                "Consciousness", header),
            "weaknesses.md": _prepend_section(
                existing.get("weaknesses.md", ""),
                parsed.get("weaknesses_update", ""),
                "Weaknesses", header),
            "tasks.md": parsed.get("tasks_update", ""),
            "patterns.md": _prepend_section(
                existing.get("patterns.md", ""),
                parsed.get("patterns_update", ""),
                "Patterns", header),
            "framework_state.md": framework_md,
        }
    }


def _prepend_section(existing_content: str, new_content: str,
                     title: str, header: str) -> str:
    """Prepend new section to existing file content (newest first).
    Preserves all historical entries."""
    if not new_content.strip():
        return existing_content  # no update, keep as-is

    new_section = f"{header}{new_content}\n\n---\n"

    if not existing_content.strip():
        return f"# {title}\n{new_section}"

    # Insert after the first H1 heading line
    lines = existing_content.split("\n", 1)
    if lines[0].startswith("# "):
        rest = lines[1] if len(lines) > 1 else ""
        return f"{lines[0]}\n{new_section}\n{rest}"

    return f"# {title}\n{new_section}\n{existing_content}"


def _build_daily_log(parsed: dict, raw: dict) -> str:
    date_str = raw.get("date", TODAY)
    git = raw.get("git_activity", {})
    sessions = raw.get("claude_sessions", {})
    app = raw.get("app_usage", {})
    kb = raw.get("input_habits", {}).get("keyboard", {})

    stats = f"""---
date: {date_str}
commits: {git.get('total_commits', 0)}
repos_active: {git.get('repos_active', 0)}
claude_sessions: {sessions.get('session_count', 0)}
focus_score: {app.get('focus_score', 'n/a')}
keystrokes: {kb.get('total_keystrokes', 'n/a')}
---

"""
    return stats + parsed.get("daily_log", "No synthesis available.")


def _offline_synthesis(raw: dict, analysis_dir_or_existing) -> dict:
    """Fallback when no API available. Performs local heuristic analysis."""
    date_str = raw.get("date", TODAY)
    git = raw.get("git_activity", {})
    sessions = raw.get("claude_sessions", {})
    app = raw.get("app_usage", {})
    kb = raw.get("input_habits", {}).get("keyboard", {})
    codex = raw.get("codex_sessions", {})
    cursor = raw.get("cursor_sessions", {})

    commits = git.get("total_commits", 0)
    repos_active = git.get("repos_active", 0)
    messages = git.get("commit_messages", [])
    session_count = sessions.get("session_count", 0)
    codex_count = codex.get("session_count", 0) if isinstance(codex, dict) else 0
    cursor_count = cursor.get("session_count", 0) if isinstance(cursor, dict) else 0
    topics = sessions.get("topics", [])
    top_apps = [a.get("app", "") for a in app.get("top_apps", [])[:8]]
    focus_score = app.get("focus_score", "n/a")

    # -- Local heuristic: categorize commits --
    categories = {"feat": [], "fix": [], "refactor": [], "docs": [], "chore": [], "other": []}
    for msg in messages[:30]:
        lower = msg.lower()
        if any(k in lower for k in ["feat", "add", "implement", "new"]):
            categories["feat"].append(msg)
        elif any(k in lower for k in ["fix", "bug", "patch", "hotfix"]):
            categories["fix"].append(msg)
        elif any(k in lower for k in ["refactor", "rename", "move", "clean"]):
            categories["refactor"].append(msg)
        elif any(k in lower for k in ["doc", "readme", "comment"]):
            categories["docs"].append(msg)
        elif any(k in lower for k in ["chore", "deps", "bump", "ci", "config"]):
            categories["chore"].append(msg)
        else:
            categories["other"].append(msg)

    category_summary = ""
    for cat, msgs in categories.items():
        if msgs:
            category_summary += f"- **{cat}** ({len(msgs)}): {', '.join(msgs[:3])}\n"

    # -- Local heuristic: extract potential tasks from commit messages --
    tasks = []
    for msg in messages[:20]:
        lower = msg.lower()
        if any(k in lower for k in ["wip:", "wip ", "temp:", "hack:", "fixme", "partial:", "todo:"]):
            tasks.append(f"- [ ] Follow up: {msg}")
    for t in topics[:5]:
        if any(k in t.lower() for k in ["debug", "investigate", "fix", "broken"]):
            tasks.append(f"- [ ] Resolve: {t}")

    tasks_section = "\n".join(tasks[:10]) if tasks else "No open tasks detected from today's activity."

    # -- Local heuristic: productivity estimate --
    total_ai_sessions = session_count + codex_count + cursor_count
    if commits >= 10 and total_ai_sessions >= 3:
        productivity = "High output day — heavy coding with AI assistance"
    elif commits >= 5:
        productivity = "Moderate coding output"
    elif total_ai_sessions >= 5 and commits < 3:
        productivity = "Research/exploration heavy — lots of AI sessions, few commits"
    elif commits == 0 and total_ai_sessions == 0:
        productivity = "Light activity or day off"
    else:
        productivity = "Mixed activity"

    log_text = f"""---
date: {date_str}
commits: {commits}
repos_active: {repos_active}
claude_sessions: {session_count}
focus_score: {focus_score}
keystrokes: {kb.get('total_keystrokes', 'n/a')}
mode: offline
---

# {date_str} — Daily Log (offline analysis)

*Synthesized locally without API — heuristic analysis only.*

## Summary
{productivity}. {commits} commits across {repos_active} repos, {total_ai_sessions} AI sessions (Claude: {session_count}, Codex: {codex_count}, Cursor: {cursor_count}).

## Git Activity by Category
{category_summary if category_summary else "No commits today."}

## AI Sessions
Topics discussed: {', '.join(topics[:10]) if topics else 'none detected'}

## App Usage
Top apps: {', '.join(top_apps) if top_apps else 'none detected'}
Focus score: {focus_score}

## Open Items
{tasks_section}
"""

    # Build tasks update if we found any
    tasks_update = ""
    if tasks:
        tasks_update = f"# Open Tasks\n\n## {date_str}\n\n" + "\n".join(tasks[:10])

    return {
        "daily_log": log_text,
        "analysis_updates": {
            "tasks.md": tasks_update,
        } if tasks_update else {}
    }
