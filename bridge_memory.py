"""
Bridge: engram-memory → Claude auto-memory
Syncs key insights from engram-memory/analysis/ into ~/.claude/projects/ memory.
Runs after daily synthesis to keep Claude's auto-memory aware of patterns.
"""

import os
import re
from datetime import date
from pathlib import Path


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
        return

    _sync_tasks(analysis_dir / "tasks.md")
    _sync_patterns(analysis_dir / "patterns.md")


def _sync_tasks(tasks_file: Path):
    """Write current open tasks as a project memory."""
    if not tasks_file.exists():
        return
    content = tasks_file.read_text().strip()
    if not content or len(content) < 20:
        return

    # Extract high-priority tasks only (first 15 lines after header)
    lines = content.splitlines()
    high_prio = []
    for line in lines[:25]:
        if "priority: H" in line or line.startswith("## "):
            high_prio.append(line)
        elif line.startswith("- [ ]") and len(high_prio) < 10:
            high_prio.append(line)

    if not high_prio:
        return

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


def _sync_patterns(patterns_file: Path):
    """Write recent behavioral patterns as a project memory."""
    if not patterns_file.exists():
        return
    content = patterns_file.read_text().strip()
    if not content or len(content) < 20:
        return

    # Get the most recent dated section
    # _prepend_section writes: 
## YYYY-MM-DD

 (with leading newline)
    sections = re.split(r"
+(?=## \d{4}-\d{2}-\d{2})", content)
    if len(sections) > 1:
        # sections[0] = "# Patterns" header, sections[1] = latest dated section
        latest = sections[1][:500].strip()
    else:
        # No dated sections found, skip header line and take body
        lines = content.splitlines()
        body = "
".join(lines[1:]) if lines else ""
        latest = body[:500].strip()

    if not latest:
        return

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


def _ensure_index_entry(filename: str, description: str):
    """Add entry to MEMORY.md if not already present."""
    if not MEMORY_INDEX.exists():
        return

    index = MEMORY_INDEX.read_text()
    if filename in index:
        return  # already indexed

    # Append to end
    entry = f"- [{description}]({filename}) — auto-synced from engram-agent
"
    if not index.endswith("
"):
        index += "
"
    index += entry
    MEMORY_INDEX.write_text(index)
