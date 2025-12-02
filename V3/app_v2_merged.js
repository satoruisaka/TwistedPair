// TwistedPair V2 - Merged Analog Knobs + Chat Sessions

const API_URL = 'http://localhost:8000';
let currentMode = 'ensemble';
let modes = [];
let tones = [];
let models = [];
let defaultModel = '';
let abortController = null;

// Knob state
let modeIndex = 0;
let toneIndex = 1; // Default to NEUTRAL
let gainValue = 5;

// Fork knob state (separate from main knobs)
let forkModeIndex = 0;
let forkToneIndex = 1;
let forkGainValue = 5;

// Chat session state
let currentSession = null;
let ensembleOutputs = []; // Store ensemble results for follow-up

// ============================================
// V1 ANALOG KNOB FUNCTIONALITY
// ============================================

// Load available models from API
async function loadModels() {
  try {
    const response = await fetch(`${API_URL}/models`);
    const data = await response.json();
    models = data.models;
    defaultModel = data.default;

    const modelSelect = document.getElementById('modelSelect');
    modelSelect.innerHTML = '';
    
    models.forEach(model => {
      const option = document.createElement('option');
      option.value = model;
      option.textContent = model;
      if (model === defaultModel) {
        option.selected = true;
      }
      modelSelect.appendChild(option);
    });
  } catch (error) {
    console.error('Failed to load models:', error);
    document.getElementById('modelSelect').innerHTML = '<option>Error loading models</option>';
  }
}

// Load knob options from API
async function loadKnobs() {
  try {
    const response = await fetch(`${API_URL}/knobs`);
    const data = await response.json();
    modes = data.modes;
    tones = data.tones;
    
    // Set initial values
    updateModeDisplay();
    updateToneDisplay();
    updateGainDisplay();
    
    // Populate fork selectors
    populateForkSelectors();
  } catch (error) {
    console.error('Failed to load knobs:', error);
  }
}

function populateForkSelectors() {
  // Fork controls now use analog knobs, just update displays
  updateForkModeDisplay();
  updateForkToneDisplay();
  updateForkGainDisplay();
}

// Rotary knob logic with circular drag
function initKnob(element, onUpdate) {
  let isDragging = false;
  let currentAngle = 0;
  let lastMouseAngle = 0;

  function getMouseAngle(e, element) {
    const rect = element.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const mouseX = e.clientX;
    const mouseY = e.clientY;
    
    const angle = Math.atan2(mouseY - centerY, mouseX - centerX);
    return angle * (180 / Math.PI);
  }

  function getTouchAngle(e, element) {
    const rect = element.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const touchX = e.touches[0].clientX;
    const touchY = e.touches[0].clientY;
    
    const angle = Math.atan2(touchY - centerY, touchX - centerX);
    return angle * (180 / Math.PI);
  }

  function normalizeAngleDelta(delta) {
    if (delta > 180) return delta - 360;
    if (delta < -180) return delta + 360;
    return delta;
  }

  element.addEventListener('mousedown', (e) => {
    isDragging = true;
    currentAngle = getCurrentAngle(element);
    lastMouseAngle = getMouseAngle(e, element);
    e.preventDefault();
  });

  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    
    const mouseAngle = getMouseAngle(e, element);
    const delta = normalizeAngleDelta(mouseAngle - lastMouseAngle);
    lastMouseAngle = mouseAngle;
    
    currentAngle += delta;
    currentAngle = Math.max(-135, Math.min(135, currentAngle));
    
    setKnobAngle(element, currentAngle);
    onUpdate(currentAngle);
  });

  document.addEventListener('mouseup', () => {
    isDragging = false;
  });

  element.addEventListener('touchstart', (e) => {
    isDragging = true;
    currentAngle = getCurrentAngle(element);
    lastMouseAngle = getTouchAngle(e, element);
    e.preventDefault();
  });

  document.addEventListener('touchmove', (e) => {
    if (!isDragging) return;
    
    const touchAngle = getTouchAngle(e, element);
    const delta = normalizeAngleDelta(touchAngle - lastMouseAngle);
    lastMouseAngle = touchAngle;
    
    currentAngle += delta;
    currentAngle = Math.max(-135, Math.min(135, currentAngle));
    
    setKnobAngle(element, currentAngle);
    onUpdate(currentAngle);
  });

  document.addEventListener('touchend', () => {
    isDragging = false;
  });
}

function getCurrentAngle(element) {
  const transform = element.querySelector('.knob-body').style.transform;
  const match = transform.match(/rotate\\((-?\\d+(?:\\.\\d+)?)deg\\)/);
  return match ? parseFloat(match[1]) : 0;
}

function setKnobAngle(element, angle) {
  element.querySelector('.knob-body').style.transform = `rotate(${angle}deg)`;
}

function angleToIndex(angle, maxIndex) {
  const normalized = (angle + 135) / 270;
  return Math.round(normalized * maxIndex);
}

function angleToValue(angle, min, max) {
  const normalized = (angle + 135) / 270;
  return Math.round(normalized * (max - min) + min);
}

function initializeKnobs() {
  initKnob(document.getElementById('modeKnob'), (angle) => {
    modeIndex = angleToIndex(angle, modes.length - 1);
    updateModeDisplay();
  });

  initKnob(document.getElementById('toneKnob'), (angle) => {
    toneIndex = angleToIndex(angle, tones.length - 1);
    updateToneDisplay();
  });

  initKnob(document.getElementById('gainKnob'), (angle) => {
    gainValue = angleToValue(angle, 1, 10);
    updateGainDisplay();
  });

  // Fork knobs
  initKnob(document.getElementById('forkModeKnob'), (angle) => {
    forkModeIndex = angleToIndex(angle, modes.length - 1);
    updateForkModeDisplay();
  });

  initKnob(document.getElementById('forkToneKnob'), (angle) => {
    forkToneIndex = angleToIndex(angle, tones.length - 1);
    updateForkToneDisplay();
  });

  initKnob(document.getElementById('forkGainKnob'), (angle) => {
    forkGainValue = angleToValue(angle, 1, 10);
    updateForkGainDisplay();
  });
}

function updateModeDisplay() {
  if (modes.length > 0) {
    document.getElementById('modeValue').textContent = modes[modeIndex].toUpperCase();
  }
}

function updateToneDisplay() {
  if (tones.length > 0) {
    document.getElementById('toneValue').textContent = tones[toneIndex].toUpperCase();
  }
}

function updateGainDisplay() {
  document.getElementById('gainValue').textContent = gainValue;
}

function updateForkModeDisplay() {
  if (modes.length > 0) {
    document.getElementById('forkModeValue').textContent = modes[forkModeIndex].toUpperCase();
  }
}

function updateForkToneDisplay() {
  if (tones.length > 0) {
    document.getElementById('forkToneValue').textContent = tones[forkToneIndex].toUpperCase();
  }
}

function updateForkGainDisplay() {
  document.getElementById('forkGainValue').textContent = forkGainValue;
}

function switchMode(mode) {
  currentMode = mode;
  
  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  event.target.classList.add('active');

  const modeKnobContainer = document.getElementById('modeKnobContainer');
  const btnText = document.getElementById('btnText');
  
  if (mode === 'manual') {
    modeKnobContainer.classList.remove('hidden');
    btnText.textContent = '🎛️ Distort Signal (Custom)';
  } else {
    modeKnobContainer.classList.add('hidden');
    btnText.textContent = '🔊 Distort Signal (All 6 Modes)';
  }
}

async function distortSignal() {
  const input = document.getElementById('signalInput').value.trim();
  
  if (!input) {
    alert('Please enter a signal to distort');
    return;
  }

  const btn = document.getElementById('distortBtn');
  const cancelBtn = document.getElementById('cancelBtn');
  const container = document.getElementById('outputContainer');
  
  const tone = tones[toneIndex];
  const gain = gainValue;
  const model = document.getElementById('modelSelect').value;

  btn.disabled = true;
  cancelBtn.classList.add('visible');
  
  abortController = new AbortController();
  
  document.querySelectorAll('.knob-body').forEach(knob => {
    knob.classList.add('processing');
  });
  
  const loadingMsg = currentMode === 'ensemble' 
    ? 'Distorting signal through 6 perspectives...'
    : 'Distorting signal with custom settings...';
  
  container.innerHTML = `
    <div class="loading">
      <div class="spinner"></div>
      <p>${loadingMsg}</p>
    </div>
  `;

  try {
    if (currentMode === 'ensemble') {
      await distortEnsemble(input, tone, gain);
    } else {
      await distortManual(input, tone, gain);
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      container.innerHTML = `
        <div class="loading" style="color: #ff9800;">
          <p>⚠️ Operation cancelled</p>
        </div>
      `;
    } else {
      container.innerHTML = `
        <div class="loading" style="color: #dc3545;">
          <p>❌ Error: ${error.message}</p>
          <p style="font-size: 0.9rem; margin-top: 1rem;">Make sure the server is running</p>
        </div>
      `;
    }
  } finally {
    btn.disabled = false;
    cancelBtn.classList.remove('visible');
    abortController = null;
    document.querySelectorAll('.knob-body').forEach(knob => {
      knob.classList.remove('processing');
    });
  }
}

function cancelDistortion() {
  if (abortController) {
    abortController.abort();
  }
}

async function distortEnsemble(input, tone, gain) {
  const model = document.getElementById('modelSelect').value;
  const timestamp = new Date().toISOString();
  
  const response = await fetch(`${API_URL}/distort`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: input,
      source: 'web-ui-ensemble',
      captured_at: timestamp,
      tags: [],
      tone: tone,
      gain: gain,
      model: model
    }),
    signal: abortController.signal
  });

  if (!response.ok) {
    throw new Error(`Server error: ${response.status}`);
  }

  const data = await response.json();
  ensembleOutputs = data.outputs;
  
  // V3: Display web search results preview if available
  displayWebSearchPreview(data.provenance);
  
  displayOutputsWithChat(ensembleOutputs, model, timestamp);
}

async function distortManual(input, tone, gain) {
  const mode = modes[modeIndex];
  const model = document.getElementById('modelSelect').value;
  const timestamp = new Date().toISOString();
  
  const response = await fetch(`${API_URL}/distort-manual`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: input,
      mode: mode,
      tone: tone,
      gain: gain,
      model: model
    }),
    signal: abortController.signal
  });

  if (!response.ok) {
    throw new Error(`Server error: ${response.status}`);
  }

  const data = await response.json();
  // Store as single-item array for consistent handling
  ensembleOutputs = [data.output];
  
  // V3: Display web search results preview if available
  displayWebSearchPreview(data.output.provenance);
  
  displayOutputsWithChat(ensembleOutputs, model, timestamp);
}

function displayWebSearchPreview(provenance) {
  const container = document.getElementById('outputContainer');
  
  // Check if web search was performed
  if (!provenance || !provenance.metadata || !provenance.metadata.web_enriched) {
    return; // No web search, skip preview
  }
  
  const metadata = provenance.metadata;
  const query = metadata.web_search_query || 'Unknown query';
  const sources = metadata.web_sources || [];
  
  if (sources.length === 0) {
    return; // No sources found
  }
  
  // Build search results preview HTML
  const sourcesHtml = sources.map((source, i) => `
    <div class="search-result-item">
      <div class="search-result-number">${i + 1}</div>
      <div class="search-result-content">
        <a href="${source.url}" target="_blank" class="search-result-title">${source.title}</a>
        <div class="search-result-domain">${source.domain}</div>
      </div>
    </div>
  `).join('');
  
  const previewHtml = `
    <div class="web-search-preview">
      <div class="search-preview-header" onclick="toggleSearchPreview()">
        <span class="search-preview-icon">🔍</span>
        <span class="search-preview-title">Web Search Results for: "${query}"</span>
        <span class="search-preview-count">${sources.length} source${sources.length > 1 ? 's' : ''} found</span>
        <span class="search-preview-toggle">▼</span>
      </div>
      <div class="search-results-list" id="searchResultsList">
        ${sourcesHtml}
      </div>
    </div>
  `;
  
  // Prepend to container (show before outputs)
  container.insertAdjacentHTML('afterbegin', previewHtml);
}

function toggleSearchPreview() {
  const list = document.getElementById('searchResultsList');
  const toggle = document.querySelector('.search-preview-toggle');
  
  if (list.style.display === 'none') {
    list.style.display = 'block';
    toggle.textContent = '▼';
  } else {
    list.style.display = 'none';
    toggle.textContent = '▶';
  }
}

function displayOutputsWithChat(outputs, model, timestamp) {
  const container = document.getElementById('outputContainer');
  
  if (!outputs || outputs.length === 0) {
    container.innerHTML = '<div class="empty-state"><p>No outputs generated</p></div>';
    return;
  }

  const timeStr = new Date(timestamp).toLocaleTimeString();

  const html = outputs.map((output, index) => {
    // Build web sources HTML if available
    let webSourcesHtml = '';
    if (output.provenance && output.provenance.metadata && output.provenance.metadata.web_sources) {
      const sources = output.provenance.metadata.web_sources;
      const sourceLinks = sources.map((source, i) => 
        `<a href="${source.url}" target="_blank" class="web-source-link">${i + 1}. ${source.title}</a>`
      ).join('');
      webSourcesHtml = `
        <div class="web-sources">
          <div class="web-sources-label">🌐 Sources:</div>
          <div class="web-sources-list">${sourceLinks}</div>
        </div>
      `;
    }

    return `
      <div class="output-card" data-output-index="${index}">
        <div class="output-header">
          <span class="badge mode-badge">${output.mode}</span>
          <span class="badge tone-badge">${output.tone}</span>
          <span class="badge gain-badge">Gain ${output.gain}</span>
          <span class="badge model-badge">🤖 ${model}</span>
          <span class="badge time-badge">🕐 ${timeStr}</span>
          <button class="copy-btn" onclick="copyOutput(${index})">📋 Copy</button>
        </div>
        <div class="output-text" data-text="${escapeHtml(output.response).replace(/"/g, '&quot;')}">${escapeHtml(output.response)}</div>
        ${webSourcesHtml}
        <div class="chat-actions">
          <button class="chat-btn" onclick="startFollowUp(${index})">💬 Follow Up</button>
        </div>
      </div>
    `;
  }).join('');

  const copyAllBtn = outputs.length > 1 ? '<button class="copy-all-btn" onclick="copyAllOutputs()">📋 Copy All Outputs</button>' : '';
  const newQueryBtn = '<button class="new-query-btn" onclick="newQuery()">🆕 New Query</button>';
  container.innerHTML = `${newQueryBtn}${copyAllBtn}<div class="outputs">${html}</div>`;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

async function copyOutput(index) {
  const card = document.querySelector(`[data-output-index="${index}"]`);
  const textElement = card.querySelector('.output-text');
  const btn = card.querySelector('.copy-btn');
  
  const text = textElement.textContent;
  
  try {
    await navigator.clipboard.writeText(text);
    const originalText = btn.textContent;
    btn.textContent = '✓ Copied!';
    btn.classList.add('copied');
    
    setTimeout(() => {
      btn.textContent = originalText;
      btn.classList.remove('copied');
    }, 2000);
  } catch (err) {
    console.error('Failed to copy:', err);
    btn.textContent = '✗ Failed';
    setTimeout(() => {
      btn.textContent = '📋 Copy';
    }, 2000);
  }
}

async function copyAllOutputs() {
  const outputs = document.querySelectorAll('.output-text');
  const btn = document.querySelector('.copy-all-btn');
  
  const allText = Array.from(outputs).map((output, index) => {
    const card = output.closest('.output-card');
    const mode = card.querySelector('.mode-badge').textContent;
    const tone = card.querySelector('.tone-badge').textContent;
    const gain = card.querySelector('.gain-badge').textContent;
    const separator = '='.repeat(60);
    return `${separator}\\n${mode} | ${tone} | ${gain}\\n${separator}\\n${output.textContent}\\n`;
  }).join('\\n\\n');
  
  try {
    await navigator.clipboard.writeText(allText);
    const originalText = btn.textContent;
    btn.textContent = '✓ All Copied!';
    btn.classList.add('copied');
    
    setTimeout(() => {
      btn.textContent = originalText;
      btn.classList.remove('copied');
    }, 2000);
  } catch (err) {
    console.error('Failed to copy all:', err);
    btn.textContent = '✗ Failed';
    setTimeout(() => {
      btn.textContent = '📋 Copy All Outputs';
    }, 2000);
  }
}

function clearInput() {
  document.getElementById('signalInput').value = '';
  document.getElementById('signalInput').focus();
}

// ============================================
// V2 CHAT SESSION FUNCTIONALITY
// ============================================

async function startFollowUp(index) {
  const outputs = ensembleOutputs.length > 0 ? ensembleOutputs : [currentMode === 'ensemble' ? null : document.querySelector('[data-output-index="0"]')];
  const output = outputs[index];
  
  if (!output) {
    alert('No output to follow up on');
    return;
  }

  const initialMessage = document.getElementById('signalInput').value.trim();

  try {
    const response = await fetch(`${API_URL}/chat/new`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mode: output.mode,
        tone: output.tone,
        gain: output.gain,
        model: document.getElementById('modelSelect').value,
        initial_message: initialMessage
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    currentSession = data;

    // Update UI
    document.getElementById('chatMode').textContent = output.mode.toUpperCase();
    document.getElementById('chatTone').textContent = output.tone.toUpperCase();
    document.getElementById('chatGain').textContent = output.gain;
    
    renderChatHistory(data.history);
    
    // Hide initial interface, show chat
    document.getElementById('initialSection').style.display = 'none';
    document.querySelector('.mode-toggle').style.display = 'none';
    document.getElementById('outputContainer').style.display = 'none';
    document.getElementById('chatInterface').classList.add('active');

  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

async function sendChatMessage() {
  const input = document.getElementById('chatInput').value.trim();
  
  if (!input || !currentSession) {
    return;
  }

  const btn = document.getElementById('sendChatBtn');
  btn.disabled = true;

  try {
    const response = await fetch(`${API_URL}/chat/followup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: currentSession.session_id,
        message: input
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    currentSession.history = data.history;

    renderChatHistory(data.history);
    document.getElementById('chatInput').value = '';

  } catch (error) {
    alert(`Error: ${error.message}`);
  } finally {
    btn.disabled = false;
  }
}

function renderChatHistory(history) {
  const container = document.getElementById('chatHistory');
  container.innerHTML = '';

  history.forEach((msg, index) => {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${msg.role}`;
    
    if (index === 0) {
      msgDiv.innerHTML = `
        <div class="message-header">Initial Query</div>
        <div class="message-content">${escapeHtml(msg.content)}</div>
      `;
    } else {
      msgDiv.innerHTML = `
        <div class="message-header">${msg.role === 'user' ? 'You' : 'Assistant'}</div>
        <div class="message-content">${escapeHtml(msg.content)}</div>
      `;
    }
    
    container.appendChild(msgDiv);
  });

  container.scrollTop = container.scrollHeight;
}

async function executeFork() {
  if (!currentSession) return;

  const newMode = modes[forkModeIndex];
  const newTone = tones[forkToneIndex];
  const newGain = forkGainValue;

  try {
    const response = await fetch(`${API_URL}/chat/fork`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: currentSession.session_id,
        mode: newMode,
        tone: newTone,
        gain: newGain
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    currentSession = data;

    // Update chat display
    document.getElementById('chatMode').textContent = newMode.toUpperCase();
    document.getElementById('chatTone').textContent = newTone.toUpperCase();
    document.getElementById('chatGain').textContent = newGain;
    
    // Sync fork knobs with new session values
    forkModeIndex = modes.indexOf(newMode);
    forkToneIndex = tones.indexOf(newTone);
    forkGainValue = newGain;
    
    renderChatHistory(data.history);

  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

function toggleForkControls() {
  const forkControls = document.querySelector('.fork-controls');
  forkControls.style.display = forkControls.style.display === 'none' ? 'block' : 'none';
}

function newQuery() {
  // Reset state
  currentSession = null;
  ensembleOutputs = [];
  
  // Reset UI
  document.getElementById('signalInput').value = '';
  document.getElementById('outputContainer').innerHTML = '';
  document.getElementById('chatInterface').classList.remove('active');
  document.getElementById('initialSection').style.display = 'block';
  document.querySelector('.mode-toggle').style.display = 'flex';
  
  // Focus input
  document.getElementById('signalInput').focus();
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  initializeKnobs();
  loadModels();
  loadKnobs();
  
  // Keyboard shortcuts
  document.getElementById('signalInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.shiftKey) {
      e.preventDefault();
      distortSignal();
    }
  });

  document.getElementById('chatInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  });
});
