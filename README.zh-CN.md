<p align="center">
  <h1 align="center">Engram</h1>
  <p align="center">
    <strong>知识工作者的自我蒸馏系统。<br>你的 AI 工具记得你是谁 —— 因为每晚，你都在自动告诉它们。</strong>
  </p>
  <p align="center">
    <a href="#问题">问题</a> &bull;
    <a href="#快速开始">快速开始</a> &bull;
    <a href="#工作原理">工作原理</a> &bull;
    <a href="./README.md">English</a> &bull;
    <a href="https://github.com/lessthanno/engram-agent/issues">Issues</a>
  </p>
</p>

---

## 问题

想象一下，你雇了一个天才助理，但他每晚都会失忆。

每天早上你走进办公室，他问你：*"你好，你是谁？我们在做什么？"* 你把所有事情重新解释一遍。他干得很好。然后下班，忘掉一切，第二天重来。

**今天的 AI 工具就是这样。** Claude Code、Cursor、Codex、ChatGPT —— 能力超强，但每次对话都从零开始。不记得昨天的决策，不了解你的习惯，没有任何连续性。

**Engram 让它们记住你。**

它在后台安静运行，观察你每天的工作 —— 写代码、写文档、做调研、开会，什么都行。到了晚上，它把你的原始活动蒸馏成结构化的洞察：你做了什么、你怎么工作、你在哪里卡住、还有什么没做完。第二天早上，你的 AI 工具已经了解你。

这不是一个程序员专用工具。这是**给所有和 AI 协作的人做的自我蒸馏系统。**

不需要云端。不需要配置。不需要维护。AI 每天都更懂你。

---

## 有什么不同

**没有 Engram —— 每天早上：**
```
你：     帮我把 Q2 报告写完
Claude： 好的！报告是关于什么的？你要什么格式？
         （问了 10 个你上周已经回答过的问题）
```

**有了 Engram —— 每天早上：**
```
你：     帮我把 Q2 报告写完
Claude： 你上周四开始写 Q2 报告了。收入部分已经写完，
         但流失分析还没做完。你当时记录说数据源不太可靠 ——
         要不要我换成更新后的仪表盘数据？
```

**它能发现你自己注意不到的事：**
```
[来自每日分析]

你昨天在 8 个项目之间切换。
切换少于 3 次的日子，你的产出高 2.4 倍。
建议：先集中 2 小时处理最重要的事，再打开其他项目。
```

**它记得你忘掉的事：**
```
你：     部署又报那个认证错误了...
Claude： 你 3 月 15 日修过一模一样的问题。原因是环境变量配置错误。
         修复在 deploy.yaml 第 47 行。看看是不是有人把那个改动回滚了。
```

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

**创建一个技能：**
```
~/.mind/skills/my-collector/
  SKILL.md      # 元数据（名称、类型、描述）
  skill.py      # 你的 Python 代码
```

**SKILL.md 格式：**
```yaml
---
name: notion-collector
description: Collects today's Notion page edits
type: collector          # collector | synthesizer | bridge
entry: skill.py
enabled: true
---
```

**不同类型的函数签名：**

| 类型 | 函数签名 |
|------|---------|
| collector | `collect(today: str) -> dict` |
| synthesizer | `synthesize(raw: dict, analysis_dir: Path)` |
| bridge | `bridge(analysis_dir: Path)` |

**在 `~/.mind/config.toml` 中配置技能参数：**
```toml
[skills.notion-collector]
api_key = "ntn_xxxxx"
database_ids = ["abc123"]
```

**示例技能**在 [`examples/skills/`](./examples/skills/)：
- **notion-collector** -- 采集 Notion 页面编辑记录
- **obsidian-bridge** -- 将每日洞察写入 Obsidian 日记

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
