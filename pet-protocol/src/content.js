// Pet Protocol v7 — Memory-driven consciousness + Multi-pet presence
// State emerges from zihao-mind memory. Ghost cats appear when teammates are on same page.

// ─── Palette & Pixel Art ──────────────────────────────────────────────────────
const P = {
  '.': null,
  'W': '#F0F0F0', 'G': '#CCCCCC', 'K': '#222222',
  'P': '#FFB3C6', 'B': '#111111', 'H': '#FF6B8A',
  'Z': '#A8D8EA', 'Y': '#FFE066', 'T': '#8BC34A',
  'S': '#1A1A1A', 'L': '#444444', 'O': '#E8A87C', 'N': '#7A4F2A',
  'g': '#888888', 'b': '#333333', 'o': '#CC7744', 'w': '#DDDDDD',
};
const PX = 4, SZ = 64;
const px = s => s.split('');

const ART_PEEK = [
  [px('................'), px('........KK......'), px('.......KWWK.....'), px('.......KPWK.....'),
   px('KKKKKKKWWWWK....'), px('WWWWWWWWWWWK....'), px('WWWWBWWWWWWK....'), px('WWWWWPWWWWWK....'),
   px('WWWWWWWWWWWK....'), px('KWWWWWWWWWWK....'), px('KKWWWWWWWWKK....'), px('..KKKKKKKK......'),
   px('................'), px('................'), px('................'), px('................')],
  [px('................'), px('........KK......'), px('.......KWWK.....'), px('.......KPWK.....'),
   px('KKKKKKKWWWWK....'), px('WWWWWWWWWWWK....'), px('WWWWGGWWWWWK....'), px('WWWWWPWWWWWK....'),
   px('WWWWWWWWWWWK....'), px('KWWWWWWWWWWK....'), px('KKWWWWWWWWKK....'), px('..KKKKKKKK......'),
   px('................'), px('................'), px('................'), px('................')],
  [px('................'), px('........KK......'), px('.......KWWK.....'), px('.......KPWK.....'),
   px('KKKKKKKWWWWK....'), px('WWWWWWWWWWWK....'), px('WWWBWWWWWWWK....'), px('WWWWWPWWWWWK....'),
   px('WWWWWWWWWWWK....'), px('KWWWWWWWWWWK....'), px('KKWWWWWWWWKK....'), px('..KKKKKKKK......'),
   px('................'), px('................'), px('................'), px('................')],
];

const ART_IDLE = [
  [px('................'), px('....KK..KK......'), px('...KWWK.KWWK....'), px('...KPWKKPWWK....'),
   px('...KWWWWWWWK....'), px('....KWWWWWWK....'), px('....KWWBWBWK....'), px('....KWWWPWWK....'),
   px('....KWWWWWWK....'), px('...KWWWWWWWK....'), px('...KWWWWWWWK....'), px('...KWWWWWWWK....'),
   px('....KKKKKKK.....'), px('................'), px('................'), px('................')],
  [px('................'), px('....KK..KK......'), px('...KWWK.KWWK....'), px('...KPWKKPWWK....'),
   px('...KWWWWWWWK....'), px('....KWWWWWWK....'), px('....KWWgggWK....'), px('....KWWWPWWK....'),
   px('....KWWWWWWK....'), px('...KWWWWWWWK....'), px('...KWWWWWWWK....'), px('...KWWWWWWWK....'),
   px('....KKKKKKK.....'), px('................'), px('................'), px('................')],
];

const ART_JUMP = [
  [px('................'), px('....KK..........'), px('...KWWK.....KK..'), px('...KPWK....KWWK.'),
   px('...KWWWWWWWWWWK.'), px('....KWWWWWWWWWK.'), px('....KWWbWbWWWK..'), px('....KWWWPWWWK...'),
   px('....KWWWWWWK....'), px('...KWWWWWWWK....'), px('..KWWWWWWWWK....'), px('..KKKWWWWKKK....'),
   px('.....KKKKK......'), px('................'), px('................'), px('................')],
  [px('....H...........'), px('................'), px('....KK..KK......'), px('...KWWK.KWWK....'),
   px('...KPWKKPWWK....'), px('...KWWWWWWWK....'), px('....KWWbWbWK....'), px('....KWWWHWWK....'),
   px('....KWWWWWWK....'), px('...KWWWWWWWK....'), px('..KWWWWWWWWK....'), px('...KKKWWWKKK....'),
   px('.....KKKKK......'), px('................'), px('................'), px('................')],
];

const ART_SLEEP = [
  [px('................'), px('................'), px('....KKKKK.......'), px('...KWWWWWK......'),
   px('..KWWWWWWWK.....'), px('.KWWKKggWWK.....'), px('.KWWWWWWWWK.....'), px('.KWWWWWWWWK.....'),
   px('..KWWWWWWWK.....'), px('..KKKWWWKKK.....'), px('.....KKK........'), px('..........Z.....'),
   px('................'), px('................'), px('................'), px('................')],
  [px('................'), px('................'), px('....KKKKK.......'), px('...KWWWWWK......'),
   px('..KWWWWWWWK.....'), px('.KWWKKggWWK.....'), px('.KWWWWWWWWK.....'), px('.KWWWWWWWWK.....'),
   px('..KWWWWWWWK.....'), px('..KKKWWWKKK.....'), px('.....KKK........'), px('.......Z.Z......'),
   px('..........Z.....'), px('................'), px('................'), px('................')],
];

const ART_HUNGRY = [
  [px('................'), px('....KK..KK......'), px('...KWWK.KWWK....'), px('...KPWKKPWWK....'),
   px('...KWWWWWWWK....'), px('....KWWWWWWK....'), px('....KWWgWgWK....'), px('....KWWWOWWK....'),
   px('....KWWWWWWK....'), px('...KWWKWWWWK....'), px('...KWWKWWWWK....'), px('...KWWWWWWWK....'),
   px('....KKKKKKK.....'), px('................'), px('................'), px('................')],
  [px('................'), px('....KK..KK......'), px('...KWWK.KWWK....'), px('...KPWKKPWWK....'),
   px('...KWWWWWWWK....'), px('....KWWWWWWK....'), px('....KWWgWgWK....'), px('....KWWWoWWK....'),
   px('....KWWWWWWK....'), px('...KWWWKWWWK....'), px('...KWWWKWWWK....'), px('...KWWWWWWWK....'),
   px('....KKKKKKK.....'), px('................'), px('................'), px('................')],
];

const ART_WORRIED = [
  [px('................'), px('....KK..KK......'), px('...KWWK.KWWK....'), px('...KPWKKPWWK....'),
   px('...KWWWWWWWK....'), px('....KWWWWWWK....'), px('....KWWbWbWK....'), px('....KWWWwWWK....'),
   px('....KWWWWWWK....'), px('...KWWWWWWWK....'), px('...KWWwWwWWK....'), px('...KWWWWWWWK....'),
   px('....KKKKKKK.....'), px('......H.........'), px('................'), px('................')],
  [px('................'), px('....KK..KK......'), px('...KWWK.KWWK....'), px('...KPWKKPWWK....'),
   px('...KWWWWWWWK....'), px('....KWWWWWWK....'), px('....KWWbWbWK....'), px('....KWWWwWWK....'),
   px('....KWWWWWWK....'), px('...KWWWWWWWK....'), px('...KWWWWWWWWK...'), px('...KWWWWWWWK....'),
   px('....KKKKKKK.....'), px('...H............'), px('................'), px('................')],
];

// Celebrate: spinning/happy
const ART_CELEBRATE = [
  [px('................'), px('.....KK.KK......'), px('....KWWKKWWK....'), px('....KPWWWPWK....'),
   px('....KWWWWWWK....'), px('.....KWWWWK.....'), px('.....KWbWbK.....'), px('.....KWWHWK.....'),
   px('...HKWWWWWWKH...'), px('....KWWWWWWK....'), px('....KWWWWWWK....'), px('....KKKKKKK.....'),
   px('................'), px('................'), px('................'), px('................')],
  [px('...H............'), px('.....KK.KK......'), px('....KWWKKWWK....'), px('....KPWWWPWK....'),
   px('....KWWWWWWK....'), px('.....KWWWWK.....'), px('.....KWbWbK.....'), px('.H...KWWHWK.....'),
   px('....KWWWWWWK....'), px('....KWWWWWWK.H..'), px('....KKKKKKK.....'), px('................'),
   px('................'), px('................'), px('................'), px('................')],
];

const STATE_ART   = { peek: ART_PEEK, idle: ART_IDLE, jump: ART_JUMP, sleep: ART_SLEEP, hungry: ART_HUNGRY, worried: ART_WORRIED, celebrate: ART_CELEBRATE, rest: ART_SLEEP, insight: ART_IDLE, reminder: ART_WORRIED };
const STATE_SPEED = { peek: 1800, idle: 2200, jump: 180, sleep: 1100, hungry: 700, worried: 500, celebrate: 150 };

// Pet color filters by type
const PET_FILTER = {
  white:  'drop-shadow(-2px 2px 5px rgba(0,0,0,0.4))',
  black:  'brightness(0.25) contrast(2.5) drop-shadow(-2px 2px 5px rgba(0,0,0,0.5))',
  orange: 'sepia(1) saturate(3) hue-rotate(340deg) drop-shadow(-2px 2px 5px rgba(0,0,0,0.4))',
};

// Ghost filters for teammates (tinted differently from owner's pet)
const GHOST_HUES = [200, 280, 60, 160, 320]; // hue rotation per peer slot

function render(ctx, grid) {
  ctx.clearRect(0, 0, SZ, SZ);
  for (let r = 0; r < 16; r++)
    for (let c = 0; c < 16; c++) {
      const color = P[grid[r]?.[c]];
      if (color) { ctx.fillStyle = color; ctx.fillRect(c * PX, r * PX, PX, PX); }
    }
}

// ─── Main ─────────────────────────────────────────────────────────────────────
async function init() {
  document.getElementById('pp-root')?.remove();
  document.getElementById('pp-chat')?.remove();
  document.querySelectorAll('.pp-ghost').forEach(el => el.remove());

  const cfg      = await chrome.storage.sync.get(['petType', 'petName', 'agent_mode']).catch(() => ({}));
  const catType  = cfg.petType    || 'white';
  const petName  = cfg.petName    || 'Mochi';
  const agentMode = cfg.agent_mode || 'api';

  // ── Unique user ID (persisted) ────────────────────────────────────────────
  const myId = await (async () => {
    const d = await chrome.storage.local.get('pp_uid').catch(() => ({}));
    if (d.pp_uid) return d.pp_uid;
    const id = Math.random().toString(36).slice(2, 10);
    chrome.storage.local.set({ pp_uid: id }).catch(() => {});
    return id;
  })();

  const pageUrl = location.hostname + location.pathname.slice(0, 30);

  let state    = 'peek';
  let frameIdx = 0;
  let out      = false;
  let chatOpen = false;
  let retreatTimer = null;
  let petContext   = null;

  // ── DOM: root + canvas (my pet) ───────────────────────────────────────────
  const root = document.createElement('div');
  root.id = 'pp-root';
  Object.assign(root.style, {
    position: 'fixed', bottom: '120px', right: `-${SZ - 14}px`,
    zIndex: '2147483647', cursor: 'pointer',
    transition: 'right 0.35s cubic-bezier(0.34,1.56,0.64,1)',
    display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px',
    userSelect: 'none',
  });

  const canvas = document.createElement('canvas');
  canvas.width = SZ; canvas.height = SZ;
  Object.assign(canvas.style, {
    imageRendering: 'pixelated', display: 'block',
    filter: PET_FILTER[catType] || PET_FILTER.white,
  });
  const ctx = canvas.getContext('2d');

  const strip = document.createElement('div');
  Object.assign(strip.style, {
    display: 'none', fontSize: '8px', fontFamily: 'monospace',
    color: '#666', textAlign: 'right', paddingRight: '2px',
  });

  root.appendChild(strip);
  root.appendChild(canvas);
  document.body.appendChild(root);

  // ── DOM: chat popup ───────────────────────────────────────────────────────
  const chat = document.createElement('div');
  chat.id = 'pp-chat';
  Object.assign(chat.style, {
    position: 'fixed', bottom: '200px', right: '16px',
    width: '300px', zIndex: '2147483647',
    background: 'rgba(10,10,18,0.96)',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: '14px', padding: '14px',
    backdropFilter: 'blur(20px)',
    boxShadow: '0 16px 48px rgba(0,0,0,0.7)',
    display: 'none', flexDirection: 'column', gap: '10px',
    fontFamily: 'monospace',
  });
  document.body.appendChild(chat);

  const msgs = document.createElement('div');
  Object.assign(msgs.style, {
    maxHeight: '200px', overflowY: 'auto',
    display: 'flex', flexDirection: 'column', gap: '6px',
    fontSize: '11px', lineHeight: '1.6',
  });

  const chatHistory = [];

  function addMsg(text, role = 'pet') {
    const d = document.createElement('div');
    const isUser = role === 'user';
    const isPet  = role === 'pet';
    Object.assign(d.style, {
      padding: '6px 10px', borderRadius: '10px', maxWidth: '92%',
      alignSelf: isUser ? 'flex-end' : 'flex-start',
      background: isUser ? 'rgba(168,216,234,0.15)' : role === 'system' ? 'transparent' : 'rgba(255,255,255,0.06)',
      color: role === 'system' ? '#444' : '#ddd',
      fontSize: '11px', lineHeight: '1.6',
      borderTopLeftRadius: isPet ? '4px' : '10px',
      borderTopRightRadius: isUser ? '4px' : '10px',
    });
    d.textContent = text;
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
    return d;
  }

  const quickReplies = document.createElement('div');
  Object.assign(quickReplies.style, { display: 'flex', flexWrap: 'wrap', gap: '5px' });

  function setQuickReplies(actions = []) {
    quickReplies.innerHTML = '';
    actions.forEach(a => {
      const btn = document.createElement('button');
      btn.textContent = a.label;
      Object.assign(btn.style, {
        background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: '20px', padding: '4px 10px',
        cursor: 'pointer', fontSize: '10px', color: '#bbb', transition: 'all 0.15s',
      });
      btn.onmouseenter = () => { btn.style.background = 'rgba(168,216,234,0.15)'; btn.style.color = '#a8d8ea'; };
      btn.onmouseleave = () => { btn.style.background = 'rgba(255,255,255,0.07)'; btn.style.color = '#bbb'; };
      btn.addEventListener('click', e => {
        e.stopPropagation();
        quickReplies.innerHTML = '';
        sendMessage(a.prompt);
      });
      quickReplies.appendChild(btn);
    });
  }

  const inputRow = document.createElement('div');
  Object.assign(inputRow.style, { display: 'flex', gap: '6px' });

  const input = document.createElement('input');
  input.placeholder = '说点什么...';
  Object.assign(input.style, {
    flex: '1', background: 'rgba(255,255,255,0.06)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '8px', padding: '7px 10px',
    color: '#fff', fontSize: '11px', fontFamily: 'monospace', outline: 'none',
  });

  const sendBtn = document.createElement('button');
  sendBtn.textContent = '↑';
  Object.assign(sendBtn.style, {
    background: '#a8d8ea', color: '#111', border: 'none',
    borderRadius: '8px', padding: '7px 10px',
    cursor: 'pointer', fontWeight: 'bold', fontSize: '13px',
  });

  async function sendMessage(text) {
    const val = (text || input.value).trim();
    if (!val) return;
    if (!text) input.value = '';
    addMsg(val, 'user');
    chatHistory.push({ role: 'user', content: val });
    const t = addMsg('...', 'pet');
    clearTimeout(retreatTimer);
    try {
      if (!chrome.runtime?.id) throw new Error('context invalidated');
      const res = await chrome.runtime.sendMessage({
        type: 'AGENT_COMMAND', command: val,
        history: chatHistory.slice(-10, -1),
      });
      const reply = res?.result || '...';
      t.remove(); addMsg(reply, 'pet');
      chatHistory.push({ role: 'assistant', content: reply });
    } catch (e) {
      t.remove();
      addMsg(e.message?.includes('invalidated') ? '扩展已更新，请刷新页面' : '需要先配置 agent', 'system');
    }
  }

  sendBtn.addEventListener('click', () => sendMessage());
  input.addEventListener('keydown', e => { e.stopPropagation(); if (e.key === 'Enter') sendMessage(); });
  input.addEventListener('keyup',   e => e.stopPropagation());
  input.addEventListener('keypress',e => e.stopPropagation());

  inputRow.append(input, sendBtn);
  chat.append(msgs, quickReplies, inputRow);

  // ── State helpers ─────────────────────────────────────────────────────────
  function setState(s) { state = s; frameIdx = 0; }

  function slideOut(greeting, actions) {
    if (out) {
      if (greeting) { openChat(); addMsg(greeting, 'pet'); if (actions) setQuickReplies(actions); }
      return;
    }
    out = true;
    root.style.right = '10px';
    strip.style.display = 'block';
    clearTimeout(retreatTimer);
    setState('jump');
    setTimeout(() => {
      setState('idle');
      if (greeting) {
        openChat();
        addMsg(greeting, 'pet');
        if (actions) setQuickReplies(actions);
      }
      retreatTimer = setTimeout(slideBack, 20000);
    }, ART_JUMP.length * STATE_SPEED.jump + 100);
  }

  function slideBack() {
    if (!out) return;
    if (chatOpen) { retreatTimer = setTimeout(slideBack, 5000); return; }
    out = false;
    root.style.right = `-${SZ - 14}px`;
    strip.style.display = 'none';
    setState('peek');
  }

  function openChat() {
    chatOpen = true;
    chat.style.display = 'flex';
    clearTimeout(retreatTimer);
    setTimeout(() => input.focus(), 60);
  }

  function closeChat() {
    chatOpen = false;
    chat.style.display = 'none';
    quickReplies.innerHTML = '';
    retreatTimer = setTimeout(slideBack, 8000);
  }

  // ── Click / Hover ─────────────────────────────────────────────────────────
  root.addEventListener('click', e => {
    e.stopPropagation();
    clearTimeout(retreatTimer);
    if (!out) {
      fetchContextAndSlideOut();
    } else if (chatOpen) {
      closeChat();
    } else {
      openChat();
    }
  });
  root.addEventListener('mouseenter', () => { if (!out) root.style.right = `-${SZ - 28}px`; });
  root.addEventListener('mouseleave', () => { if (!out) root.style.right = `-${SZ - 14}px`; });

  document.addEventListener('click', e => {
    if (chatOpen && !chat.contains(e.target) && !root.contains(e.target)) closeChat();
  });

  // ── Context fetch ─────────────────────────────────────────────────────────
  async function fetchContext() {
    try {
      const res = await fetch('http://localhost:19099/context', { signal: AbortSignal.timeout(8000) });
      if (!res.ok) return null;
      return await res.json();
    } catch { return null; }
  }

  async function fetchContextAndSlideOut(prefetchedCtx) {
    const JUMP_MS = ART_JUMP.length * STATE_SPEED.jump + 150;
    slideOut(null, null);
    setTimeout(async () => {
      openChat();
      const loadMsg = addMsg('...', 'pet');
      const pctx = prefetchedCtx ?? await fetchContext();
      loadMsg.remove();
      if (pctx?.message) {
        petContext = pctx;
        addMsg(pctx.message, 'pet');
        if (pctx.subtext) strip.textContent = pctx.subtext;
        if (pctx.actions?.length) setQuickReplies(pctx.actions);
        const stateMap = { insight: 'idle', reminder: 'worried', rest: 'sleep', celebrate: 'celebrate', worried: 'worried' };
        if (stateMap[pctx.state]) setState(stateMap[pctx.state]);
      } else {
        const h = new Date().getHours();
        const msg = h >= 23 || h < 6 ? '这么晚了，还在搞代码？'
                  : h >= 12 && h < 14 ? '该吃午饭了喵～'
                  : '喵，有什么要做的？';
        addMsg(msg, 'pet');
        setQuickReplies([
          { label: '聊聊', prompt: '我现在在做什么，你有什么看法' },
          { label: '没事', prompt: '没事，继续待机' },
        ]);
      }
    }, JUMP_MS);
  }

  // ── Popup Save listener ───────────────────────────────────────────────────
  chrome.runtime.onMessage.addListener(msg => {
    if (!chrome.runtime?.id) return;
    if (msg.type === 'PET_ANNOUNCE') {
      const modeLabel = { claude: 'Claude Code', codex: 'Codex', api: 'Anthropic API' }[msg.mode] || msg.mode;
      slideOut(`喵！切换到 ${modeLabel} 了，有什么要做的？`, [
        { label: '测试一下', prompt: '用一句话证明你在线' },
        { label: '查看状态', prompt: '告诉我你现在能做什么' },
      ]);
    }
  });

  // ── Multi-pet Presence ────────────────────────────────────────────────────
  // peers: Map<id, {name, petType, state, el, canvas, pctx, frameIdx, lastFrame}>
  const peers = new Map();

  function ghostFilter(petType, slotIdx) {
    const hue = GHOST_HUES[slotIdx % GHOST_HUES.length];
    return `hue-rotate(${hue}deg) saturate(1.4) drop-shadow(-2px 2px 5px rgba(0,0,0,0.5))`;
  }

  function createGhostCat(peer, slotIdx) {
    const el = document.createElement('div');
    el.className = 'pp-ghost';
    Object.assign(el.style, {
      position: 'fixed',
      right: `-${SZ - 14}px`,
      bottom: `${120 + slotIdx * 90}px`,
      zIndex: '2147483645',
      opacity: '0',
      transition: 'right 0.5s cubic-bezier(0.34,1.56,0.64,1), opacity 0.4s ease',
      display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '2px',
      pointerEvents: 'none',
    });

    const nameTag = document.createElement('div');
    nameTag.textContent = peer.name || '?';
    Object.assign(nameTag.style, {
      fontSize: '8px', fontFamily: 'monospace',
      color: '#a8d8ea', background: 'rgba(0,0,0,0.65)',
      padding: '2px 5px', borderRadius: '3px',
      whiteSpace: 'nowrap',
    });

    const c = document.createElement('canvas');
    c.width = SZ; c.height = SZ;
    c.style.cssText = `image-rendering:pixelated; filter:${ghostFilter(peer.petType, slotIdx)};`;

    el.append(nameTag, c);
    document.body.appendChild(el);

    // Slide into view after brief delay
    setTimeout(() => {
      el.style.right = '-10px';
      el.style.opacity = '0.75';
    }, 80);

    return { ...peer, el, canvas: c, pctx: c.getContext('2d'), frameIdx: 0, lastFrame: Date.now() };
  }

  function repositionGhosts() {
    let i = 0;
    for (const [, peer] of peers) {
      peer.el.style.bottom = `${120 + i * 90}px`;
      i++;
    }
  }

  function reconcilePeers(newList) {
    const newIds = new Set(newList.map(p => p.id));

    // Remove gone peers
    for (const [id, peer] of peers) {
      if (!newIds.has(id)) {
        peer.el.style.opacity = '0';
        peer.el.style.right = `-${SZ - 14}px`;
        setTimeout(() => peer.el.remove(), 600);
        peers.delete(id);
      }
    }

    // Add or update peers
    let slotIdx = peers.size;
    for (const p of newList) {
      if (!peers.has(p.id)) {
        // New peer! Create ghost
        const ghost = createGhostCat(p, slotIdx++);
        peers.set(p.id, ghost);
        // My pet greets: quick jump
        if (out) { setState('jump'); setTimeout(() => setState('idle'), 400); }
        // Show greeting in chat if open
        if (chatOpen) addMsg(`${p.name || '新宠物'} 也在这个页面 👋`, 'system');
      } else {
        // Update state
        const existing = peers.get(p.id);
        existing.state   = p.state || 'idle';
        existing.name    = p.name;
        existing.petType = p.pet_type;
      }
    }

    repositionGhosts();
  }

  async function heartbeat() {
    try {
      await fetch('http://localhost:19099/presence/heartbeat', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ id: myId, name: petName, pet_type: catType, state, url: pageUrl }),
        signal: AbortSignal.timeout(3000),
      });
    } catch {}
  }

  async function pollPeers() {
    try {
      const res = await fetch(
        `http://localhost:19099/presence/peers?url=${encodeURIComponent(pageUrl)}&id=${myId}`,
        { signal: AbortSignal.timeout(3000) }
      );
      if (!res.ok) return;
      const list = await res.json();
      if (Array.isArray(list)) reconcilePeers(list);
    } catch {}
  }

  heartbeat();
  pollPeers();
  const presenceInterval = setInterval(() => { heartbeat(); pollPeers(); }, 10000);

  window.addEventListener('beforeunload', () => {
    clearInterval(presenceInterval);
    try {
      navigator.sendBeacon('http://localhost:19099/presence/leave',
        JSON.stringify({ id: myId, url: pageUrl }));
    } catch {}
  });

  // ── Animation loop ────────────────────────────────────────────────────────
  let lastFrameAt = Date.now();
  let lastCtxAt   = 0;

  function loop() {
    if (!chrome.runtime?.id) {
      root?.remove(); chat?.remove();
      document.querySelectorAll('.pp-ghost').forEach(el => el.remove());
      return;
    }

    const now   = Date.now();
    const speed = STATE_SPEED[state] || 1000;

    // Advance my frame
    if (now - lastFrameAt > speed) {
      const frames = STATE_ART[state] || ART_IDLE;
      frameIdx = (frameIdx + 1) % frames.length;
      lastFrameAt = now;
    }

    // Blink randomly
    if ((state === 'idle' || state === 'peek') && Math.random() < 0.004) {
      frameIdx = 1; setTimeout(() => { frameIdx = 0; }, 150);
    }
    if (state === 'peek' && Math.random() < 0.004) {
      frameIdx = 2; setTimeout(() => { frameIdx = 0; }, 200);
    }

    // Render my cat
    const myFrames = STATE_ART[state] || ART_IDLE;
    render(ctx, myFrames[frameIdx % myFrames.length]);

    // Render ghost peers
    for (const [, peer] of peers) {
      const pState = peer.state || 'idle';
      const pSpeed = STATE_SPEED[pState] || 2000;
      if (now - peer.lastFrame > pSpeed) {
        const pFrames = STATE_ART[pState] || ART_IDLE;
        peer.frameIdx = (peer.frameIdx + 1) % pFrames.length;
        peer.lastFrame = now;
      }
      const pFrames = STATE_ART[pState] || ART_IDLE;
      render(peer.pctx, pFrames[peer.frameIdx % pFrames.length]);
    }

    // Periodic context auto-appear (every 25~35 min)
    if (!out && now - lastCtxAt > 1500000 + Math.random() * 600000) {
      lastCtxAt = now;
      fetchContext().then(c => {
        if (c?.message && !out) {
          petContext = c;
          fetchContextAndSlideOut(c);
        }
      });
    }

    requestAnimationFrame(loop);
  }

  loop();
}

init();
