---
name: obsidian-bridge
description: Bridges daily analysis into Obsidian vault as a daily note.
type: bridge
entry: skill.py
enabled: true
---

# Obsidian Bridge

Writes today's open tasks and recent patterns into your Obsidian vault as a daily note, formatted for the Daily Notes plugin.

## Setup

Add config to `~/.mind/config.toml`:

```toml
[skills.obsidian-bridge]
vault_path = "~/Obsidian/Main"
daily_notes_folder = "Daily Notes"
```

## Behavior

- Appends a `## Engram Sync` section to the daily note
- If the note already exists, appends without overwriting
- If the sync section already exists, replaces it with updated content
- Includes: open tasks (high priority) and recent behavioral patterns
