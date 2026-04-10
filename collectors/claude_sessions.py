"""
Collector: Claude Code Sessions
Parses ~/.claude/projects/ JSONL session files for today's activity.
Extracts: decisions made, code written, topics explored, open questions.
"""

import json
import re
from datetime import date
from pathlib import Path


# Broader topic detection with categories
TOPIC_PATTERNS = {
    # Infra & DevOps
    "docker": r"\bdocker\b|dockerfile|container",
    "ci/cd": r"\bci\b|github.actions|pipeline|deploy|coolify",
    "kubernetes": r"\bk8s\b|kubernetes|helm|pod",
    "nginx": r"\bnginx\b|reverse.proxy|load.balanc",
    # Backend
    "api": r"\bapi\b|endpoint|rest\b|graphql",
    "database": r"\bdatabase\b|postgres|redis|sql\b|migration|prisma",
    "auth": r"\bauth\b|jwt|oauth|session|token|login",
    "go": r"\bgo\b.*\b(func|package|goroutine)\b|\bgin\b|\becho\b",
    "python": r"\bpython\b|pip\b|venv|fastapi|django",
    # Frontend
    "react": r"\breact\b|jsx|component|hook|useState",
    "nextjs": r"\bnext\.?js\b|getServerSide|app.router",
    "typescript": r"\btypescript\b|\bts\b|interface\s+\w+|type\s+\w+\s*=",
    "css": r"\btailwind\b|css\b|styled|className",
    # AI
    "agent": r"\bagent\b|multi.agent|orchestrat|claude.sdk",
    "prompt": r"\bprompt\b|system.message|few.shot|chain.of.thought",
    "llm": r"\bllm\b|model|anthropic|openai|embedding",
    # Web3
    "blockchain": r"\bweb3\b|blockchain|contract|solidity|ethers",
    # General
    "testing": r"\btest\b|jest|vitest|pytest|spec\b",
    "refactor": r"\brefactor\b|cleanup|restructur|reorganiz",
    "debug": r"\bbug\b|debug|fix\b|error\b|issue",
    "perf": r"\bperformance\b|optimi[zs]|latency|cache",
}

# Decision signal patterns
DECISION_SIGNALS = [
    r"(?:decided|决定|选择|will use|going with|let's go with|采用|确定用)",
    r"(?:switching to|migrating to|replacing .+ with)",
    r"(?:approach:|plan:|strategy:)",
]

# Question signal patterns
QUESTION_SIGNALS = [
    r"\?|？",
    r"(?:todo|TODO|FIXME|HACK|need to figure)",
    r"(?:not sure|unclear|should we|how to|怎么|是否)",
]


def collect(claude_projects: Path, today: str) -> dict:
    sessions = []
    total_chars = 0
    topics = set()
    decisions = []
    open_questions = []
    files_touched = set()

    if not claude_projects.exists():
        return {"session_count": 0, "note": "~/.claude/projects not found"}

    for session_file in claude_projects.rglob("*.jsonl"):
        try:
            entries = _parse_session(session_file, today)
            if not entries:
                continue
            session_data = _extract_insights(entries)
            sessions.append({
                "project": session_file.parent.name,
                "file": session_file.name,
                "turns": session_data["turns"],
                "summary": session_data["summary"],
                "files": session_data["files"][:20],
            })
            total_chars += session_data["total_chars"]
            topics.update(session_data["topics"])
            decisions.extend(session_data["decisions"])
            open_questions.extend(session_data["questions"])
            files_touched.update(session_data["files"])
        except Exception:
            continue

    return {
        "session_count": len(sessions),
        "total_tokens_approx": total_chars // 4,  # ~4 chars per token
        "sessions": sessions[:20],
        "topics": list(topics),
        "decisions": decisions[:15],
        "open_questions": open_questions[:15],
        "files_touched": list(files_touched)[:50],
    }


def _parse_session(path: Path, today: str) -> list:
    entries = []
    for line in path.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            # Timestamp can be at top level or nested
            ts = (obj.get("timestamp", "")
                  or obj.get("message", {}).get("timestamp", "")
                  or obj.get("snapshot", {}).get("timestamp", ""))
            if today in str(ts):
                entries.append(obj)
        except Exception:
            continue
    return entries


def _extract_insights(entries: list) -> dict:
    messages = []
    files = set()
    decisions = []
    questions = []
    topics = set()
    total_chars = 0

    for entry in entries:
        # Claude Code JSONL nests under "message" key
        msg = entry.get("message", entry)
        role = msg.get("role", entry.get("type", ""))
        content = msg.get("content", "")

        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text", "")
                    if text:
                        messages.append({"role": role, "text": text})
                        total_chars += len(text)
                    if block.get("type") == "tool_use":
                        inp = block.get("input", {})
                        for k in ["path", "file_path", "filename", "command"]:
                            if k in inp and isinstance(inp[k], str):
                                files.add(inp[k])
                    if block.get("type") == "tool_result":
                        # tool results may contain file paths
                        pass
        elif isinstance(content, str) and content.strip():
            messages.append({"role": role, "text": content})
            total_chars += len(content)

    # Topic detection with regex
    all_text = " ".join(m["text"][:500] for m in messages)
    for topic, pattern in TOPIC_PATTERNS.items():
        if re.search(pattern, all_text, re.IGNORECASE):
            topics.add(topic)

    # Decision detection
    decision_re = "|".join(DECISION_SIGNALS)
    for m in messages:
        if m["role"] == "assistant":
            continue  # only count user/human decisions
        if re.search(decision_re, m["text"], re.IGNORECASE):
            # Extract the sentence containing the decision
            snippet = m["text"][:300].strip()
            if snippet:
                decisions.append(snippet)

    # Question detection
    question_re = "|".join(QUESTION_SIGNALS)
    for m in messages:
        if re.search(question_re, m["text"], re.IGNORECASE):
            snippet = m["text"][:200].strip()
            if snippet:
                questions.append(snippet)

    return {
        "turns": len(messages),
        "summary": f"{len(messages)} messages, {len(files)} files, {len(topics)} topics",
        "files": list(files),
        "total_chars": total_chars,
        "decisions": decisions[:5],
        "questions": questions[:5],
        "topics": list(topics),
    }
