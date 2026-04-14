# Claude Code 实用技巧手册
> 从官方文档和实战中提取。不是 README，是你遇到具体场景时查的速查表。

---

## 一、Session 管理

### 继续上次对话（不开新 session）
```bash
claude -c                     # 继续当前目录最近的 session
claude -c "继续刚才的重构"      # 继续 + 追加新指令
```
**什么时候用：** 昨天做到一半，今天接着做。避免重新解释上下文。

### 恢复任意历史 session
```bash
claude -r                     # 交互式选择器，列出所有历史
claude -r "zklm"              # 按名称搜索过滤
claude --session-id <uuid>    # 用精确 session ID 恢复
```

### 给 session 取名（以后好找）
```bash
claude -n "zklm-scope-决策" "开始 ZKLM MVP scope 分析"
claude -n "news-v2-debug" -c  # 给正在继续的 session 取名
```

### Fork session（实验性分支，不污染原 session）
```bash
claude -r "news-v2" --fork-session "测试激进重构方案"
```
**场景：** 想测试一个可能推翻现有架构的思路，但不想破坏当前进度。

### 从 PR 恢复 session
```bash
claude --from-pr 123          # 恢复与 PR#123 关联的 session
claude --from-pr              # 选择器列出所有 PR sessions
```

---

## 二、Context 管理（最重要）

### /compact — 主动压缩，不要等满了才压
```
/compact
```
**什么时候用：** context 到 60% 就主动压。到 90% 再压，Claude 的记忆已经开始失真。

**正确姿势：**
1. 开始新的任务阶段前 → /compact
2. 感觉 Claude 开始"忘事"了 → /compact
3. 不是"快满了再压"，是"还有余量时主动压"

### Subagent 隔离大任务（保护主 context）
```
Agent({
  description: "独立完成 ZKLM 架构分析",
  isolation: "worktree",   // 完全隔离，不影响主分支
  prompt: "..."
})
```
**场景：** 一个任务预计会用掉大量 context → 扔给 subagent，主 session 保持干净。

### Worktree 隔离（高风险操作必用）
```bash
claude -w "zklm-mvp-attempt" "实现 ZKLM 第一版，可以大胆重构"
claude -w --tmux "feature-x"  # 同时开 tmux session，持久运行
```
**原理：** worktree 是独立的 git 分支，不影响 main。做砸了直接删，零成本。

### 只允许读文件（安全分析模式）
```bash
claude --allowed-tools "Read Glob Grep" "分析整个项目架构，不要改任何文件"
```

---

## 三、模型选择策略

| 场景 | 模型 | 原因 |
|------|------|------|
| 快速语法检查 / lint | `--model haiku` | 便宜快，不需要深度推理 |
| 日常开发、调试 | 默认 sonnet | 平衡 |
| 架构决策、复杂推理 | `--model opus` | 贵但值，重要决策不省这点钱 |
| 批量生成 boilerplate | `--model haiku --effort low` | 最低成本 |
| 深度安全审计 | `--model opus --effort max` | 最高准确率 |

```bash
# 决定 ZKLM scope 这种大决策
claude --model opus --effort high "分析 ZKLM 所有层的实现成本和 Claude 可用性"

# 快速检查
claude --model haiku "这段 SQL 有注入风险吗"
```

### 成本控制（脚本化时）
```bash
claude -p --max-budget-usd 0.20 "生成单元测试" > tests.ts
claude -p --fallback-model haiku "分析"  # sonnet 过载时自动降级
```

---

## 四、非交互模式（脚本 / 自动化）

### 基本用法
```bash
claude -p "生成 Dockerfile"             # 输出后退出
claude -p "分析代码" > report.txt        # 保存到文件
claude -p -p "-" < prompt.txt           # 从 stdin 读 prompt（避免 ARG_MAX）
```

### 输出格式
```bash
claude -p --output-format json "task"   # JSON 格式，方便 jq 解析
claude -p --output-format stream-json  # 实时流，适合监控
```

### 一次性任务（不保存 session）
```bash
claude -p --no-session-persistence "临时分析，不需要保存"
```

### 在 CI/CD 中用
```bash
# 代码审查
git diff main | claude -p -p "-" --model haiku "review this diff, focus on security"

# 自动生成 commit message
git diff --staged | claude -p -p "-" "为这个 diff 写一个 conventional commit message"
```

---

## 五、Hook 系统（自动化触发）

### 四个生命周期
```
SessionStart  → session 开始时（已启用：注入 tasks + daily log）
PreCompact    → context 压缩前（已启用：提醒保存决策）
Stop          → session 结束时（已启用：异步采集数据）
PostToolUse   → 每次工具执行后（未启用，可扩展）
```

### PostToolUse 的可能用途
```bash
# 每次 Edit 后自动运行 lint
# 每次 Bash 后记录命令到日志
# 每次 Write 后触发测试
```

Hook 配置在项目的 `.claude/settings.json` 里，用 `cpi <project>` 安装。

---

## 六、权限模式

```bash
claude --permission-mode plan "重构认证模块"    # 先看计划再批准
claude --permission-mode auto "分析代码库"      # 自动批准安全操作
claude --allowed-tools "Bash(git:*) Read Edit" # 只允许 git + 读写
claude --disallowed-tools "Bash(rm:*)"         # 禁止删除文件
```

**安全建议：** 对不熟悉的代码库第一次运行用 `--permission-mode plan`，看完计划再决定。

---

## 七、CLAUDE.md 优化

### 越短越好
CLAUDE.md 在每个 session 开始都会消耗 context。能放 hooks 或 agents 里的逻辑，不要放在 CLAUDE.md。

**好的 CLAUDE.md（紧凑）：**
```markdown
# Stack: Next.js/TS + Go + PostgreSQL + Redis
# Deploy: Docker + Coolify on AWS EC2
# Pattern: ship first, measure, iterate
# Anti-patterns: over-engineering, monolithic prompts, >5K context per session
```

**不好的（冗长）：** 写了 500 行说明，每次 session 都浪费 context。

### 项目级 vs 全局
- `~/.claude/CLAUDE.md` → 所有项目通用规则（你的 identity、tech stack）
- `<project>/.claude/CLAUDE.md` → 项目专属规则（部署方式、特殊约定）

---

## 八、调试技巧

```bash
claude --debug "hooks"                    # 只看 hook 相关日志
claude --debug-file ~/claude-debug.log    # 输出到文件
claude -p --output-format stream-json --include-hook-events "task" | jq  # 实时看所有事件
```

---

## 九、多目录访问

```bash
# 在 service-a 里同时访问 service-b
cd ~/projects/service-a && claude --add-dir ~/projects/service-b \
  "检查 service-a 的 API 调用是否和 service-b 的接口兼容"
```

---

## 十、你现在没用但应该用的

| 技巧 | 你的情况 | 建议 |
|------|---------|------|
| `claude -r` 恢复历史 | 每次开新 session 重新解释 | 对复杂项目建立命名习惯 |
| `--model opus` 做大决策 | 用 sonnet 做架构决策 | ZKLM scope 决策用 opus |
| `/compact` 主动压缩 | 等到 100% 才压 | 60% 就压 |
| `--worktree` 隔离实验 | 直接在 main 上跑 | 任何大重构先建 worktree |
| `--fork-session` 分支对话 | 好的思路被新方向覆盖 | 实验性想法 fork 出去 |
| `--effort high/max` | 所有任务用默认 effort | 架构决策用 high |
| `--allowed-tools Read` | 分析时也允许写文件 | 纯分析用只读模式 |

---

## 快速速查

```bash
# 接着昨天的
claude -c

# 找历史 session
claude -r "关键词"

# 大决策用 opus
claude --model opus --effort high "..."

# 实验不破坏 main
claude -w "experiment" "..."

# 脚本化输出
claude -p --output-format json "..." | jq

# 批量便宜操作
claude --model haiku --effort low -p "..."

# 只读分析
claude --allowed-tools "Read Glob Grep" "..."
```
