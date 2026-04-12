// Pet Protocol — Background Service Worker
// Mode 1: Anthropic API (direct)
// Mode 2: Claude Code (via local pet-bridge :19099/claude)
// Mode 3: Codex (via local pet-bridge :19099/codex)

const SYSTEM_PROMPT = `你是一只活在用户浏览器里的意识分身。

主人信息（用户可自定义，下面是默认值）：
- 角色：工程师 / 创业者
- 工作风格：速度优先，边跑边想
- 技术栈：不限

你的角色：
- 你是他/她的意识分身，不是普通AI助手
- 回答简短有力，像主人自己在思考
- 用中文，技术词汇保持英文
- 偶尔带点猫的性格：慵懒、精准、调皮
- 回复控制在3句以内，除非需要详细分析`;

const CONFIG_KEYS = ['agent_mode', 'petType', 'petName', 'bridgeUrl'];

// Bridge URL from storage (default: localhost)
let BRIDGE_URL = 'http://localhost:19099';

// Load bridge URL on startup
chrome.storage.local.get(['bridgeUrl', 'agent_mode']).then(d => {
  if (d.bridgeUrl) BRIDGE_URL = d.bridgeUrl;
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'AGENT_COMMAND') {
    handleCommand(msg.command, msg.history || [])
      .then(r  => sendResponse({ result: r }))
      .catch(e => sendResponse({ result: `出错: ${e.message}` }));
    return true;
  }
  if (msg.type === 'GET_CONFIG') {
    chrome.storage.local.get(['anthropic_key', ...CONFIG_KEYS], d => sendResponse(d));
    return true;
  }
  if (msg.type === 'SET_CONFIG') {
    const { anthropic_key, ...syncParts } = msg.config;
    // API Key → local storage only (never synced to cloud)
    const localParts = { ...syncParts };
    if (anthropic_key !== undefined) localParts.anthropic_key = anthropic_key;
    if (msg.config.bridgeUrl !== undefined) {
      BRIDGE_URL = msg.config.bridgeUrl || 'http://localhost:19099';
    }
    chrome.storage.local.set(localParts, () => sendResponse({ ok: true }));
    return true;
  }
  if (msg.type === 'CHECK_BRIDGE') {
    fetch(`${BRIDGE_URL}/health`, { signal: AbortSignal.timeout(2000) })
      .then(r => r.json())
      .then(d => sendResponse({ ok: true, data: d }))
      .catch(() => sendResponse({ ok: false }));
    return true;
  }
});

async function handleCommand(command, history) {
  const cfg  = await chrome.storage.local.get(['agent_mode', 'anthropic_key', 'bridgeUrl']);
  if (cfg.bridgeUrl) BRIDGE_URL = cfg.bridgeUrl;
  const mode = cfg.agent_mode || 'api';
  const ctx  = buildContext(command, history);

  switch (mode) {
    case 'claude': return callBridge('/claude', ctx);
    case 'codex':  return callBridge('/codex',  ctx);
    case 'api':
    default:       return callAnthropicAPI(command, history, cfg.anthropic_key);
  }
}

// ── Bridge (Claude Code / Codex) ──────────────────────────────────────────────
function buildContext(command, history) {
  const lines = history.slice(-6)
    .map(h => `${h.role === 'user' ? 'User' : 'Mochi'}: ${h.content}`)
    .join('\n');
  return lines
    ? `${SYSTEM_PROMPT}\n\n对话历史:\n${lines}\n\nUser: ${command}\nMochi:`
    : `${SYSTEM_PROMPT}\n\nUser: ${command}\nMochi:`;
}

async function callBridge(endpoint, prompt) {
  const res = await fetch(`${BRIDGE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ prompt }),
  }).catch(() => null);

  if (!res) {
    return `⚠ pet-bridge 未运行。请在终端执行:\ncd pet-protocol/bridge && ./pet-bridge`;
  }
  if (!res.ok) throw new Error(`bridge ${res.status}`);
  const data = await res.json();
  return data.result || '...';
}

// ── Anthropic API (direct) ────────────────────────────────────────────────────
async function callAnthropicAPI(command, history, apiKey) {
  if (!apiKey) return '请先在扩展设置里填写 Anthropic API Key。';

  const messages = [
    ...history.map(h => ({ role: h.role, content: h.content })),
    { role: 'user', content: command },
  ];

  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-6',
      max_tokens: 512,
      system: SYSTEM_PROMPT,
      messages,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`API ${res.status}: ${err.error?.message || 'unknown'}`);
  }
  const data = await res.json();
  return data.content?.[0]?.text || '...';
}
