"""
Synthesizer: Claude Coach
Analyzes Claude Code usage quality from claude_context collector data.
Produces: usage quality score, detected anti-patterns, actionable tips for tomorrow.
Writes to analysis/claude_usage.md — newest entries first.
"""

from datetime import date
from pathlib import Path


TODAY = date.today().isoformat()


def synthesize(raw: dict, analysis_dir: Path) -> str:
    """
    Returns a markdown section to prepend to analysis/claude_usage.md.
    Driven entirely by heuristics — no API call needed.
    """
    ctx = raw.get("claude_context", {})
    sessions_data = raw.get("claude_sessions", {})

    if not ctx and not sessions_data:
        return ""

    session_count = ctx.get("session_count", sessions_data.get("session_count", 0))
    avg_ctx = ctx.get("avg_context_pct", 0)
    avg_calls = ctx.get("avg_tool_calls", 0)
    quality = ctx.get("quality", {})
    score = quality.get("score", 50)
    signals = quality.get("signals", [])
    recommendations = quality.get("recommendations", [])
    overflow = ctx.get("overflow_sessions", [])
    shallow = ctx.get("shallow_sessions", [])
    deep = ctx.get("deep_sessions", [])
    project_map = ctx.get("project_breakdown", {})
    total_tokens = sessions_data.get("total_tokens_approx", 0)

    # Derive additional signals from raw session data
    extra_signals = _derive_signals(sessions_data, ctx)
    signals = extra_signals + signals
    recommendations = _derive_recommendations(sessions_data, ctx) + recommendations

    # Build markdown section
    lines = [
        f"## {TODAY} — Claude Usage Quality",
        "",
        f"**Score: {score}/100** · {session_count} sessions · "
        f"avg {avg_ctx}% context · avg {avg_calls} tool calls · "
        f"~{total_tokens:,} tokens",
        "",
    ]

    if signals:
        lines.append("### 信号")
        for s in signals[:6]:
            lines.append(f"- {s}")
        lines.append("")

    if recommendations:
        lines.append("### 明日优化建议")
        for r in recommendations[:5]:
            lines.append(f"- [ ] {r}")
        lines.append("")

    # Project breakdown (only show projects with notable patterns)
    notable_projects = {
        p: v for p, v in project_map.items()
        if v.get("max_ctx", 0) >= 80 or v.get("total_calls", 0) >= 30
    }
    if notable_projects:
        lines.append("### 项目分析")
        for proj, stats in list(notable_projects.items())[:4]:
            ctx_flag = "⚠️ 溢出" if stats.get("max_ctx", 0) >= 90 else ""
            lines.append(
                f"- **{proj}**: {stats['sessions']} sessions · "
                f"max context {stats['max_ctx']}% {ctx_flag} · "
                f"{stats['total_calls']} tool calls · "
                f"{stats['edits']} file changes"
            )
        lines.append("")

    # Depth distribution
    if overflow or deep or shallow:
        lines.append("### Session 深度分布")
        lines.append(
            f"- 深度 (≥20 calls): {len(deep)} sessions  "
            f"| 溢出 (>90% ctx): {len(overflow)} sessions  "
            f"| 浅层 (<8 calls): {len(shallow)} sessions"
        )
        lines.append("")

    # Framework signals derived from usage metrics
    framework_signals = _derive_framework_signals(ctx, sessions_data, overflow, shallow, deep)
    if framework_signals:
        lines.append("### 框架信号")
        for fs in framework_signals:
            lines.append(f"- {fs}")
        lines.append("")

    lines.append("---")
    return "\n".join(lines)


def _derive_signals(sessions_data: dict, ctx_data: dict) -> list:
    signals = []
    session_count = sessions_data.get("session_count", 0)
    total_tokens = sessions_data.get("total_tokens_approx", 0)
    topics = sessions_data.get("topics", [])

    if session_count > 0 and total_tokens > 0:
        avg_tokens = total_tokens // session_count
        if avg_tokens < 3000:
            signals.append(
                f"平均 {avg_tokens} tokens/session — 偏浅，更适合调试而非架构决策"
            )
        elif avg_tokens > 15000:
            signals.append(
                f"平均 {avg_tokens} tokens/session — 深度良好，适合复杂任务"
            )

    if session_count > 25:
        signals.append(
            f"今日 {session_count} sessions — 高频切换，注意力碎片化风险"
        )

    topic_count = len(topics)
    if topic_count > 12:
        signals.append(
            f"今日涉及 {topic_count} 个技术领域 — scattered 工作模式，考虑限制到 ≤6"
        )

    return signals


def _derive_recommendations(sessions_data: dict, ctx_data: dict) -> list:
    recs = []
    session_count = sessions_data.get("session_count", 0)
    overflow = ctx_data.get("overflow_sessions", [])
    shallow = ctx_data.get("shallow_sessions", [])
    topics = sessions_data.get("topics", [])

    if overflow:
        overflow_projects = list({o["project"] for o in overflow})
        proj_str = ", ".join(overflow_projects[:2])
        recs.append(
            f"项目 [{proj_str}] 发生 context 溢出 → "
            f"下次在 ~60% 时主动 /compact，或用 subagent 隔离大任务"
        )

    if len(shallow) > session_count * 0.4 and session_count > 5:
        recs.append(
            "大量浅层 session → 把相关的快速问题合并到一个 session 里处理，"
            "用 --continue 延续上下文"
        )

    if len(topics) > 10:
        recs.append(
            f"今日 {len(topics)} 个技术话题 → 明天先选 2 个最重要的，"
            "其他在 tasks.md 里排队"
        )

    if session_count > 0:
        total_tokens = sessions_data.get("total_tokens_approx", 0)
        avg = total_tokens // session_count if session_count else 0
        if avg < 4000 and session_count > 10:
            recs.append(
                "架构/设计类问题需要更深的 session → 明天对复杂问题用 --effort high 或 --model opus"
            )

    return recs


def _derive_framework_signals(ctx: dict, sessions_data: dict,
                               overflow: list, shallow: list, deep: list) -> list:
    """Map usage metrics to physics/math framework diagnostics."""
    signals = []
    avg_ctx = ctx.get("avg_context_pct", 0)
    session_count = sessions_data.get("session_count", 0)
    topics = sessions_data.get("topics", [])

    # 相变临界点: context approaching cliff
    if avg_ctx >= 85:
        signals.append(
            f"⚠️ 相变临界点: 平均 context {avg_ctx}% — 已超断崖区，立即 /compact 或拆 subagent"
        )
    elif avg_ctx >= 70:
        signals.append(
            f"🔶 相变预警: 平均 context {avg_ctx}% — 接近临界点(70%)，主动压缩"
        )

    # 量子/原子状态: session depth distribution
    if shallow and deep:
        shallow_ratio = len(shallow) / max(session_count, 1)
        deep_ratio = len(deep) / max(session_count, 1)
        if shallow_ratio > 0.6:
            signals.append(
                f"量子探索模式: {len(shallow)} 浅层 sessions — 正在探索多假设，"
                "确保有明确测量标准后再收敛"
            )
        elif deep_ratio > 0.4:
            signals.append(
                f"原子收敛模式: {len(deep)} 深度 sessions — 正在精确执行，"
                "避免中途切换到新假设"
            )

    # 香农熵: topic scatter = high entropy
    topic_count = len(topics)
    if topic_count > 10:
        signals.append(
            f"香农熵高: 今日 {topic_count} 个话题 — 输出分散，"
            "明天用帕累托前沿选出 top 2 专注"
        )

    # PID I分量: overflow indicates accumulated systemic issue
    if len(overflow) >= 2:
        overflow_projects = list({o["project"] for o in overflow})
        signals.append(
            f"PID I分量: {', '.join(overflow_projects[:2])} 反复 context 溢出 — "
            "系统性问题，不是单次偶发，需要架构层面修复"
        )

    return signals


def update_usage_file(coach_section: str, analysis_dir: Path) -> None:
    """Prepend today's coaching section to analysis/claude_usage.md."""
    if not coach_section.strip():
        return

    usage_file = analysis_dir / "claude_usage.md"
    existing = usage_file.read_text() if usage_file.exists() else ""

    if not existing.strip():
        content = f"# Claude Usage Quality\n\n{coach_section}\n"
    else:
        lines = existing.split("\n", 1)
        if lines[0].startswith("# "):
            rest = lines[1] if len(lines) > 1 else ""
            content = f"{lines[0]}\n\n{coach_section}\n\n{rest}"
        else:
            content = f"# Claude Usage Quality\n\n{coach_section}\n\n{existing}"

    usage_file.write_text(content)
