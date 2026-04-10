"""
Collector: Git Activity
Scans git repos for today's commits by the configured author.
Uses --since/--until for reliable date filtering.
"""

import subprocess
from pathlib import Path

import config as cfg


def collect(today: str) -> dict:
    repos = _find_repos()
    author = _get_author()
    all_commits = []
    repo_stats = []

    for repo in repos:
        try:
            commits = _get_commits(repo, today, author)
            if not commits:
                continue
            files = _get_changed_files(repo, today, author)
            all_commits.extend(commits)
            repo_stats.append({
                "repo": repo.name,
                "path": str(repo),
                "commits": len(commits),
                "files_changed": len(files),
                "messages": [c["message"] for c in commits],
            })
        except Exception:
            continue

    return {
        "repos_active": len(repo_stats),
        "total_commits": len(all_commits),
        "total_files_changed": sum(r["files_changed"] for r in repo_stats),
        "repos": repo_stats,
        "commit_messages": [c["message"] for c in all_commits],
        "velocity": _classify_velocity(len(all_commits)),
    }


def _get_author() -> str:
    """Get git author email from config or git config."""
    email = cfg.git_author_email()
    if email:
        return email
    result = subprocess.run(
        ["git", "config", "user.email"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def _find_repos() -> list:
    found = set()
    # Configured extra repos
    for r in cfg.extra_repos():
        if (r / ".git").exists():
            found.add(r)
    # Scan directories
    for root in cfg.scan_roots():
        if not root.exists():
            continue
        # Depth-limited search: look for .git dirs up to 3 levels deep
        for depth in range(1, 4):
            pattern = "/".join(["*"] * depth) + "/.git"
            for git_dir in root.glob(pattern):
                if git_dir.is_dir():
                    found.add(git_dir.parent)
                if len(found) > 50:
                    break
            if len(found) > 50:
                break
    return list(found)


def _get_commits(repo: Path, today: str, author: str) -> list:
    cmd = [
        "git", "log", "--oneline", "--no-merges",
        f"--since={today} 00:00",
        f"--until={today} 23:59:59",
        "--format=%H|%s|%ae|%ai",
    ]
    if author:
        cmd.append(f"--author={author}")

    result = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    commits = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("|", 3)
        if len(parts) >= 2:
            commits.append({"hash": parts[0][:8], "message": parts[1]})
    return commits


def _get_changed_files(repo: Path, today: str, author: str) -> list:
    """Get files changed in today's commits."""
    cmd = [
        "git", "log", "--name-only", "--pretty=format:",
        f"--since={today} 00:00",
        f"--until={today} 23:59:59",
    ]
    if author:
        cmd.append(f"--author={author}")

    result = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    files = [f for f in result.stdout.strip().splitlines() if f.strip()]
    return list(set(files))


def _classify_velocity(commit_count: int) -> str:
    if commit_count == 0:
        return "idle"
    elif commit_count <= 3:
        return "light"
    elif commit_count <= 10:
        return "active"
    else:
        return "high"
