# Pet Protocol — 10-Version Roadmap

> Boil the lake. When AI makes the marginal cost near-zero, do the complete thing.

---

## v0.1 ✅ SHIPPED — Foundation
**Theme: Make it real**

- Pixel cat peeks from right edge, slides out with spring animation
- Memory-driven: reads `zihao-mind` memory files + git log → Claude generates state/message/actions
- Three modes: Claude Code (bridge), Codex (bridge), Anthropic API (direct)
- Multi-turn chat with history
- Multi-pet presence server (heartbeat/peers/leave endpoints)
- Ghost cats appear when teammates are on same page
- Bridge: Go stdlib, no external deps

---

## v0.2 🔨 NEXT — Alive & Tangible
**Theme: Make it feel like a real creature**

**3D & Visual:**
- [x] CSS perspective tilt on mouse (rotateX/Y based on cursor distance)
- [x] Float animation (sine wave, 5px up/down)
- [x] Dynamic glow by emotional state (yellow=celebrate, red=worried, blue=sleep)
- [x] Ground shadow that scales with float height
- [x] Cat portraits from jimeng in chat header

**UX bugs fixed:**
- [x] Chat messages scroll properly (`flex:1; min-height:0`)
- [x] Pet shows 40px peeking (ear tip visible) instead of 14px sliver
- [x] Retreat timer: 60s when out, no retreat on outside click, explicit × button
- [x] Hover pauses retreat timer

**New animal system:**
- [ ] Bridge `/context` returns `animal` field (cat / dog / fox / owl / raccoon)
- [ ] Pixel art for 5 animals (new sprites)
- [ ] Animal assigned based on memory personality traits at first run
- [ ] Stored in `chrome.storage.local` as permanent identity

**Deliverable:** Feels like a living creature, not a widget.

---

## v0.3 — True 3D
**Theme: Spline / Three.js integration**

- Replace canvas pixel art with a Spline 3D model embedded via `<iframe>`
- 5 3D animal models (cat, dog, fox, owl, raccoon)
- Idle/walk/jump/sleep animations in Spline
- Mouse parallax: 3D model responds to cursor position via postMessage
- State-to-animation mapping (worried = ears flat, celebrate = tail up)
- Fallback to pixel art if Spline fails to load
- Keep pixel art for ghost peers (lightweight)

**Deliverable:** First browser extension with a real 3D pet companion.

---

## v0.4 — Page Awareness
**Theme: The pet reads what you're reading**

- Content script parses current page: title, H1/H2s, selected text
- On slide-out: pet reacts to page content ("喵，你在看 GitHub PR 评论？")
- Detect page context: GitHub (shows PR stats), Notion (shows doc summary), Google Docs
- If you highlight text: pet offers to summarize/translate/explain
- Reading mode detection: long-form article → pet curls up, doesn't distract
- "Summarize this page" quick reply auto-generated

**Deliverable:** Pet knows where you are and what you're doing.

---

## v0.5 — Team Chat Layer
**Theme: Pets talk to each other**

- When 2+ pets on same page: they can "pass messages" to each other
- Your message to your pet appears as a speech bubble visible to teammates
- Ghost cats have speech bubbles showing what their owner just sent
- `/whisper @Alice hello` sends a message directly to Alice's pet
- Broadcast mode: "/shout we're shipping in 10 min" → all teammates see it
- Presence server upgraded to WebSocket for real-time delivery
- Message history persisted in bridge (last 20 messages per page)

**Deliverable:** Async team comms without leaving the page. Like Slack but in your browser corner.

---

## v0.6 — Memory Writing
**Theme: The pet learns and remembers**

- Pet can capture insights you share: "remember that we decided X"
- Bridge writes back to `zihao-mind` memory files directly
- Daily summary: at end of day, pet synthesizes what happened and writes to memory
- `/remember [fact]` quick command from chat
- Pet surfaces related memories when you visit certain pages ("上次你在这里研究了架构问题")
- Memory versioning: reads current, diffs, appends only new information

**Deliverable:** The pet grows over time. Your digital twin accumulates context.

---

## v0.7 — Task Companion
**Theme: The pet tracks what you promised**

- Extract TODOs from chat: "I need to do X" → pet adds to todo list
- Todo list stored in bridge, shown as quick-replies
- When you visit a relevant page, pet resurfaces related todos
- `/done` marks item complete, pet celebrates (ART_CELEBRATE)
- Connect to Linear/GitHub issues via bridge (read-only)
- Daily todo review: pet shows unfinished items at 9am
- Snooze: "remind me tonight" → bridge schedules a nudge

**Deliverable:** You stop losing track of what you said you'd do.

---

## v0.8 — Multi-Animal Ecosystem
**Theme: Diverse personalities, real community**

- 10 animals: cat, dog, fox, owl, raccoon, rabbit, panda, bear, penguin, dragon
- Each animal has a personality template in the system prompt
- Animal selection: personality quiz at first install (5 questions about work style)
- Or: bridge reads memory and auto-assigns ("你的记忆显示你是夜枭型" → owl)
- Each animal has unique quick-reply suggestions based on personality
- Pet marketplace: community-contributed pixel art skins (GitHub PR workflow)
- Seasonal events: holiday pixel art overlays (New Year fireworks, etc.)

**Deliverable:** Team of 5 has 5 different animal personalities — rich identity system.

---

## v0.9 — Mobile Companion
**Theme: Your pet follows you everywhere**

- Native iOS app (SwiftUI): pet lives in Dynamic Island
- Pet syncs state from browser via bridge API (same memory source)
- Push notifications from pet: "你已经连续工作4小时了"
- Tap Dynamic Island: mini chat interface
- Complication for Apple Watch: pet's face + current state
- Bridge upgrades to include `/mobile/state` endpoint
- Deep link: tap notification → opens specific page in browser

**Deliverable:** Consciousness follows you from browser to phone to watch.

---

## v1.0 — Open Ecosystem
**Theme: Anyone can build a consciousness**

**Core:**
- One-click install (packaged extension on Chrome Web Store)
- Bridge installer script: `curl | bash` setup for Claude/Codex/API
- Memory adapter: works with any markdown folder, not just zihao-mind
- Plugin SDK: third-party developers can add custom pet states and reactions

**Community:**
- Pet Protocol GitHub Org with contribution guidelines
- `pet-protocol/animals` repo: community-contributed sprites
- `pet-protocol/plugins` repo: page-specific awareness plugins (GitHub, Notion, Figma)
- Documentation site (website/index.html upgraded to full docs)

**Enterprise:**
- Team admin panel: configure which bridge URL all employees connect to
- SSO: pets linked to company identity
- Analytics: which pages your team spends the most time on (pet presence data)
- Custom animal skins per company (branded pets)

**Deliverable:** Platform, not a product. Anyone can have a consciousness in their browser.

---

## Version Themes Summary

| Version | Theme | Key Unlock |
|---------|-------|-----------|
| v0.1 | Foundation | It exists |
| v0.2 | Alive | It feels real |
| v0.3 | 3D | It looks stunning |
| v0.4 | Page-aware | It knows where you are |
| v0.5 | Team layer | Your pets talk |
| v0.6 | Memory writing | It grows with you |
| v0.7 | Task companion | It remembers your promises |
| v0.8 | Ecosystem | Rich identity system |
| v0.9 | Mobile | Always with you |
| v1.0 | Platform | Anyone can use it |

---

## Immediate Next (v0.2 scope, this sprint)

1. [ ] Test 3D tilt + float in browser (reload extension)
2. [ ] Verify jimeng portrait shows in chat header
3. [ ] Test multi-pet with 2 browser tabs on same page
4. [ ] Add 5 animal pixel arts to STATE_ART
5. [ ] Bridge `/context` response includes `animal` field
6. [ ] Ship to GitHub as public repo
