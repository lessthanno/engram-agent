<div align="center">

# Engram

**你的 AI 工具每天晚上都会忘掉一切。Engram 解决这个问题。**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://apple.com/macos)
[![Zero deps](https://img.shields.io/badge/依赖-零-brightgreen.svg)](#环境要求)
[![Claude Code](https://img.shields.io/badge/Claude_Code-完整支持-orange.svg)](https://claude.ai/code)

*知识工作者的自我蒸馏系统。每晚自动运行。没有任何按钮需要点击。*

[快速开始](#快速开始) · [工作原理](#工作原理) · [技能扩展](#技能系统----扩展-engram) · [隐私说明](#隐私----不可妥协) · [English](README.md)

</div>

---

## 有无 Engram 的对比

**没有 Engram —— 每天早上都是这样：**

```
你：    帮我把 Q2 报告写完
Claude：好的！这份报告是关于什么的？格式要求？
        目前做到哪里了？受众是谁？
        （回答一遍上周已经回答过的问题）
```

**有了 Engram：**

```
你：    帮我把 Q2 报告写完
Claude：你上周四开始起草这份报告。营收部分已经完成。
        客户流失分析还没做 —— 你当时备注说数据源
        可能有问题。要不要我直接从最新的仪表盘拉数据？
```

**它发现你自己没注意到的事：**

```
[本周行为分析]

你周二在 8 个项目之间来回切换。
在切换次数 ≤3 的日子里，你的产出是平时的 2.4 倍。
你最近三个高产日，都是先花 2 小时专注工作，然后才开始处理其他事。
```

**它记住你忘掉的事：**

```
你：    部署一直因为那个 auth 报错失败……
Claude：你 3 月 15 日遇到过完全一样的问题。根本原因是
        一个配置错误的环境变量。修复在 deploy.yaml 第 47 行 ——
        检查一下是不是有人把它 revert 掉了。
```

---

## Engram 和其他工具的区别

> *"这不就是 mem0 / MemGPT / 一个 CLAUDE.md 文件吗？"*

不是。它们在完全不同的层面解决不同的问题。

### 本质差异

大多数「AI 记忆」工具工作在**对话内部** —— 它们记住你*对 AI 说了什么*。

Engram 工作在**对话外部** —— 它观察你*在电脑上做了什么*。

这是完全不同的数据层。

```
mem0 / MemGPT / 对话记忆：

  你告诉 Claude "我叫 Alex"
       │
       ▼
  工具存储："用户名叫 Alex"
       │
       ▼
  下次会话：Claude 知道你的名字

─────────────────────────────────────────────

Engram：

  你在 VS Code 里工作了 3 小时，向 auth.ts
  提交了 7 次代码，跑了 4 次测试，然后打开
  了 12 个关于 JWT refresh token 的浏览器标签
       │
       ▼
  Engram 捕获：你实际做了什么
       │
       ▼
  Claude 综合分析：「你在调试 JWT refresh 的问题。
  测试还在失败。你已经在这上面花了 3 小时 ——
  问题很可能在 auth.ts 第 142 行的 token 过期逻辑。」
```

你没有告诉 Claude 任何这些信息。Engram 从你的行为里推断出来的。

### 横向对比

| | Engram | mem0 / MemGPT | CLAUDE.md |
|---|---|---|---|
| **捕获什么** | 你的真实行为（git、应用、文件、终端、浏览器）| 你主动告诉 AI 的内容 | 你手动写的内容 |
| **工作方式** | 被动观察，每晚自动运行 | 主动拦截 AI 对话 | 静态文件，需要手动维护 |
| **需要你主动输入？** | 不需要，全自动 | 需要（正常和 AI 对话即可）| 需要（自己写并持续更新）|
| **数据来源** | 操作系统级别的活动 | 对话内容 | 你自己的笔记 |
| **能发现你没注意到的规律？** | 能 | 不能 | 不能 |
| **能识别你的短板？** | 能 | 不能 | 只有你自己写进去才有 |
| **跨 AI 工具？** | 能 —— 一份记忆，所有工具共享 | 通常绑定特定工具 | 绑定特定工具 |
| **本地/隐私？** | 100% 本地，无云端 | 通常依赖云端 | 本地 |
| **维护成本** | 装一次，再也不用管 | 需要 API 集成 | 需要持续手动维护 |

### 各自适合的场景

**用 mem0 / MemGPT，如果**：你想让 AI 记住你明确分享过的信息 —— 你的名字、偏好、项目名称、重复过的指令。

**用 CLAUDE.md，如果**：你想编码静态规则、代码规范，或者不常变化的项目背景信息。

**用 Engram，如果**：你想让 AI 理解你*真正的工作方式* —— 你的节奏、你反复犯的错、你一直没完成的线头、你自己看不见的行为规律。

它们解决的是不同的问题。很多人同时用这三种。

### Engram 背后的洞察

大多数自称「AI 记忆」的工具，实际上解决的问题比它们看起来更窄：它们是在跨会话扩展有效上下文窗口，以语言为媒介。

Engram 增加的是一个全新的*感知通道* —— 完全不经过语言。你的 git 历史知道你工作中的事，是你永远不会想到要说的。你的命令行透露了你没有说出口的优先级。你的应用使用模式暴露了你自己没注意到的习惯。

**关于你工作方式最诚实的记录，不是你汇报的内容 —— 而是你做了什么。**

---

## 工作原理

可以理解为一本 **自动书写的日记** —— 你的 AI 每天早上自动阅读。

```
                    你正常工作
                        |
                        v
               Engram 安静地观察
          （git 提交、AI 会话、命令行历史、
           浏览器标签页、应用使用 —— 7 个来源）
                        |
                        v
              每晚 23:45，Claude
           分析所有原始数据，蒸馏出个人简报：
                        |
          +-------------+-------------+
          |             |             |
      今天做了什么   行为模式     明天的待办
                    和薄弱点
          |             |             |
          +-------------+-------------+
                        |
                        v
            第二天早上，你的 AI 工具
            自动读取简报。了解你。
            循环往复。你被一天天蒸馏。
```

**就是这样。** 不用看仪表盘。不用写笔记。不用点任何按钮。

---

## 快速开始

三条命令，两分钟。

```bash
git clone https://github.com/lessthanno/engram-agent.git ~/engram-agent
cd ~/engram-agent
bash scripts/install.sh
```

安装程序会问 3 个问题（记忆存在哪里、你的邮箱、扫描哪些文件夹），然后自动搞定一切。

安装完成后，**你不需要做任何事。** Engram 自己运行。

---

## 收集什么

Engram 从 7 个来源收集上下文 —— 全部在本地，数据不会离开你的电脑：

| 来源 | 收集内容 |
|------|---------|
| **AI 会话** | 你和 Claude / Cursor / Codex 讨论了什么 |
| **Git 活动** | 你改了什么代码，效率如何 |
| **命令行历史** | 你执行了什么命令（密码自动脱敏） |
| **浏览器标签页** | 你在研究什么 |
| **应用使用** | 你在哪些应用上花了时间 |
| **最近文件** | 你打开了什么文档 |
| **系统状态** | 正在运行的进程、活跃的项目 |

不是程序员？没关系 —— 浏览器标签页、应用使用、最近文件和 AI 会话能捕捉到任何类型的工作。

---

## 产出什么

每天晚上，Claude 分析你的一天，输出：

| 产出 | 用途 |
|------|------|
| **日志** | 今天做了什么的完整记录 |
| **待办事项** | 从会话中提取的未完成工作 |
| **行为模式** | 行为趋势（比如"上午效率最高"、"周三调研最多"） |
| **薄弱点** | 反复出现的问题（比如"频繁切换上下文"、"任务总是做到 80% 就放下"） |
| **周报** | 过去 7 天的趋势 |

全部以 Markdown 文件存储在本地 git 仓库中。人类可读。有版本历史。完全属于你。

---

## 支持的工具

| 工具 | 状态 |
|------|------|
| **Claude Code** | 完整支持 —— 读取会话、写回上下文、hooks 已安装 |
| **Codex** | 收集会话数据，写回功能即将支持 |
| **Cursor** | 收集会话数据，写回功能即将支持 |

未安装的工具会被自动跳过，不会报错。

---

## 隐私 —— 不可妥协

- **100% 本地。** 数据永远不会离开你的电脑。
- **无云端。** 无账号。无服务器。无订阅。
- **无遥测。** 我们不追踪任何信息，连匿名统计都没有。
- **密码脱敏。** API 密钥、token、密码会从收集的数据中自动移除。
- **你拥有一切。** 纯文件存在 git 仓库里。随时可以删除。

---

## 查询你的记忆

Engram 运行后，你可以在任何 Claude Code 会话中查询自己的历史：

```
> @memory-analyst 上周二我在做什么？
> @memory-analyst 我之前遇到过这个问题吗？
> @memory-analyst 我当前的待办事项是什么？
> @memory-analyst 这周我表现出什么模式？
```

就像和一个替你做笔记的"自己"对话。

---

## 技能系统 -- 扩展 Engram

Engram 内置技能系统。你可以添加自定义的采集器、合成器或桥接器，无需修改核心代码。

### 创建技能

在 `~/.mind/skills/` 下放一个文件夹，包含两个文件：

```
~/.mind/skills/my-collector/
  SKILL.md      # 元数据（名称、类型、描述）
  skill.py      # 你的 Python 代码
```

### SKILL.md 格式

```yaml
---
name: notion-collector
description: Collects today's Notion page edits
type: collector          # collector | synthesizer | bridge
entry: skill.py          # 可选，默认 skill.py
function: collect        # 可选，根据类型自动设定
enabled: true            # 可选，默认 true
---
```

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | 是 | -- | 技能唯一标识符（字母、数字、连字符） |
| `type` | 是 | -- | `collector`、`synthesizer` 或 `bridge` |
| `description` | 否 | -- | 技能功能描述 |
| `entry` | 否 | `skill.py` | 包含函数的 Python 文件 |
| `function` | 否 | 根据类型 | 要调用的函数名（见下表） |
| `enabled` | 否 | `true` | 可在 `config.toml` 中覆盖 |

### 函数签名

| 类型 | 默认函数名 | 签名 |
|------|-----------|------|
| collector | `collect` | `collect(today: str) -> dict` |
| synthesizer | `synthesize` | `synthesize(raw: dict, analysis_dir: Path)` |
| bridge | `bridge` | `bridge(analysis_dir: Path)` |

- **采集器 (collector)** 接收 ISO 日期字符串（如 `"2026-04-10"`），返回采集数据的 dict，合并到原始数据管道中。
- **合成器 (synthesizer)** 接收完整的原始数据 dict 和分析目录路径，将合成文件（如 `tasks.md`、`patterns.md`）写入该目录。
- **桥接器 (bridge)** 接收分析目录路径，将合成结果推送到外部系统（如 Obsidian、Notion）。

可以通过 SKILL.md 中的 `function` 字段覆盖默认函数名：

```yaml
---
name: my-collector
type: collector
function: my_custom_collect
---
```

### 配置

在 `~/.mind/config.toml` 中配置技能参数：

```toml
[skills.notion-collector]
api_key = "ntn_xxxxx"
database_ids = ["abc123"]
```

在技能代码中访问配置：

```python
import config as cfg

skill_cfg = cfg.skill_config("notion-collector")
api_key = skill_cfg.get("api_key", "")
```

配置优先级（从高到低）：
1. 环境变量（`MIND_SKILLS_NOTION_COLLECTOR_API_KEY`）
2. `~/.mind/config.toml`
3. 代码中的默认值

#### 全局开关

一键禁用所有技能：

```toml
[skills]
enabled = false
```

或通过 config 禁用单个技能（覆盖 SKILL.md 中的设置）：

```toml
[skills.notion-collector]
enabled = false
```

### 容错机制

技能系统默认容错。如果任何技能在发现、加载或执行阶段出错，Engram 会记录警告并继续正常运行。一个损坏的技能永远不会导致主流程崩溃。

### 示例技能

包含在 [`examples/skills/`](./examples/skills/) 中：

- **notion-collector** -- 通过 API 采集 Notion 页面编辑记录
- **obsidian-bridge** -- 将每日洞察写入 Obsidian 日记

### 自动发现

技能在运行时自动发现。不需要注册 —— 把文件夹放到 `~/.mind/skills/` 就能用。

---

## 环境要求

- **macOS**（Linux 和 Windows 支持即将到来）
- **Python 3.10+**（你的 Mac 上已经有了，不需要额外安装）
- **Claude CLI** 用于 AI 分析（可选 —— 没有它也能用，只是没那么智能）

零外部依赖。不需要 `pip install`。不需要 `npm`。不需要 Docker。只要 Python。

---

## 卸载

```bash
bash scripts/uninstall.sh
```

移除所有组件，但保留你的记忆仓库。你的数据永远不会被删除。

---

## 贡献

代码库刻意保持简单 —— 纯 Python，无框架，无构建步骤。

欢迎贡献的方向：
- **Linux / Windows 支持**
- **更多 AI 工具集成**（VS Code、JetBrains、Warp）
- **本地仪表盘** 可视化浏览你的历史
- **团队模式** 匿名分享团队行为洞察

---

## 许可证

MIT

---

<p align="center">
  <sub>由 <a href="https://github.com/lessthanno">@lessthanno</a> 构建。<br>你的 AI 应该从你身上学习，而不是每次都从头开始。</sub>
</p>
