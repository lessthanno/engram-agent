"""Notion activity collector for Engram Agent."""

import json
import logging
from urllib.request import urlopen, Request

import config as cfg

log = logging.getLogger("mind-sync")


def collect(today: str) -> dict:
    """Collect Notion pages edited today."""
    skill_cfg = cfg.skill_config("notion-collector")
    api_key = skill_cfg.get("api_key", "")
    if not api_key:
        return {"error": "no api_key configured in [skills.notion-collector]"}

    db_ids = skill_cfg.get("database_ids", [])
    if isinstance(db_ids, str):
        db_ids = [db_ids]

    pages_edited = []

    for db_id in db_ids:
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        body = json.dumps({
            "filter": {
                "timestamp": "last_edited_time",
                "last_edited_time": {"on_or_after": today}
            }
        }).encode()
        req = Request(url, data=body, headers={
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        })
        try:
            resp = json.loads(urlopen(req, timeout=15).read())
            for page in resp.get("results", []):
                title_prop = page.get("properties", {}).get("Name", {})
                title = ""
                if title_prop.get("title"):
                    title = title_prop["title"][0].get("plain_text", "")
                pages_edited.append({
                    "id": page["id"],
                    "title": title,
                    "last_edited": page.get("last_edited_time", ""),
                    "url": page.get("url", ""),
                })
        except Exception as e:
            log.warning(f"notion query failed for {db_id}: {e}")
            pages_edited.append({"error": str(e), "database_id": db_id})

    return {
        "pages_edited_today": len([p for p in pages_edited if "error" not in p]),
        "pages": pages_edited,
    }
