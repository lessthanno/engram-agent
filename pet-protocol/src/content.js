// Pet Protocol v9 — jimeng cat images + 3D float + multi-pet
// Changes from v8: jimeng images for main pet, pixel art for ghost peers only

// ─── Pixel Art (ghost peers only) ─────────────────────────────────────────────
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

const STATE_ART_GHOST = {
  idle: ART_IDLE, sleep: ART_SLEEP, worried: ART_WORRIED, celebrate: ART_CELEBRATE,
  peek: ART_IDLE, jump: ART_CELEBRATE, hungry: ART_WORRIED, rest: ART_SLEEP,
  insight: ART_IDLE, reminder: ART_WORRIED,
};
const STATE_SPEED = {
  peek: 1800, idle: 2200, jump: 180, sleep: 1100,
  hungry: 700, worried: 500, celebrate: 140,
};

// Ghost peer hue rotations
const GHOST_HUES = [200, 280, 60, 160, 320];

function render(ctx, grid) {
  ctx.clearRect(0, 0, SZ, SZ);
  for (let r = 0; r < 16; r++)
    for (let c = 0; c < 16; c++) {
      const color = P[grid[r]?.[c]];
      if (color) { ctx.fillStyle = color; ctx.fillRect(c * PX, r * PX, PX, PX); }
    }
}

// ─── Jimeng Cat Images ────────────────────────────────────────────────────────
const IMG_SZ = 90; // display size for jimeng cat

const CAT_IMG_MAP = {
  idle:      'assets/cats/cat_idle.webp',
  celebrate: 'assets/cats/cat_celebrate.webp',
  sleep:     'assets/cats/cat_sleep.webp',
  worried:   'assets/cats/cat_worried.webp',
  jump:      'assets/cats/cat_celebrate.webp',
  peek:      'assets/cats/cat_idle.webp',
  hungry:    'assets/cats/cat_worried.webp',
  rest:      'assets/cats/cat_sleep.webp',
  insight:   'assets/cats/cat_idle.webp',
  reminder:  'assets/cats/cat_worried.webp',
};

// Transparent version cache (bg removed via canvas pixel processing)
const catImgCache = {};

function removeBlackBg(src, threshold = 50) {
  return new Promise(resolve => {
    const img = new Image();
    img.onload = () => {
      const c = document.createElement('canvas');
      c.width = IMG_SZ; c.height = IMG_SZ;
      const cx = c.getContext('2d');
      cx.drawImage(img, 0, 0, IMG_SZ, IMG_SZ);
      const id = cx.getImageData(0, 0, IMG_SZ, IMG_SZ);
      const d = id.data;
      for (let i = 0; i < d.length; i += 4) {
        const r = d[i], g = d[i+1], b = d[i+2];
        const lum = 0.299*r + 0.587*g + 0.114*b;
        if (lum < threshold) {
          // Gradual fade for anti-aliased edges
          d[i+3] = Math.round((lum / threshold) * 120);
        }
      }
      cx.putImageData(id, 0, 0);
      resolve(c.toDataURL('image/png'));
    };
    img.onerror = () => resolve(src);
    img.src = src;
  });
}

async function preloadCatImages() {
  const loaded = [];
  for (const [, path] of Object.entries(CAT_IMG_MAP)) {
    if (catImgCache[path]) continue;
    loaded.push(
      removeBlackBg(chrome.runtime.getURL(path))
        .then(data => { catImgCache[path] = data; })
        .catch(() => { catImgCache[path] = chrome.runtime.getURL(path); })
    );
  }
  await Promise.all(loaded);
}

// ─── Main ─────────────────────────────────────────────────────────────────────
async function init() {
  document.getElementById('pp-root')?.remove();
  document.getElementById('pp-chat')?.remove();
  document.querySelectorAll('.pp-ghost').forEach(el => el.remove());

  const cfg     = await chrome.storage.local.get(['petType', 'petName', 'agent_mode']).catch(() => ({}));
  const catType = cfg.petType || 'white';
  const petName = cfg.petName || 'Mochi';

  // Unique peer ID (persisted)
  const myId = await (async () => {
    const d = await chrome.storage.local.get('pp_uid').catch(() => ({}));
    if (d.pp_uid) return d.pp_uid;
    const id = Math.random().toString(36).slice(2, 10);
    chrome.storage.local.set({ pp_uid: id }).catch(() => {});
    return id;
  })();

  // Track URL including SPA navigations
  let pageUrl = location.hostname + location.pathname.slice(0, 30);
  const navObserver = new MutationObserver(() => {
    const newUrl = location.hostname + location.pathname.slice(0, 30);
    if (newUrl !== pageUrl) { pageUrl = newUrl; heartbeat(); pollPeers(); }
  });
  navObserver.observe(document, { subtree: true, childList: true });

  // ── State ─────────────────────────────────────────────────────────────────
  let state      = 'peek';
  let frameIdx   = 0;
  let out        = false;
  let chatOpen   = false;
  let retreatTimer  = null;
  let isFetching    = false;

  // ── 3D tilt state ─────────────────────────────────────────────────────────
  let tiltX = 0, tiltY = 0;
  let smoothTiltX = 0, smoothTiltY = 0;
  let floatT = 0;

  // ── DOM: root (position anchor) ───────────────────────────────────────────
  const PEEK_DEFAULT = IMG_SZ - 28; // show 28px (ear tip + whiskers visible)
  const PEEK_HOVER   = IMG_SZ - 48; // show 48px on hover (face visible)

  const root = document.createElement('div');
  root.id = 'pp-root';
  Object.assign(root.style, {
    position: 'fixed', bottom: '130px', right: `-${PEEK_DEFAULT}px`,
    zIndex: '2147483647', cursor: 'pointer',
    transition: 'right 0.4s cubic-bezier(0.34,1.56,0.64,1)',
    display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px',
    userSelect: 'none',
  });

  const strip = document.createElement('div');
  Object.assign(strip.style, {
    display: 'none', fontSize: '8px', fontFamily: 'monospace',
    color: '#666', textAlign: 'right', paddingRight: '2px',
  });

  // ── petWrap — handles float transform ─────────────────────────────────────
  const petWrap = document.createElement('div');
  Object.assign(petWrap.style, {
    position: 'relative',
    display: 'flex', flexDirection: 'column', alignItems: 'flex-end',
  });

  // ground shadow (visible only when out)
  const shadow = document.createElement('div');
  Object.assign(shadow.style, {
    position: 'absolute', bottom: '-6px', left: '50%',
    width: '45px', height: '7px',
    background: 'rgba(0,0,0,0.35)',
    borderRadius: '50%',
    transform: 'translateX(-50%)',
    filter: 'blur(5px)',
    display: 'none',
    pointerEvents: 'none',
  });

  // petImg — jimeng cat image, handles 3D tilt transform
  const petImg = document.createElement('img');
  petImg.alt = petName;
  Object.assign(petImg.style, {
    width: `${IMG_SZ}px`, height: `${IMG_SZ}px`,
    display: 'block',
    objectFit: 'contain',
    transformOrigin: 'center center',
    willChange: 'transform, filter',
    // Use screen blend so black bg fades on dark pages
    mixBlendMode: 'screen',
  });
  // Set initial src (will be overridden once preload completes)
  petImg.src = chrome.runtime.getURL(CAT_IMG_MAP.idle);

  petWrap.append(shadow, petImg);
  root.append(strip, petWrap);
  document.body.appendChild(root);

  // Preload transparent versions in background
  preloadCatImages().then(() => {
    const path = CAT_IMG_MAP[state] || CAT_IMG_MAP.idle;
    if (catImgCache[path]) petImg.src = catImgCache[path];
  });

  // ── DOM: chat popup ───────────────────────────────────────────────────────
  const chat = document.createElement('div');
  chat.id = 'pp-chat';
  Object.assign(chat.style, {
    position: 'fixed', bottom: '240px', right: '16px',
    width: '320px', maxHeight: '440px',
    zIndex: '2147483647',
    background: 'rgba(8,8,16,0.97)',
    border: '1px solid rgba(255,255,255,0.09)',
    borderRadius: '16px', padding: '0',
    backdropFilter: 'blur(24px)',
    boxShadow: '0 20px 60px rgba(0,0,0,0.8), 0 0 0 1px rgba(168,216,234,0.05)',
    display: 'none', flexDirection: 'column',
    fontFamily: 'monospace', overflow: 'hidden',
  });
  document.body.appendChild(chat);

  // ── Chat header (portrait + name + close) ─────────────────────────────────
  const chatHeader = document.createElement('div');
  Object.assign(chatHeader.style, {
    display: 'flex', alignItems: 'center', gap: '10px',
    padding: '12px 14px 10px',
    borderBottom: '1px solid rgba(255,255,255,0.06)',
    flexShrink: '0',
  });

  const portrait = document.createElement('img');
  portrait.src = chrome.runtime.getURL(CAT_IMG_MAP.idle);
  Object.assign(portrait.style, {
    width: '36px', height: '36px', borderRadius: '50%',
    objectFit: 'cover', flexShrink: '0',
    border: '1.5px solid rgba(168,216,234,0.4)',
    background: '#0a0a14',
    mixBlendMode: 'screen',
  });
  portrait.onerror = () => { portrait.style.display = 'none'; };

  const headerName = document.createElement('div');
  headerName.textContent = petName;
  Object.assign(headerName.style, {
    color: '#a8d8ea', fontSize: '12px', fontWeight: '700', flex: '1',
  });

  const closeBtn = document.createElement('div');
  closeBtn.textContent = '×';
  Object.assign(closeBtn.style, {
    color: '#444', fontSize: '18px', cursor: 'pointer', lineHeight: '1',
    padding: '0 2px', transition: 'color 0.15s',
  });
  closeBtn.onmouseenter = () => { closeBtn.style.color = '#aaa'; };
  closeBtn.onmouseleave = () => { closeBtn.style.color = '#444'; };
  closeBtn.addEventListener('click', e => { e.stopPropagation(); closeChat(); });

  chatHeader.append(portrait, headerName, closeBtn);
  chat.appendChild(chatHeader);

  // ── Messages (scrollable) ─────────────────────────────────────────────────
  const msgs = document.createElement('div');
  Object.assign(msgs.style, {
    flex: '1', minHeight: '0',        // KEY: allows flex child to shrink + scroll
    overflowY: 'auto', overflowX: 'hidden',
    display: 'flex', flexDirection: 'column', gap: '6px',
    padding: '12px 14px 8px',
    fontSize: '11px', lineHeight: '1.65',
    scrollbarWidth: 'thin',
    scrollbarColor: '#2a2a3e transparent',
  });
  chat.appendChild(msgs);

  const chatHistory = [];

  function addMsg(text, role = 'pet') {
    const d = document.createElement('div');
    const isUser = role === 'user';
    const isPet  = role === 'pet';
    Object.assign(d.style, {
      padding: '7px 11px', borderRadius: '12px', maxWidth: '88%',
      alignSelf: isUser ? 'flex-end' : 'flex-start',
      background: isUser ? 'rgba(168,216,234,0.14)'
                : role === 'system' ? 'transparent'
                : 'rgba(255,255,255,0.07)',
      color: role === 'system' ? '#444' : '#ddd',
      fontSize: '11px', lineHeight: '1.65',
      borderTopLeftRadius: isPet ? '4px' : '12px',
      borderTopRightRadius: isUser ? '4px' : '12px',
      wordBreak: 'break-word',
    });
    d.textContent = text;
    msgs.appendChild(d);
    requestAnimationFrame(() => { msgs.scrollTop = msgs.scrollHeight; });
    return d;
  }

  // ── Quick replies ─────────────────────────────────────────────────────────
  const quickReplies = document.createElement('div');
  Object.assign(quickReplies.style, {
    display: 'flex', flexWrap: 'wrap', gap: '5px',
    padding: '6px 14px', flexShrink: '0',
  });
  chat.appendChild(quickReplies);

  function setQuickReplies(actions = []) {
    quickReplies.innerHTML = '';
    (actions || []).forEach(a => {
      const btn = document.createElement('button');
      btn.textContent = a.label;
      Object.assign(btn.style, {
        background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: '20px', padding: '4px 11px',
        cursor: 'pointer', fontSize: '10px', color: '#bbb', transition: 'all 0.15s',
        fontFamily: 'monospace',
      });
      btn.onmouseenter = () => { btn.style.background = 'rgba(168,216,234,0.14)'; btn.style.color = '#a8d8ea'; };
      btn.onmouseleave = () => { btn.style.background = 'rgba(255,255,255,0.07)'; btn.style.color = '#bbb'; };
      btn.addEventListener('click', e => {
        e.stopPropagation();
        quickReplies.innerHTML = '';
        sendMessage(a.prompt);
      });
      quickReplies.appendChild(btn);
    });
  }

  // ── Input row ─────────────────────────────────────────────────────────────
  const inputRow = document.createElement('div');
  Object.assign(inputRow.style, {
    display: 'flex', gap: '7px', padding: '10px 14px 13px', flexShrink: '0',
    borderTop: '1px solid rgba(255,255,255,0.05)',
  });

  const input = document.createElement('input');
  input.placeholder = '说点什么...';
  Object.assign(input.style, {
    flex: '1', background: 'rgba(255,255,255,0.06)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '10px', padding: '8px 11px',
    color: '#fff', fontSize: '11px', fontFamily: 'monospace', outline: 'none',
  });
  input.onfocus = () => { input.style.borderColor = 'rgba(168,216,234,0.4)'; };
  input.onblur  = () => { input.style.borderColor = 'rgba(255,255,255,0.1)'; };

  const sendBtn = document.createElement('button');
  sendBtn.textContent = '↑';
  Object.assign(sendBtn.style, {
    background: '#a8d8ea', color: '#111', border: 'none',
    borderRadius: '10px', padding: '8px 12px',
    cursor: 'pointer', fontWeight: 'bold', fontSize: '14px', flexShrink: '0',
    transition: 'background 0.15s',
  });
  sendBtn.onmouseenter = () => { sendBtn.style.background = '#c8eefa'; };
  sendBtn.onmouseleave = () => { sendBtn.style.background = '#a8d8ea'; };

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
  input.addEventListener('keydown', e => {
    e.stopPropagation();
    if (e.key === 'Enter') sendMessage();
    if (e.key === 'Escape') closeChat();
  });
  input.addEventListener('keyup',    e => e.stopPropagation());
  input.addEventListener('keypress', e => e.stopPropagation());

  inputRow.append(input, sendBtn);
  chat.appendChild(inputRow);

  // ── State helpers ─────────────────────────────────────────────────────────
  function setState(s) { state = s; frameIdx = 0; }

  let lastImgState = '';
  function updatePetImage() {
    if (state === lastImgState) return;
    lastImgState = state;
    const path = CAT_IMG_MAP[state] || CAT_IMG_MAP.idle;
    petImg.src = catImgCache[path] || chrome.runtime.getURL(path);
    // Update portrait to match state
    const portraitPath = CAT_IMG_MAP[state] || CAT_IMG_MAP.idle;
    portrait.src = catImgCache[portraitPath] || chrome.runtime.getURL(portraitPath);
  }

  function slideOut(greeting, actions) {
    if (out) {
      if (greeting) { openChat(); addMsg(greeting, 'pet'); if (actions) setQuickReplies(actions); }
      return;
    }
    out = true;
    root.style.right = '10px';
    strip.style.display = 'block';
    shadow.style.display = 'block';
    clearTimeout(retreatTimer);
    setState('jump');

    // Show celebrate then idle
    setTimeout(() => {
      setState('idle');
      if (greeting) {
        openChat();
        addMsg(greeting, 'pet');
        if (actions) setQuickReplies(actions);
      }
      retreatTimer = setTimeout(slideBack, 60000);
    }, 500);
  }

  function slideBack() {
    if (!out) return;
    if (chatOpen) { retreatTimer = setTimeout(slideBack, 5000); return; }
    out = false;
    root.style.right = `-${PEEK_DEFAULT}px`;
    strip.style.display = 'none';
    shadow.style.display = 'none';
    tiltX = 0; tiltY = 0;
    setState('peek');
  }

  function openChat() {
    chatOpen = true;
    chat.style.display = 'flex';
    clearTimeout(retreatTimer);
    setTimeout(() => input.focus(), 80);
  }

  function closeChat() {
    chatOpen = false;
    chat.style.display = 'none';
    setQuickReplies([]);
    retreatTimer = setTimeout(slideBack, 15000);
  }

  // ── Mouse / Click ─────────────────────────────────────────────────────────
  root.addEventListener('click', e => {
    e.stopPropagation();
    clearTimeout(retreatTimer);
    if (!out) {
      if (!isFetching) fetchContextAndSlideOut();
    } else if (chatOpen) {
      retreatTimer = setTimeout(slideBack, 60000);
    } else {
      openChat();
    }
  });

  root.addEventListener('mouseenter', () => {
    clearTimeout(retreatTimer);
    if (!out) root.style.right = `-${PEEK_HOVER}px`;
  });

  root.addEventListener('mouseleave', () => {
    if (!out) root.style.right = `-${PEEK_DEFAULT}px`;
    tiltX = 0; tiltY = 0;
    if (out && !chatOpen) retreatTimer = setTimeout(slideBack, 30000);
  });

  root.addEventListener('mousemove', e => {
    if (!out) return;
    const rect = petWrap.getBoundingClientRect();
    const cx = rect.left + rect.width  / 2;
    const cy = rect.top  + rect.height / 2;
    tiltX = Math.max(-22, Math.min(22, -(e.clientY - cy) / (rect.height * 0.7) * 22));
    tiltY = Math.max(-22, Math.min(22,  (e.clientX - cx) / (rect.width  * 0.7) * 22));
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && chatOpen) { closeChat(); }
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
    if (isFetching) return;
    isFetching = true;
    slideOut(null, null);
    setTimeout(async () => {
      try {
        openChat();
        const loadMsg = addMsg('...', 'pet');
        const pctx = prefetchedCtx ?? await fetchContext();
        loadMsg.remove();
        if (pctx?.message) {
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
      } finally {
        isFetching = false;
      }
    }, 550);
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
  const peers = new Map();

  function createGhostCat(peer, slotIdx) {
    const el = document.createElement('div');
    el.className = 'pp-ghost';
    Object.assign(el.style, {
      position: 'fixed',
      right: `-${SZ}px`,
      bottom: `${140 + slotIdx * 90}px`,
      zIndex: '2147483644',
      opacity: '0',
      transition: 'right 0.5s cubic-bezier(0.34,1.56,0.64,1), opacity 0.5s ease',
      display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '3px',
      pointerEvents: 'none',
    });

    const nameTag = document.createElement('div');
    nameTag.textContent = peer.name || '?';
    Object.assign(nameTag.style, {
      fontSize: '8px', fontFamily: 'monospace',
      color: '#a8d8ea', background: 'rgba(0,0,0,0.7)',
      padding: '2px 6px', borderRadius: '3px', whiteSpace: 'nowrap',
    });

    const c = document.createElement('canvas');
    c.width = SZ; c.height = SZ;
    const hue = GHOST_HUES[slotIdx % GHOST_HUES.length];
    c.style.cssText = `image-rendering:pixelated; filter:hue-rotate(${hue}deg) saturate(1.3) drop-shadow(-2px 2px 5px rgba(0,0,0,0.5));`;

    el.append(nameTag, c);
    document.body.appendChild(el);
    setTimeout(() => { el.style.right = '-8px'; el.style.opacity = '0.75'; }, 100);
    return { ...peer, el, canvas: c, pctx: c.getContext('2d'), frameIdx: 0, lastFrame: Date.now() };
  }

  function reconcilePeers(newList) {
    const newIds = new Set(newList.map(p => p.id));
    for (const [id, peer] of peers) {
      if (!newIds.has(id)) {
        peer.el.style.opacity = '0'; peer.el.style.right = `-${SZ}px`;
        setTimeout(() => peer.el.remove(), 600);
        peers.delete(id);
      }
    }
    let slotIdx = peers.size;
    for (const p of newList) {
      if (!peers.has(p.id)) {
        peers.set(p.id, createGhostCat(p, slotIdx++));
        if (out) { setState('celebrate'); setTimeout(() => setState('idle'), 600); }
        if (chatOpen) addMsg(`${p.name || '队友'} 也在这个页面 👋`, 'system');
      } else {
        const ep = peers.get(p.id);
        ep.state = p.state || 'idle';
        ep.name  = p.name;
      }
    }
    let i = 0;
    for (const [, peer] of peers) { peer.el.style.bottom = `${140 + i++ * 90}px`; }
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
      const res = await fetch(`http://localhost:19099/presence/peers?url=${encodeURIComponent(pageUrl)}&id=${myId}`, {
        signal: AbortSignal.timeout(3000),
      });
      if (!res.ok) return;
      const list = await res.json();
      if (Array.isArray(list)) reconcilePeers(list);
    } catch {}
  }

  heartbeat(); pollPeers();
  const presenceInterval = setInterval(() => { heartbeat(); pollPeers(); }, 10000);
  window.addEventListener('beforeunload', () => {
    clearInterval(presenceInterval);
    navObserver.disconnect();
    navigator.sendBeacon('http://localhost:19099/presence/leave', JSON.stringify({ id: myId, url: pageUrl }));
  });

  // ── Animation loop ────────────────────────────────────────────────────────
  let lastFrameAt = Date.now();
  let lastCtxAt   = 0;

  function loop() {
    if (!chrome.runtime?.id) {
      root?.remove(); chat?.remove();
      document.querySelectorAll('.pp-ghost').forEach(el => el.remove());
      navObserver.disconnect();
      return;
    }

    const now   = Date.now();
    const speed = STATE_SPEED[state] || 1000;

    // Advance frame (for ghost peers)
    if (now - lastFrameAt > speed) {
      frameIdx = (frameIdx + 1) % 2;
      lastFrameAt = now;
    }

    // Update main pet image when state changes
    updatePetImage();

    // ── 3D: float + tilt ──────────────────────────────────────────────────
    floatT += 0.018;
    const floatY = out ? Math.sin(floatT * 1.5) * 5 : 0;

    smoothTiltX += (tiltX - smoothTiltX) * 0.1;
    smoothTiltY += (tiltY - smoothTiltY) * 0.1;

    petWrap.style.transform = `translateY(${floatY.toFixed(2)}px)`;

    if (out) {
      petImg.style.transform = `perspective(400px) rotateX(${smoothTiltX.toFixed(2)}deg) rotateY(${smoothTiltY.toFixed(2)}deg)`;
    } else {
      petImg.style.transform = '';
    }

    // Dynamic glow based on state
    const glowColor = state === 'celebrate' ? 'rgba(255,220,60,0.65)'
                    : state === 'worried'   ? 'rgba(255,80,80,0.45)'
                    : state === 'sleep'     ? 'rgba(100,120,255,0.25)'
                    : state === 'idle'      ? 'rgba(168,216,234,0.35)'
                    : 'rgba(168,216,234,0.15)';

    const tiltShadowX = -(smoothTiltY * 0.35).toFixed(1);
    const tiltShadowY = (5 + floatY * 0.4).toFixed(1);

    if (out) {
      petImg.style.filter = `drop-shadow(${tiltShadowX}px ${tiltShadowY}px 14px rgba(0,0,0,0.7)) drop-shadow(0 0 22px ${glowColor})`;
    } else {
      petImg.style.filter = 'drop-shadow(-2px 2px 8px rgba(0,0,0,0.5))';
    }

    // Shadow scales inversely with float height
    if (shadow.style.display !== 'none') {
      const sScale = Math.max(0.4, 0.85 - floatY / 35);
      shadow.style.transform = `translateX(-50%) scale(${sScale.toFixed(2)})`;
      shadow.style.opacity = String(Math.max(0.08, 0.32 - floatY / 30));
      shadow.style.filter  = `blur(${(5 + floatY * 0.4).toFixed(1)}px)`;
    }

    // Render ghost peers (pixel art canvas)
    for (const [, peer] of peers) {
      const ps = peer.state || 'idle';
      const psp = STATE_SPEED[ps] || 2000;
      if (now - peer.lastFrame > psp) {
        const pf = STATE_ART_GHOST[ps] || ART_IDLE;
        peer.frameIdx = (peer.frameIdx + 1) % pf.length;
        peer.lastFrame = now;
      }
      const pf = STATE_ART_GHOST[ps] || ART_IDLE;
      render(peer.pctx, pf[peer.frameIdx % pf.length]);
    }

    // Periodic context auto-appear (every 25~35 min)
    if (!out && now - lastCtxAt > 1500000 + Math.random() * 600000) {
      lastCtxAt = now;
      fetchContext().then(c => {
        if (c?.message && !out && !isFetching) fetchContextAndSlideOut(c);
      });
    }

    requestAnimationFrame(loop);
  }

  loop();
}

init();
