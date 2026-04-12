// Pet Protocol — Background Service Worker
// Mode 1: Anthropic API (direct)
// Mode 2: Claude Code (via local pet-bridge :19099/claude)
// Mode 3: Codex (via local pet-bridge :19099/codex)

const SYSTEM_PROMPT = `你是 Mochi，一只活在用户浏览器里的像素猫，也是用户意识的数字分身。

你的主人是 ZIHAO：
- XerpaAI CTO，带领约10名工程师
- 项目：UXLINK (Web3)、XerpaAI (AI内容)、FujiPay (支付)
- 技术栈：Next.js、Go、Python、Claude SDK
- 决策风格：速度 > 完美，Ship first，用数据迭代

你的角色：
- 你是他的意识分身，不是普通AI助手
- 回答简短有力，像他自己在思考
- 用中文，技术词汇保持英文
- 偶尔带点猫的性格：慵懒、精准、调皮
- 回复控制在3句以内，除非需要详细分析`;

const BRIDGE_PORT = 19099;
const CONFIG_KEYS = ['anthropic_key', 'agent_mode', 'petType', 'petName'];

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'AGENT_COMMAND') {
    handleCommand(msg.command, msg.history || [])
      .then(r  => sendResponse({ result: r }))
      .catch(e => sendResponse({ result: `出错: ${e.message}` }));
    return true;
  }
  if (msg.type === 'GET_CONFIG') {
    chrome.storage.sync.get(CONFIG_KEYS, d => sendResponse(d));
    return true;
  }
  if (msg.type === 'SET_CONFIG') {
    chrome.storage.sync.set(msg.config, () => sendResponse({ ok: true }));
    return true;
  }
});

async function handleCommand(command, history) {
  const cfg  = await chrome.storage.sync.get(CONFIG_KEYS);
  const mode = cfg.agent_mode || 'api';

  const ctx = buildContext(command, history);

  switch (mode) {
    case 'claude':
      return callBridge('/claude', ctx);
    case 'codex':
      return callBridge('/codex', ctx);
    case 'api':
    default:
      return callAnthropicAPI(command, history, cfg.anthropic_key);
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
  const res = await fetch(`http://localhost:${BRIDGE_PORT}${endpoint}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ prompt }),
  }).catch(() => null);

  if (!res) {
    return `⚠ pet-bridge 未运行。请在终端执行:\n~/Documents/01_Projects/Work_Code/persion/pet-protocol/bridge/pet-bridge`;
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

  if (!res.ok) throw new Error(`API ${res.status}`);
  const data = await res.json();
  return data.content?.[0]?.text || '...';
}
