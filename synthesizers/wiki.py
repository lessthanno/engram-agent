"""
Wiki Compiler: Compiles raw daily data into a structured Markdown wiki.

Follows Karpathy's llm.wiki architecture:
  raw/ (immutable) → wiki/ (compiled, linked, accumulating)

Three operations: ingest, query, lint.
"""

import json
import logging
import os
import re
import shutil
import subprocess
from datetime import date, datetime
from pathlib import Path

import config as cfg

log = logging.getLogger("mind-sync")
TODAY = date.today().isoformat()


# ── Ingest ───────────────────────────────────────────────────────────────────

def ingest(raw: dict, wiki_dir: Path):
    """Compile raw daily data into wiki pages."""
    _ensure_dirs(wiki_dir)

    # 1. Compile daily reflection page
    daily_page = _compile_daily(raw, wiki_dir)

    # 2. Ripple updates: projects, patterns, decisions, weaknesses
    touched_pages = [daily_page]
    touched_pages += _ripple_projects(raw, wiki_dir)
    touched_pages += _ripple_decisions(raw, wiki_dir)
    touched_pages += _ripple_weaknesses(raw, wiki_dir)
    touched_pages += _ripple_patterns(raw, wiki_dir)

    # 3. Update index.md
    _update_index(wiki_dir)

    # 4. Append to log.md
    _append_log(wiki_dir, touched_pages)

    log.info(f"wiki ingest complete: {len(touched_pages)} pages touched")
    return touched_pages


def _ensure_dirs(wiki_dir: Path):
    for d in ["daily", "projects", "patterns", "decisions", "weaknesses", "concepts"]:
        (wiki_dir / d).mkdir(parents=True, exist_ok=True)


# ── Daily Page ───────────────────────────────────────────────────────────────

def _compile_daily(raw: dict, wiki_dir: Path) -> str:
    date_str = raw.get("date", TODAY)
    git = raw.get("git_activity", {})
    cs = raw.get("claude_sessions", {})
    app = raw.get("app_usage", {})
    kb = raw.get("input_habits", {}).get("keyboard", {})
    sh = raw.get("input_habits", {}).get("shell_commands", {})
    patterns = raw.get("input_habits", {}).get("patterns", {})
    sysops = raw.get("system_ops", {})

    # Build topics and project links
    topics = cs.get("topics", [])
    topic_tags = ", ".join(topics) if topics else "none detected"

    # Project links from git repos
    project_links = []
    for repo in git.get("repos", []):
        name = repo["repo"]
        slug = _slugify(name)
        project_links.append(f"[[projects/{slug}|{name}]]")

    # Decision summaries
    decisions = cs.get("decisions", [])
    decision_section = ""
    if decisions:
        decision_section = "\n## Decisions Made\n"
        for d in decisions[:5]:
            decision_section += f"- {d[:200]}\n"

    # Open questions
    questions = cs.get("open_questions", [])
    question_section = ""
    if questions:
        question_section = "\n## Open Questions\n"
        for q in questions[:8]:
            question_section += f"- {q[:200]}\n"

    # Tools
    top_tools = [t["tool"] for t in sh.get("top_tools", [])[:8]]

    # Commits
    commit_section = ""
    if git.get("commit_messages"):
        commit_section = "\n## Commits\n"
        for msg in git["commit_messages"][:15]:
            commit_section += f"- `{msg}`\n"

    # Browser context
    tabs = sysops.get("browser_tabs", [])
    tab_section = ""
    if tabs:
        tab_section = "\n## Browser Context\n"
        for t in tabs[:10]:
            tab_section += f"- {t}\n"

    tldr = (f"{cs.get('session_count', 0)} Claude sessions, "
            f"{git.get('total_commits', 0)} commits, "
            f"velocity={git.get('velocity', 'idle')}, "
            f"topics: {', '.join(topics[:5]) if topics else 'none'}")

    content = f"""---
title: "{date_str} Daily Reflection"
type: daily
created: {date_str}
updated: {date_str}
confidence: high
tags: [{topic_tags}]
related: [{', '.join(f'"{p}"' for p in project_links)}]
sources: ["raw/{date_str}.json"]
tldr: "{tldr}"
---

## TLDR
{tldr}

## Stats
| Metric | Value |
|--------|-------|
| Commits | {git.get('total_commits', 0)} |
| Repos Active | {git.get('repos_active', 0)} ({', '.join(project_links) if project_links else 'none'}) |
| Velocity | **{git.get('velocity', 'idle')}** |
| Claude Sessions | {cs.get('session_count', 0)} |
| Tokens (approx) | ~{cs.get('total_tokens_approx', 0):,} |
| Focus Score | {app.get('focus_score', 'n/a')}{'%' if isinstance(app.get('focus_score'), (int, float)) else ''} |
| Keystrokes | {kb.get('total_keystrokes', 'n/a')} |
| WPM | {kb.get('wpm_estimate', 'n/a')} |
| Typing Intensity | {kb.get('intensity', 'n/a')} |
| Shell Commands Today | {sh.get('today_command_count', 0)} |
| Top Tools | {', '.join(f'`{t}`' for t in top_tools)} |
| Work Diversity | {patterns.get('work_diversity', 'n/a')} |
{decision_section}
{question_section}
{commit_section}
{tab_section}
## Topics
{', '.join(f'`{t}`' for t in topics) if topics else 'No topics detected.'}

## Files Touched
{len(cs.get('files_touched', []))} files across {cs.get('session_count', 0)} sessions.
"""

    page_path = wiki_dir / "daily" / f"{date_str}.md"
    page_path.write_text(content.strip() + "\n")
    log.info(f"  wiki: daily/{date_str}.md")
    return f"daily/{date_str}"


# ── Ripple: Projects ─────────────────────────────────────────────────────────

def _ripple_projects(raw: dict, wiki_dir: Path) -> list:
    """Create or update project pages for active repos."""
    touched = []
    git = raw.get("git_activity", {})
    date_str = raw.get("date", TODAY)

    for repo in git.get("repos", []):
        name = repo["repo"]
        slug = _slugify(name)
        page_path = wiki_dir / "projects" / f"{slug}.md"

        if page_path.exists():
            # Append today's activity
            existing = page_path.read_text()
            entry = f"\n### {date_str}\n"
            entry += f"- {repo['commits']} commits, {repo['files_changed']} files changed\n"
            for msg in repo.get("messages", [])[:5]:
                entry += f"- `{msg}`\n"

            # Update frontmatter 'updated' date
            existing = re.sub(r'updated: \d{4}-\d{2}-\d{2}', f'updated: {date_str}', existing)
            page_path.write_text(existing + entry)
        else:
            # Create new project page
            content = f"""---
title: "{name}"
type: project
created: {date_str}
updated: {date_str}
confidence: medium
tags: []
related: ["[[daily/{date_str}]]"]
sources: ["raw/{date_str}.json"]
tldr: "Project {name}, first seen {date_str}"
---

## TLDR
Project `{name}` — tracked since {date_str}.

## Activity Log

### {date_str}
- {repo['commits']} commits, {repo['files_changed']} files changed
"""
            for msg in repo.get("messages", [])[:5]:
                content += f"- `{msg}`\n"

            page_path.write_text(content.strip() + "\n")

        log.info(f"  wiki: projects/{slug}.md")
        touched.append(f"projects/{slug}")

    return touched


# ── Ripple: Decisions ────────────────────────────────────────────────────────

def _ripple_decisions(raw: dict, wiki_dir: Path) -> list:
    touched = []
    cs = raw.get("claude_sessions", {})
    date_str = raw.get("date", TODAY)
    decisions = cs.get("decisions", [])

    for i, decision in enumerate(decisions[:3]):  # max 3 per day
        slug = _slugify(decision[:30])
        filename = f"{date_str}-{slug}.md"
        page_path = wiki_dir / "decisions" / filename

        if page_path.exists():
            continue

        topics = cs.get("topics", [])
        content = f"""---
title: "{decision[:80]}"
type: decision
created: {date_str}
updated: {date_str}
confidence: medium
tags: [{', '.join(topics[:3])}]
related: ["[[daily/{date_str}]]"]
sources: ["raw/{date_str}.json"]
tldr: "{decision[:120]}"
---

## TLDR
{decision[:120]}

## Context
Detected from Claude Code session on {date_str}.

## Decision
{decision[:500]}

## Follow-up
- [ ] Review this decision in 30 days
"""
        page_path.write_text(content.strip() + "\n")
        log.info(f"  wiki: decisions/{filename}")
        touched.append(f"decisions/{filename[:-3]}")

    return touched


# ── Ripple: Weaknesses ───────────────────────────────────────────────────────

def _ripple_weaknesses(raw: dict, wiki_dir: Path) -> list:
    """Track weaknesses from patterns — late night work, context switching, etc."""
    touched = []
    date_str = raw.get("date", TODAY)
    patterns = raw.get("input_habits", {}).get("patterns", {})

    # Detect: scattered work
    if patterns.get("work_diversity") == "scattered":
        touched += _upsert_weakness(
            wiki_dir, date_str, "context-switching",
            "Context Switching",
            f"Work diversity classified as 'scattered' on {date_str}. "
            "Too many different tools/contexts in one day.",
            ["productivity"]
        )

    return touched


def _upsert_weakness(wiki_dir: Path, date_str: str, slug: str,
                     title: str, evidence: str, tags: list) -> list:
    page_path = wiki_dir / "weaknesses" / f"{slug}.md"

    if page_path.exists():
        existing = page_path.read_text()
        entry = f"\n### {date_str}\n{evidence}\n"
        existing = re.sub(r'updated: \d{4}-\d{2}-\d{2}', f'updated: {date_str}', existing)

        # Increment occurrence count in tldr
        m = re.search(r'Observed (\d+) times', existing)
        count = int(m.group(1)) + 1 if m else 2
        existing = re.sub(r'Observed \d+ times', f'Observed {count} times', existing)

        page_path.write_text(existing + entry)
    else:
        content = f"""---
title: "{title}"
type: weakness
created: {date_str}
updated: {date_str}
confidence: low
tags: [{', '.join(tags)}]
related: ["[[daily/{date_str}]]"]
sources: ["raw/{date_str}.json"]
tldr: "{title} — Observed 1 times since {date_str}"
---

## TLDR
{title}. Observed 1 times.

## Evidence

### {date_str}
{evidence}

## Mitigation
- [ ] Define concrete mitigation strategy
"""
        page_path.write_text(content.strip() + "\n")

    log.info(f"  wiki: weaknesses/{slug}.md")
    return [f"weaknesses/{slug}"]


# ── Ripple: Patterns ─────────────────────────────────────────────────────────

def _ripple_patterns(raw: dict, wiki_dir: Path) -> list:
    """Extract and update behavioral patterns."""
    touched = []
    date_str = raw.get("date", TODAY)
    git = raw.get("git_activity", {})
    cs = raw.get("claude_sessions", {})
    kb = raw.get("input_habits", {}).get("keyboard", {})
    sh = raw.get("input_habits", {}).get("shell_commands", {})

    # Velocity pattern
    velocity = git.get("velocity", "idle")
    touched += _upsert_pattern(
        wiki_dir, date_str, "coding-velocity",
        "Coding Velocity",
        f"Velocity: **{velocity}** — {git.get('total_commits', 0)} commits across {git.get('repos_active', 0)} repos",
        ["git", "productivity"]
    )

    # Tool usage pattern
    top_tools = [t["tool"] for t in sh.get("top_tools", [])[:5]]
    if top_tools:
        touched += _upsert_pattern(
            wiki_dir, date_str, "tool-usage",
            "Tool Usage Patterns",
            f"Top tools: {', '.join(f'`{t}`' for t in top_tools)}. "
            f"{sh.get('today_command_count', 0)} commands today.",
            ["tools", "productivity"]
        )

    # Claude usage pattern
    sessions = cs.get("session_count", 0)
    tokens = cs.get("total_tokens_approx", 0)
    if sessions > 0:
        touched += _upsert_pattern(
            wiki_dir, date_str, "claude-usage",
            "Claude AI Usage",
            f"{sessions} sessions, ~{tokens:,} tokens. Topics: {', '.join(cs.get('topics', [])[:5])}",
            ["ai", "claude"]
        )

    return touched


def _upsert_pattern(wiki_dir: Path, date_str: str, slug: str,
                    title: str, evidence: str, tags: list) -> list:
    page_path = wiki_dir / "patterns" / f"{slug}.md"

    if page_path.exists():
        existing = page_path.read_text()
        entry = f"\n### {date_str}\n{evidence}\n"
        existing = re.sub(r'updated: \d{4}-\d{2}-\d{2}', f'updated: {date_str}', existing)
        page_path.write_text(existing + entry)
    else:
        content = f"""---
title: "{title}"
type: pattern
created: {date_str}
updated: {date_str}
confidence: low
tags: [{', '.join(tags)}]
related: ["[[daily/{date_str}]]"]
sources: ["raw/{date_str}.json"]
tldr: "{title} — tracking since {date_str}"
---

## TLDR
{title}. Tracking behavioral data to detect trends.

## Observations

### {date_str}
{evidence}

## Trends
_Trends will emerge after 7+ days of data._
"""
        page_path.write_text(content.strip() + "\n")

    log.info(f"  wiki: patterns/{slug}.md")
    return [f"patterns/{slug}"]


# ── Index ────────────────────────────────────────────────────────────────────

def _update_index(wiki_dir: Path):
    """Rebuild index.md from all wiki pages."""
    sections = {
        "daily": "Daily Reflections",
        "projects": "Projects",
        "patterns": "Patterns",
        "decisions": "Decisions",
        "weaknesses": "Weaknesses",
        "concepts": "Concepts",
    }

    lines = [
        "---",
        'title: "Wiki Index"',
        "type: index",
        f"updated: {TODAY}",
        "---",
        "",
        f"# {cfg.wiki_title()}",
        "",
        *([ f"> {cfg.wiki_motto()}", ""] if cfg.wiki_motto() else []),
        "",
    ]

    total_pages = 0
    for folder, title in sections.items():
        folder_path = wiki_dir / folder
        if not folder_path.exists():
            continue
        pages = sorted(folder_path.glob("*.md"), reverse=True)
        if not pages:
            continue

        lines.append(f"## {title}")
        lines.append("")
        for page in pages[:30]:  # cap display
            tldr = _extract_tldr(page)
            link_name = page.stem
            lines.append(f"- [[{folder}/{link_name}]] — {tldr}")
            total_pages += 1
        if len(pages) > 30:
            lines.append(f"- _...and {len(pages) - 30} more_")
        lines.append("")

    lines.append(f"---\n_{total_pages} pages total. Updated {TODAY}._\n")

    (wiki_dir / "index.md").write_text("\n".join(lines))
    log.info(f"  wiki: index.md ({total_pages} pages)")


def _extract_tldr(page_path: Path) -> str:
    """Extract tldr from frontmatter."""
    try:
        text = page_path.read_text()
        m = re.search(r'^tldr:\s*["\']?(.+?)["\']?\s*$', text, re.MULTILINE)
        if m:
            return m.group(1)[:120]
    except Exception:
        pass
    return page_path.stem


# ── Log ──────────────────────────────────────────────────────────────────────

def _append_log(wiki_dir: Path, touched_pages: list):
    """Append ingest event to log.md."""
    log_path = wiki_dir / "log.md"
    if not log_path.exists():
        log_path.write_text("# Wiki Log\n\nAppend-only timeline of all wiki operations.\n\n")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- **{timestamp}** ingest: {len(touched_pages)} pages — "
    entry += ", ".join(f"[[{p}]]" for p in touched_pages[:10])
    if len(touched_pages) > 10:
        entry += f" +{len(touched_pages) - 10} more"
    entry += "\n"

    with open(log_path, "a") as f:
        f.write(entry)


# ── Lint ─────────────────────────────────────────────────────────────────────

def lint(wiki_dir: Path) -> dict:
    """Health check the wiki. Returns report dict."""
    issues = {
        "orphan_pages": [],
        "stale_pages": [],
        "missing_links": [],
        "no_tldr": [],
    }

    all_pages = {}
    incoming_links = {}

    for md in wiki_dir.rglob("*.md"):
        rel = md.relative_to(wiki_dir)
        if rel.name in ("index.md", "log.md"):
            continue
        key = str(rel.with_suffix(""))
        all_pages[key] = md
        incoming_links.setdefault(key, 0)

    # Scan links and check TLDRs
    for key, page_path in all_pages.items():
        text = page_path.read_text()

        # Check TLDR
        if "tldr:" not in text:
            issues["no_tldr"].append(key)

        # Find outgoing [[links]]
        links = re.findall(r'\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]', text)
        for link in links:
            link_clean = link.replace(".md", "")
            if link_clean in incoming_links:
                incoming_links[link_clean] += 1
            elif link_clean not in all_pages:
                issues["missing_links"].append({"from": key, "target": link_clean})

        # Check staleness (updated date)
        m = re.search(r'updated: (\d{4}-\d{2}-\d{2})', text)
        if m:
            updated = m.group(1)
            days_old = (date.today() - date.fromisoformat(updated)).days
            if days_old > 30:
                issues["stale_pages"].append({"page": key, "last_updated": updated, "days": days_old})

    # Orphans: pages with 0 incoming links (excluding daily — they're naturally orphans)
    for key, count in incoming_links.items():
        if count == 0 and not key.startswith("daily/"):
            issues["orphan_pages"].append(key)

    return issues


def lint_report(wiki_dir: Path) -> str:
    """Generate a human-readable lint report."""
    issues = lint(wiki_dir)
    lines = [f"# Wiki Lint Report — {TODAY}\n"]

    if issues["orphan_pages"]:
        lines.append(f"## Orphan Pages ({len(issues['orphan_pages'])})")
        lines.append("These pages have no incoming links. Consider linking them or removing.")
        for p in issues["orphan_pages"]:
            lines.append(f"- [[{p}]]")
        lines.append("")

    if issues["stale_pages"]:
        lines.append(f"## Stale Pages ({len(issues['stale_pages'])})")
        for s in issues["stale_pages"]:
            lines.append(f"- [[{s['page']}]] — last updated {s['last_updated']} ({s['days']} days ago)")
        lines.append("")

    if issues["missing_links"]:
        lines.append(f"## Missing Pages ({len(issues['missing_links'])})")
        lines.append("These pages are linked but don't exist yet.")
        seen = set()
        for m in issues["missing_links"]:
            if m["target"] not in seen:
                lines.append(f"- `{m['target']}` (linked from [[{m['from']}]])")
                seen.add(m["target"])
        lines.append("")

    if issues["no_tldr"]:
        lines.append(f"## Missing TLDR ({len(issues['no_tldr'])})")
        for p in issues["no_tldr"]:
            lines.append(f"- [[{p}]]")
        lines.append("")

    total = sum(len(v) for v in issues.values())
    if total == 0:
        lines.append("All clear. Wiki is healthy.\n")
    else:
        lines.append(f"---\n_{total} issues found._\n")

    return "\n".join(lines)


# ── Utilities ────────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Convert text to kebab-case slug."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', text)
    text = text.strip('-')
    return text[:60] if text else "unnamed"
