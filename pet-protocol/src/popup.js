let selectedMode = 'api';
let selectedType = 'white';

document.querySelectorAll('.mode-card').forEach(card => {
  card.addEventListener('click', () => {
    document.querySelectorAll('.mode-card').forEach(c => c.classList.remove('selected'));
    document.querySelectorAll('.cfg').forEach(p => p.classList.remove('show'));
    card.classList.add('selected');
    selectedMode = card.dataset.mode;
    document.getElementById(`cfg-${selectedMode}`)?.classList.add('show');
  });
});

document.querySelectorAll('.pet-opt').forEach(el => {
  el.addEventListener('click', () => {
    document.querySelectorAll('.pet-opt').forEach(o => o.classList.remove('selected'));
    el.classList.add('selected');
    selectedType = el.dataset.type;
  });
});

chrome.runtime.sendMessage({ type: 'GET_CONFIG' }, cfg => {
  if (!cfg) return;
  if (cfg.anthropic_key) document.getElementById('apiKey').value = cfg.anthropic_key;
  if (cfg.petName) document.getElementById('petName').value = cfg.petName;
  if (cfg.agent_mode) {
    selectedMode = cfg.agent_mode;
    document.querySelectorAll('.mode-card').forEach(c =>
      c.classList.toggle('selected', c.dataset.mode === selectedMode)
    );
    document.querySelectorAll('.cfg').forEach(p => p.classList.remove('show'));
    document.getElementById(`cfg-${selectedMode}`)?.classList.add('show');
  }
  if (cfg.petType) {
    selectedType = cfg.petType;
    document.querySelectorAll('.pet-opt').forEach(el =>
      el.classList.toggle('selected', el.dataset.type === selectedType)
    );
  }
});

document.getElementById('saveBtn').addEventListener('click', () => {
  const prevMode = selectedMode;
  const config = {
    agent_mode:    selectedMode,
    petType:       selectedType,
    petName:       document.getElementById('petName').value.trim() || 'Mochi',
    anthropic_key: document.getElementById('apiKey').value.trim(),
  };

  chrome.runtime.sendMessage({ type: 'SET_CONFIG', config }, async () => {
    const s = document.getElementById('status');
    s.textContent = '✓ 已保存';
    setTimeout(() => { s.textContent = ''; }, 2000);

    // Notify active tab → pet slides out and announces
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab?.id) {
      chrome.tabs.sendMessage(tab.id, {
        type: 'PET_ANNOUNCE',
        petName: config.petName,
        mode: config.agent_mode,
        petType: config.petType,
      });
    }
  });
});
