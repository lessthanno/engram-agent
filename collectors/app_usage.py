"""
Collector: App Usage + Window Titles
Uses ActivityWatch (localhost:5600) to get today's app usage.
ActivityWatch is open-source, fully local, privacy-safe.
Install: https://activitywatch.net

Falls back to macOS Screen Time if ActivityWatch not running.
"""

import json
import subprocess
from datetime import date, datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError


def _local_tz_offset() -> str:
    """Get local timezone offset as +HH:MM string."""
    offset = datetime.now(timezone.utc).astimezone().utcoffset()
    total_seconds = int(offset.total_seconds())
    hours, remainder = divmod(abs(total_seconds), 3600)
    minutes = remainder // 60
    sign = "+" if total_seconds >= 0 else "-"
    return f"{sign}{hours:02d}:{minutes:02d}"


AW_BASE = "http://localhost:5600/api/0"


def collect(today: str) -> dict:
    # Try ActivityWatch first
    try:
        return _collect_activitywatch(today)
    except Exception:
        pass

    # Fallback: macOS usage via AppleScript (app switch events only)
    try:
        return _collect_macos_fallback(today)
    except Exception:
        return {"note": "ActivityWatch not running. Install from activitywatch.net"}


def _collect_activitywatch(today: str) -> dict:
    # Get available buckets
    req = Request(f"{AW_BASE}/buckets")
    with urlopen(req, timeout=3) as r:
        buckets = json.loads(r.read())

    results = {
        "source": "activitywatch",
        "apps": {},
        "window_titles": [],
        "total_active_seconds": 0,
        "focus_score": 0,
        "top_apps": [],
        "context_switches": 0,
    }

    # Window watcher buckets (exclude AFK buckets)
    window_buckets = [b for b in buckets if "window" in b.lower() and "afk" not in b.lower()]

    for bucket_id in window_buckets:
        events = _get_bucket_events(bucket_id, today)
        for event in events:
            dur = event.get("duration", 0)
            data = event.get("data", {})
            app = data.get("app", data.get("title", "unknown"))
            title = data.get("title", "")

            if app not in results["apps"]:
                results["apps"][app] = 0
            results["apps"][app] += dur
            results["total_active_seconds"] += dur
            if title and title not in results["window_titles"]:
                results["window_titles"].append(title[:80])

    results["context_switches"] = len(results["window_titles"])
    # Sort apps by time
    sorted_apps = sorted(results["apps"].items(), key=lambda x: x[1], reverse=True)
    results["top_apps"] = [
        {"app": a, "minutes": round(s / 60, 1)}
        for a, s in sorted_apps[:15]
    ]
    # Focus score: % of time in top app vs total
    if results["top_apps"] and results["total_active_seconds"] > 0:
        top_mins = results["top_apps"][0]["minutes"]
        total_mins = results["total_active_seconds"] / 60
        results["focus_score"] = round(top_mins / total_mins * 100, 1)

    return results


def _get_bucket_events(bucket_id: str, today: str) -> list:
    tz = _local_tz_offset()
    start = f"{today}T00:00:00{tz}"
    end = f"{today}T23:59:59{tz}"
    url = f"{AW_BASE}/buckets/{bucket_id}/events?start={start}&end={end}&limit=10000"
    try:
        with urlopen(Request(url), timeout=5) as r:
            return json.loads(r.read())
    except Exception:
        return []


def _collect_macos_fallback(today: str) -> dict:
    """Get frontmost app history via macOS accessibility (limited)."""
    script = '''
    tell application "System Events"
        set appList to name of every process where background only is false
        return appList as string
    end tell
    '''
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True
    )
    apps = [a.strip() for a in result.stdout.split(",") if a.strip()]
    return {
        "source": "macos_fallback",
        "running_apps": apps,
        "note": "Install ActivityWatch for detailed tracking: activitywatch.net"
    }
