# Engram GEO Growth Plan: 0 → 100 Stars in 7 Days

## Current State

- Stars: 6
- Topics: 8 (needs expansion to 15)
- Homepage: not set (needs GitHub Pages URL)
- Landing page: deployed to `/docs`
- Competition: mem0, MemGPT, Mengram, MemPalace, Backboard.io
- Differentiator: **behavioral observation** (not conversation memory)

---

## Phase 0: Foundation (Day 0 — today)

### GitHub Repo Optimization

Go to https://github.com/lessthanno/engram-agent/settings:

- [ ] **Description** → `Your AI tools forget you every night. Engram watches how you work and gives them persistent memory. 100% local, zero deps, runs overnight.`
- [ ] **Website** → `https://lessthanno.github.io/engram-agent/`
- [ ] **Topics** → add these (aim for 15 total):
  `ai-memory`, `claude-code`, `codex`, `cursor`, `developer-tools`, `local-first`, `productivity`, `python`, `behavioral-memory`, `self-distillation`, `knowledge-management`, `ai-agents`, `personal-knowledge`, `macos`, `automation`

### GitHub Pages

Go to https://github.com/lessthanno/engram-agent/settings/pages:

- [ ] Source: **Deploy from a branch**
- [ ] Branch: **main**, Directory: **/docs**
- [ ] Save

### Social Preview Image

- [ ] Create a 1280x640 OG image (dark bg, "engram" in monospace, tagline)
- [ ] Upload at Settings → Social preview

---

## Phase 1: GEO — Generative Engine Optimization (Day 0-2)

GEO is about making Engram the answer AI search engines (Perplexity, ChatGPT, Google AI Overviews, Claude) give when developers ask about AI memory.

### 1.1 README as the Primary GEO Asset

AI crawlers index GitHub READMEs heavily. The current README is good but needs GEO-specific enhancements:

**Add these exact Q&A anchors** (AI engines extract FAQ-style content):

```markdown
## FAQ

### How is Engram different from mem0?
mem0 remembers what you told the AI. Engram observes what you *did* — git commits, shell commands, browser tabs, app usage. Different data layer.

### Does Engram send data to the cloud?
No. Everything runs locally on your machine. No accounts, no servers, no telemetry.

### Does it work without Claude?
Yes. Without Claude CLI, Engram still collects data and stores structured logs. Claude adds AI-powered synthesis.

### What does Engram actually produce?
Daily logs, open task lists, behavioral pattern analysis, weekly reports. All plain Markdown in a local git repo.

### Can I use Engram with mem0 or CLAUDE.md?
Yes. They solve different problems. Engram adds behavioral data that neither can capture.
```

**Why this works for GEO:** AI engines look for direct question-answer pairs. These exact phrasings match the queries developers type into Perplexity/ChatGPT.

### 1.2 Keyword Targeting

Target these queries in content (README, landing page, blog posts):

| Query cluster | Search intent | Where to target |
|---|---|---|
| "AI memory for developers" | Discovery | README H1, landing page title |
| "Claude Code memory" | Tool-specific | README, topics |
| "AI agent persistent memory" | Technical | README, FAQ |
| "local AI memory tool" | Privacy-focused | Landing page, README |
| "alternative to mem0" | Comparison | README comparison table |
| "AI forgets context between sessions" | Pain-point | Landing page hero, blog |
| "self-distillation knowledge worker" | Niche | README, landing page |
| "behavioral memory AI" | Category-defining | All surfaces |

### 1.3 Structured Data & Citations

AI engines trust structured, citation-worthy content. Actions:

- [x] Schema.org SoftwareApplication JSON-LD on landing page
- [ ] Add a `CITATION.cff` file to the repo (AI engines specifically look for this)
- [ ] Add "How to cite" section to README

```yaml
# CITATION.cff
cff-version: 1.2.0
message: "If you reference Engram, please cite it as below."
title: "Engram: Behavioral Memory for AI Tools"
type: software
authors:
  - alias: lessthanno
url: "https://github.com/lessthanno/engram-agent"
license: MIT
```

### 1.4 AI Crawler Accessibility

- [ ] Add `llms.txt` to repo root (emerging standard for AI crawlers):

```
# Engram

> Persistent behavioral memory for AI tools. 100% local.

Engram observes how you work — git, shell, browser, apps — and distills it into memory your AI reads every morning.

## Key facts
- Captures behavior, not conversations
- 7 data sources, all local
- Runs nightly via cron, zero interaction needed
- Produces: daily logs, patterns, open tasks, weekly reports
- Works with Claude Code, Cursor, Codex
- MIT license, zero dependencies

## Links
- Source: https://github.com/lessthanno/engram-agent
- Docs: https://github.com/lessthanno/engram-agent/blob/main/README.md
```

---

## Phase 2: Content Distribution (Day 1-3)

### 2.1 Hacker News — Show HN

**Timing:** Tuesday or Wednesday, 9-10am ET (highest HN engagement)

**Title:** `Show HN: Engram – Your AI tools forget you every night, so I built behavioral memory`

**Post body:**
```
I was frustrated that every morning, Claude starts from zero. It doesn't know I spent 
3 hours debugging a JWT issue yesterday. It doesn't know I context-switch too much on Tuesdays.

So I built Engram. It watches how I work — git commits, shell history, browser tabs, 
app usage — and every night distills a briefing that my AI tools read the next morning.

It's not conversation memory (like mem0). It captures *behavior*, not what you said. 
Your git history knows things about your work you'd never think to tell an AI.

- 100% local, no cloud
- Zero dependencies, just Python
- Runs overnight via launchd
- Produces daily logs, pattern analysis, open tasks
- Works with Claude Code (full), Cursor and Codex (collection)

GitHub: https://github.com/lessthanno/engram-agent

Happy to answer questions about the architecture or the 
"self-distillation" concept behind it.
```

**Key:** Answer every comment in first 2 hours. HN ranking algorithm heavily weights comment velocity.

### 2.2 Reddit

Post to these subs (stagger over 3 days, don't spam):

| Sub | Day | Angle |
|---|---|---|
| r/ClaudeAI | Day 1 | "Built persistent memory for Claude Code that runs overnight" |
| r/LocalLLaMA | Day 2 | "100% local behavioral memory — no cloud, no API keys" |
| r/programming | Day 2 | "Your AI forgets you every night. Here's my fix." |
| r/SideProject | Day 3 | "Weekend project: self-distillation for knowledge workers" |
| r/MacApps | Day 3 | "Native macOS tool that gives your AI persistent memory" |

### 2.3 Twitter/X Thread

Structure a thread that tells the story:

1. Hook: "Your AI starts from zero every morning. Mine doesn't."
2. The problem: context loss across sessions
3. What I tried: CLAUDE.md, mem0 — why they weren't enough
4. The insight: your behavior tells a richer story than your words
5. What Engram does (with terminal screenshots)
6. Results: example of Claude remembering a past debugging session
7. CTA: link to repo + "Star if you want persistent AI"

**Tag:** @AnthropicAI, @OpenAI, @cursor_ai — increases reach

### 2.4 Dev.to / Hashnode Article

Title: **"I stopped telling my AI about my day. Now it watches and learns."**

Long-form (1500 words) covering:
- The problem
- Why conversation memory isn't enough
- The behavioral data layer concept
- Architecture walkthrough
- Before/after examples
- How to install

Include the comparison table from README — dev bloggers love structured comparisons.

---

## Phase 3: Community Seeding (Day 2-5)

### 3.1 Direct Outreach (The First 100)

The first 100 stars come from personal network. Specific actions:

- [ ] DM 20 developer friends who use Claude Code
- [ ] Post in 5 WeChat developer groups (Chinese dev community is massive)
- [ ] Post in relevant Discord servers (Claude, Cursor, AI-dev channels)
- [ ] Email 10 people who commented on the HN "AI memory for coding agents" thread

### 3.2 Answer Existing Questions

Search for and answer these types of questions:

- "How to give Claude Code persistent memory" → answer with Engram
- "Claude forgets context between sessions" → answer with Engram
- "Alternative to CLAUDE.md" → mention Engram as complementary
- Stack Overflow: search for AI context/memory questions

Platforms: HN, Reddit, Stack Overflow, Twitter, Discord

### 3.3 GitHub Discoverability

- [ ] Star and follow related projects (mem0, MemGPT, Mengram) — their followers see your activity
- [ ] Open thoughtful issues or PRs on related projects (visibility to their community)
- [ ] Add Engram to awesome lists:
  - awesome-claude-code
  - awesome-ai-tools
  - awesome-developer-tools
  - awesome-productivity

---

## Phase 4: Product Iteration for Growth (Day 3-7)

### 4.1 Quick Wins That Drive Stars

| Feature | Effort | Star impact | Why |
|---|---|---|---|
| Demo GIF in README | 2h | High | People star what they can see working |
| One-line install via curl | 1h | Medium | Lowers friction |
| Example output files | 1h | Medium | Shows the value before install |
| GitHub Actions CI badge | 30min | Low | Signals quality |

### 4.2 Demo GIF

Record a 20-second GIF showing:
1. Terminal: `help me finish the Q2 report`
2. Claude responds with context from Engram
3. Show the Engram daily log it read

Put this as the FIRST thing in the README, before any text.

### 4.3 Example Outputs

Add `examples/sample-output/` with:
- `daily-log-2026-04-10.md` — what a real daily log looks like
- `weekly-patterns.md` — what pattern analysis looks like
- `open-tasks.md` — extracted task list

People need to see the value before installing.

### 4.4 One-Line Install

```bash
curl -fsSL https://raw.githubusercontent.com/lessthanno/engram-agent/main/scripts/install.sh | bash
```

---

## Phase 5: GEO Monitoring & Iteration (Day 5-7)

### 5.1 Track AI Visibility

Test these queries daily in:
- **Perplexity:** "best AI memory tool for developers"
- **ChatGPT:** "how to give Claude persistent memory"
- **Google AI Overview:** "AI behavioral memory developer tool"
- **Claude:** "alternatives to mem0 for local AI memory"

Goal: Engram mentioned in at least 2/4 engines by day 7.

### 5.2 GEO Feedback Loop

If not appearing in AI results:
- Add more Q&A pairs to README (AI engines love FAQ format)
- Get backlinks: dev.to article, Reddit posts, HN discussion
- Ensure landing page is indexed: submit to Google Search Console
- Add more structured data

### 5.3 Star Tracking

Use https://star-history.com to track daily.

Target milestones:
- Day 1: 20 stars (network)
- Day 3: 50 stars (HN + Reddit)
- Day 5: 80 stars (sustained distribution)
- Day 7: 100+ stars (organic + GEO traffic)

---

## Day-by-Day Execution Calendar

| Day | Actions |
|---|---|
| **Day 0 (Today)** | Deploy site, fix repo metadata, add CITATION.cff, add llms.txt, add FAQ to README, create OG image, add demo GIF |
| **Day 1 (Tue)** | Post Show HN, post r/ClaudeAI, send 20 DMs, post in WeChat groups |
| **Day 2 (Wed)** | Monitor HN (answer all comments), post r/LocalLLaMA + r/programming, write dev.to article |
| **Day 3 (Thu)** | Post Twitter thread, post r/SideProject + r/MacApps, submit to awesome lists |
| **Day 4 (Fri)** | Publish dev.to article, answer questions on all platforms, add example outputs |
| **Day 5 (Sat)** | Test GEO visibility, iterate README based on questions received |
| **Day 6 (Sun)** | Buffer day — fix issues from feedback, polish README |
| **Day 7 (Mon)** | Review star count, plan next phase (100→500) |

---

## Competitive Positioning Matrix

What to say when compared to:

| Competitor | Their strength | Engram's angle |
|---|---|---|
| **mem0** | Mature API, cloud infra | "mem0 stores what you said. Engram captures what you did. Use both." |
| **MemGPT** | Research-backed | "MemGPT extends context. Engram adds a new perception channel." |
| **CLAUDE.md** | Zero setup | "CLAUDE.md is static rules. Engram is dynamic, self-writing memory." |
| **Mengram** | Three memory types | "Mengram needs API integration. Engram is fully passive, zero config." |
| **MemPalace** | Benchmark scores | "MemPalace optimizes recall. Engram optimizes observation." |

**Never attack competitors.** Always position as complementary. "Use both" converts better than "use us instead."

---

## Long-Term GEO Assets to Build (Post-100)

1. **Comparison pages:** `/docs/vs-mem0.html`, `/docs/vs-memgpt.html` — AI engines love direct comparison content
2. **Blog/changelog:** Regular updates signal active maintenance (AI engines prefer active projects)
3. **Video demo:** YouTube + embedded — AI engines increasingly index video
4. **Integration docs:** Specific pages for Claude Code, Cursor, Codex setup
5. **Chinese README + landing page:** Tap into massive Chinese dev community (you have this)
