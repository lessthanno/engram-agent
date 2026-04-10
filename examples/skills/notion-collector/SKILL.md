---
name: notion-collector
description: Collects today's Notion page edits and database changes via the Notion API.
type: collector
entry: skill.py
enabled: true
---

# Notion Collector

Queries the Notion API for pages edited today. Returns structured data for the synthesis pipeline.

## Setup

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Share your databases with the integration
3. Add config to `~/.mind/config.toml`:

```toml
[skills.notion-collector]
api_key = "ntn_xxxxx"
database_ids = ["your-database-id"]
```

## Output

```json
{
  "pages_edited_today": 3,
  "pages": [
    {"id": "...", "title": "Meeting Notes", "last_edited": "2026-04-10T14:30:00Z", "url": "..."}
  ]
}
```
