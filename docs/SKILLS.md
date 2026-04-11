# Skills — Extend Engram

Engram has a built-in skill system. Add custom collectors, synthesizers, or bridges without touching core code.

## Create a Skill

Drop a folder into `~/.mind/skills/` with two files:

```
~/.mind/skills/my-collector/
  SKILL.md      # metadata (name, type, description)
  skill.py      # your Python code
```

## SKILL.md Format

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
| `function` | No | Based on type | Function name to call (see below) |
| `enabled` | No | `true` | Can be overridden in `config.toml` |

## Function Signatures

| Type | Default function | Signature |
|------|-----------------|-----------|
| collector | `collect` | `collect(today: str) -> dict` |
| synthesizer | `synthesize` | `synthesize(raw: dict, analysis_dir: Path)` |
| bridge | `bridge` | `bridge(analysis_dir: Path)` |

- **Collectors** return a dict merged into the raw data pipeline.
- **Synthesizers** write files into the analysis directory.
- **Bridges** push results to external systems (Obsidian, Notion, etc).

## Configuration

Per-skill settings in `~/.mind/config.toml`:

```toml
[skills.notion-collector]
api_key = "ntn_xxxxx"
database_ids = ["abc123"]
```

Access inside your skill:

```python
import config as cfg
skill_cfg = cfg.skill_config("notion-collector")
```

Priority: env vars > config.toml > code defaults.

## Toggle Skills

```toml
# Disable all
[skills]
enabled = false

# Disable one
[skills.notion-collector]
enabled = false
```

## Error Handling

Skills are fault-tolerant. A broken skill logs a warning and never crashes the pipeline.

## Examples

See [`examples/skills/`](../examples/skills/):
- **notion-collector** — Notion page edits via API
- **obsidian-bridge** — daily insights to Obsidian vault

## Auto-Discovery

No registration needed. Drop a folder into `~/.mind/skills/` and it works.
