"""Bridge Engram analysis into Obsidian daily notes."""

import logging
from datetime import date
from pathlib import Path

import config as cfg

log = logging.getLogger("mind-sync")


def bridge(analysis_dir: Path):
    """Write today's insights into an Obsidian vault daily note."""
    skill_cfg = cfg.skill_config("obsidian-bridge")
    vault = skill_cfg.get("vault_path", "")
    if not vault:
        return
    vault = Path(vault).expanduser()
    folder = skill_cfg.get("daily_notes_folder", "Daily Notes")
    notes_dir = vault / folder
    if not notes_dir.exists():
        log.warning(f"obsidian-bridge: {notes_dir} not found")
        return

    today = date.today().isoformat()
    sections = []

    # Open tasks
    tasks_file = analysis_dir / "tasks.md"
    if tasks_file.exists():
        tasks = [l for l in tasks_file.read_text().splitlines() if l.startswith("- [ ]")][:10]
        if tasks:
            sections.append("### Open Tasks\n\n" + "\n".join(tasks))

    # Recent patterns
    patterns_file = analysis_dir / "patterns.md"
    if patterns_file.exists():
        lines = patterns_file.read_text().splitlines()[1:12]  # skip header
        if lines:
            sections.append("### Recent Patterns\n\n" + "\n".join(lines))

    if not sections:
        return

    marker = "## Engram Sync"
    synced_block = f"\n\n---\n\n{marker}\n\n" + "\n\n".join(sections) + "\n"

    note_path = notes_dir / f"{today}.md"
    if note_path.exists():
        existing = note_path.read_text()
        if marker in existing:
            before = existing[:existing.index(marker)].rstrip()
            note_path.write_text(before + synced_block)
        else:
            note_path.write_text(existing + synced_block)
    else:
        note_path.write_text(f"# {today}\n{synced_block}")

    log.info(f"obsidian-bridge: wrote to {note_path}")
