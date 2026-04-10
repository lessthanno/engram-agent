"""
Collector: System Operations
Captures: files created/modified, processes run, network connections,
clipboard patterns (opt-in), browser tabs (via AppleScript).
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime


def collect(today: str) -> dict:
    return {
        "recent_files": _recent_files(today),
        "running_processes": _running_processes(),
        "browser_tabs": _browser_tabs(),
        "disk_writes": _disk_activity(),
        "network_summary": _network_summary(),
    }


def _recent_files(today: str) -> list:
    """Files modified today in common work directories."""
    dirs = [
        Path("~/code").expanduser(),
        Path("~/Desktop").expanduser(),
        Path("~/Documents").expanduser(),
        Path("~/Downloads").expanduser(),
    ]
    files = []
    for d in dirs:
        if not d.exists():
            continue
        result = subprocess.run(
            ["find", str(d), "-maxdepth", "4",
             "-mtime", "0",  # modified today (last 24h)
             "-type", "f",
             "!", "-path", "*/.git/*",
             "!", "-path", "*/node_modules/*",
             "!", "-path", "*/__pycache__/*",
             "!", "-path", "*/.next/*",
             "!", "-name", ".DS_Store"],
            capture_output=True, text=True, timeout=30
        )
        files.extend(result.stdout.strip().splitlines())

    return files[:100]


def _running_processes() -> list:
    """Get currently interesting processes (exclude system daemons)."""
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True, text=True
    )
    user = os.environ.get("USER", "")
    interesting = []
    skip = {"kernel", "launchd", "loginwindow", "WindowServer", "coreaudiod",
             "configd", "logd", "com.apple", "spotlightknowledged"}

    for line in result.stdout.splitlines()[1:]:
        parts = line.split(None, 10)
        if len(parts) < 11:
            continue
        proc_user = parts[0]
        cmd = parts[10]
        if proc_user != user:
            continue
        if any(s in cmd for s in skip):
            continue
        if cmd.startswith("-"):
            continue
        interesting.append(cmd.split("/")[-1][:60])

    return list(set(interesting))[:30]


def _browser_tabs() -> list:
    """Get open Chrome/Safari tabs via AppleScript (title only, no URLs)."""
    tabs = []

    # Chrome
    chrome_script = '''
    tell application "Google Chrome"
        if it is running then
            set tabList to {}
            repeat with w in windows
                repeat with t in tabs of w
                    set end of tabList to title of t
                end repeat
            end repeat
            return tabList
        end if
    end tell
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", chrome_script],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            tabs.extend([t.strip() for t in result.stdout.split(",") if t.strip()][:20])
    except Exception:
        pass

    # Arc
    arc_script = '''
    tell application "Arc"
        if it is running then
            set tabList to {}
            repeat with w in windows
                repeat with t in tabs of w
                    set end of tabList to title of t
                end repeat
            end repeat
            return tabList
        end if
    end tell
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", arc_script],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            tabs.extend([t.strip() for t in result.stdout.split(",") if t.strip()][:20])
    except Exception:
        pass

    return list(set(tabs))[:40]


def _disk_activity() -> dict:
    """Basic disk usage snapshot."""
    result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()
    if len(lines) >= 2:
        parts = lines[1].split()
        if len(parts) >= 5:
            return {"size": parts[1], "used": parts[2], "avail": parts[3], "pct": parts[4]}
    return {}


def _network_summary() -> dict:
    """Check which network interfaces are active."""
    result = subprocess.run(["ifconfig"], capture_output=True, text=True)
    active = []
    for line in result.stdout.splitlines():
        if "inet " in line and "127.0.0.1" not in line:
            ip = line.strip().split()[1]
            active.append(ip)
    return {"active_ips": active}
