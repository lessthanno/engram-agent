"""
Bridge: engram-memory → Claude auto-memory
Syncs key insights from engram-memory/analysis/ into ~/.claude/projects/ memory.
Runs after daily synthesis to keep Claude's auto-memory aware of patterns.
"""

import logging
import os
import re
from datetime import date
from pathlib import Path

log = logging.getLogger("mind-sync")


def _find_claude_memory_dir() -> Path:
    """Find the Claude auto-memory directory for the current user's home dir."""
    # Claude Code stores project memory at ~/.claude/projects/-<sanitized-cwd>/memory/
    # For the home directory, cwd is sanitized as: -Users-<username>
    home = Path.home()
    sanitized = str(home).replace("/", "-")  # /Users/foo -> -Users-foo
    return Path("~/.claude/projects").expanduser() / sanitized / "memory"


CLAUDE_MEMORY_DIR = _find_claude_memory_dir()
MEMORY_INDEX = CLAUDE_MEMORY_DIR / "MEMORY.md"
TODAY = date.today().isoformat()


def bridge(analysis_dir: Path):
    """Sync top insights from engram-memory into Claude auto-memory."""
    if not CLAUDE_MEMORY_DIR.exists():
        log.info(f"bridge: Claude memory dir not found at {CLAUDE_MEMORY_DIR}, skipping")
        return

    log.info(f"bridge: syncing {analysis_dir} → {CLAUDE_MEMORY_DIR}")
    synced = []
    errors = []

    try:
        if _sync_tasks(analysis_dir / "tasks.md"):
            synced.append("tasks")
    except Exception as e:
        errors.append(f"tasks: {e}")
        log.warning(f"bridge: failed to sync tasks: {e}")

    try:
        if _sync_patterns(analysis_dir / "patterns.md"):
            synced.append("patterns")
    except Exception as e:
        errors.append(f"patterns: {e}")
        log.warning(f"bridge: failed to sync patterns: {e}")

    if synced:
        log.info(f"bridge: synced [{', '.join(synced)}] to Claude auto-memory")
    if errors:
        log.warning(f"bridge: {len(errors)} sync errors: {'; '.join(errors)}")
    if not synced and not errors:
        log.info("bridge: no new data to sync (source files empty or unchanged)")


def _sync_tasks(tasks_file: Path) -> bool:
    """Write current open tasks as a project memory. Returns True if synced."""
    if not tasks_file.exists():
        log.debug(f"bridge: {tasks_file} does not exist, skipping tasks")
        return False
    content = tasks_file.read_text().strip()
    if not content or len(content) < 20:
        log.debug(f"bridge: {tasks_file} too short ({len(content)} chars), skipping")
        return False

    # Extract high-priority tasks only (first 15 lines after header)
    lines = content.splitlines()
    high_prio = []
    for line in lines[:25]:
        if "priority: H" in line or line.startswith("## "):
            high_prio.append(line)
        elif line.startswith("- [ ]") and len(high_prio) < 10:
            high_prio.append(line)

    if not high_prio:
        log.debug("bridge: no high-priority tasks found")
        return False

    log.info(f"bridge: writing {len(high_prio)} tasks to Claude auto-memory")
    mem_file = CLAUDE_MEMORY_DIR / "engram_agent_tasks.md"
    mem_content = f"""---
name: engram-agent open tasks
description: High-priority open tasks extracted from daily self-analysis (auto-synced from ~/engram-memory)
type: project
---

Last synced: {TODAY}

{chr(10).join(high_prio)}
"""
    mem_file.write_text(mem_content)
    _ensure_index_entry("engram_agent_tasks.md", "Open tasks from daily self-analysis (auto-synced)")
    return True


def _sync_patterns(patterns_file: Path) -> bool:
    """Write recent behavioral patterns as a project memory. Returns True if synced."""
    if not patterns_file.exists():
        log.debug(f"bridge: {patterns_file} does not exist, skipping patterns")
        return False
    content = patterns_file.read_text().strip()
    if not content or len(content) < 20:
        log.debug(f"bridge: {patterns_file} too short ({len(content)} chars), skipping")
        return False

    # Get the most recent dated section
    # _prepend_section writes: \n## YYYY-MM-DD\n (with leading newline)
    sections = re.split(r"\n+(?=## \d{4}-\d{2}-\d{2})", content)
    if len(sections) > 1:
        # sections[0] = "# Patterns" header, sections[1] = latest dated section
        latest = sections[1][:500].strip()
    else:
        # No dated sections found, skip header line and take body
        lines = content.splitlines()
        body = "\n".join(lines[1:]) if lines else ""
        latest = body[:500].strip()

    if not latest:
        log.debug("bridge: no recent patterns found")
        return False

    log.info(f"bridge: writing patterns ({len(latest)} chars) to Claude auto-memory")
    mem_file = CLAUDE_MEMORY_DIR / "engram_agent_patterns.md"
    mem_content = f"""---
name: engram-agent behavioral patterns
description: Recent work patterns from daily self-analysis — tool usage, focus, coding rhythm (auto-synced from ~/engram-memory)
type: project
---

Last synced: {TODAY}

{latest}
"""
    mem_file.write_text(mem_content)
    _ensure_index_entry("engram_agent_patterns.md", "Behavioral patterns from daily self-analysis (auto-synced)")
    return True


def _ensure_index_entry(filename: str, description: str):
    """Add entry to MEMORY.md if not already present."""
    if not MEMORY_INDEX.exists():
        return

    index = MEMORY_INDEX.read_text()
    if filename in index:
        return  # already indexed

    # Append to end
    entry = f"- [{description}]({filename}) — auto-synced from engram-agent\n"
    if not index.endswith("\n"):
        index += "\n"
    index += entry
    MEMORY_INDEX.write_text(index)
