/**
 * GridGuard AI — Frontend Application
 * =====================================
 * Vanilla JS, no frameworks, no CDN dependencies.
 * All risk data is fetched from the local FastAPI backend.
 * Risk calculations are NEVER duplicated here — the API owns all scoring.
 *
 * API endpoints used:
 *   GET  /api/risk/summary            → summary cards + grid status
 *   GET  /api/equipment               → asset table + distribution bars
 *   GET  /api/risk/top?n=10           → top-risk assets table
 *   GET  /api/outage-risk             → zone outage bars
 *   GET  /api/equipment/{id}          → detail panel (scores + impact + recs)
 *   POST /api/copilot                 → operations copilot chat
 *
 * Copilot label displayed verbatim from API response "model" field.
 * Impact disclaimer displayed verbatim from API response "_note" field.
 */

'use strict';

// ── API base (same origin — FastAPI serves both API and static files) ────────
const API = '';

// ── State ────────────────────────────────────────────────────────────────────
let allEquipment = [];      // from GET /api/equipment
let selectedId   = null;    // currently selected asset_id

// ── Utility helpers ──────────────────────────────────────────────────────────

function badgeHtml(label) {
  return `<span class="badge badge-${label}">${label}</span>`;
}

function scoreCellHtml(score, label) {
  return `<span class="score-cell">
    <span class="score-num">${score.toFixed(1)}</span>
    ${badgeHtml(label)}
  </span>`;
}

function zoneColor(avg) {
  if (avg >= 81) return 'var(--critical)';
  if (avg >= 61) return 'var(--high)';
  if (avg >= 31) return 'var(--medium)';
  return 'var(--low)';
}

function fmt(n, decimals = 0) {
  return Number(n).toLocaleString('en-US', { maximumFractionDigits: decimals });
}

async function fetchJson(path) {
  const res = await fetch(API + path);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${path}`);
  return res.json();
}

function showError(msg) {
  const el = document.getElementById('error-banner');
  el.textContent = '⚠ ' + msg;
  el.style.display = 'block';
}

// ── Loading overlay ──────────────────────────────────────────────────────────

function hideLoading() {
  const el = document.getElementById('loading-overlay');
  if (el) el.style.display = 'none';
}

// ── 1. Summary cards + grid status header ───────────────────────────────────
// Endpoint: GET /api/risk/summary

async function loadSummary() {
  const s = await fetchJson('/api/risk/summary');

  document.getElementById('card-total').textContent    = s.total_assets;
  document.getElementById('card-crit-eq').textContent  = s.critical_equipment;
  document.getElementById('card-high-eq').textContent  = s.high_equipment;
  document.getElementById('card-crit-out').textContent = s.critical_outage;
  document.getElementById('card-avg').textContent      = s.avg_equipment_risk_score.toFixed(1);

  const statusEl = document.getElementById('grid-status');
  if (s.critical_equipment >= 5) {
    statusEl.textContent = `⚠ CRITICAL ALERTS — ${s.critical_equipment} assets critical`;
    statusEl.className = 'status-critical';
  } else if (s.high_equipment >= 5) {
    statusEl.textContent = `⚡ HIGH ALERTS — ${s.high_equipment} assets at high risk`;
    statusEl.className = 'status-high';
  } else {
    statusEl.textContent = `✓ Grid monitoring active — ${s.total_assets} assets tracked`;
  }
}

// ── 2. Risk distribution bars ────────────────────────────────────────────────
// Endpoint: GET /api/equipment (uses labels on all 50 assets)

function renderDistribution(equipment) {
  const eq  = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
  const out = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
  equipment.forEach(a => {
    eq[a.equipment_risk_label]++;
    out[a.outage_risk_label]++;
  });
  const total = equipment.length;
  ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].forEach(lbl => {
    const eqPct  = (eq[lbl]  / total * 100).toFixed(1);
    const outPct = (out[lbl] / total * 100).toFixed(1);
    const eqEl  = document.getElementById(`eq-bar-${lbl.toLowerCase()}`);
    const outEl = document.getElementById(`out-bar-${lbl.toLowerCase()}`);
    const eqCnt  = document.getElementById(`eq-cnt-${lbl.toLowerCase()}`);
    const outCnt = document.getElementById(`out-cnt-${lbl.toLowerCase()}`);
    if (eqEl)  { eqEl.style.width  = eqPct  + '%'; }
    if (outEl) { outEl.style.width = outPct + '%'; }
    if (eqCnt)  eqCnt.textContent  = eq[lbl];
    if (outCnt) outCnt.textContent = out[lbl];
  });
}

// ── 3. Top vulnerable assets table ──────────────────────────────────────────
// Endpoint: GET /api/risk/top?n=10

async function loadTopAssets() {
  const top = await fetchJson('/api/risk/top?n=10');
  const tbody = document.getElementById('top-assets-body');
  tbody.innerHTML = '';
  top.forEach(a => {
    const tr = document.createElement('tr');
    tr.dataset.id = a.asset_id;
    tr.innerHTML = `
      <td>
        <div class="asset-name">${a.name}</div>
        <div class="asset-type">${a.type}</div>
      </td>
      <td>${a.zone}</td>
      <td>${scoreCellHtml(a.equipment_risk_score, a.equipment_risk_label)}</td>
      <td>${scoreCellHtml(a.outage_risk_score, a.outage_risk_label)}</td>
    `;
    tr.addEventListener('click', () => selectAsset(a.asset_id));
    tbody.appendChild(tr);
  });
}

// ── 4. Full equipment table (for full list below top table) ──────────────────
// Endpoint: GET /api/equipment

async function loadAllEquipment() {
  allEquipment = await fetchJson('/api/equipment');
  renderDistribution(allEquipment);
}

// ── 5 & 6. Asset detail + recommendations ───────────────────────────────────
// Endpoint: GET /api/equipment/{asset_id}
// (includes recommendations[] and impact{} inline)

async function selectAsset(assetId) {
  selectedId = assetId;

  // Highlight selected row in both tables
  document.querySelectorAll('tbody tr').forEach(tr => {
    tr.classList.toggle('selected', tr.dataset.id === assetId);
  });

  const panel = document.getElementById('detail-panel');
  const placeholder = document.getElementById('detail-placeholder');
  panel.classList.add('visible');
  placeholder && (placeholder.style.display = 'none');

  // Show loading state
  document.getElementById('detail-body').innerHTML =
    '<div class="detail-placeholder">Loading asset data…</div>';

  try {
    const a = await fetchJson(`/api/equipment/${encodeURIComponent(assetId)}`);
    renderDetail(a);
  } catch (e) {
    document.getElementById('detail-body').innerHTML =
      `<div class="detail-placeholder" style="color:var(--critical)">Failed to load asset: ${e.message}</div>`;
  }
}

function renderDetail(a) {
  const imp  = a.impact || {};
  const recs = a.recommendations || [];

  // Divergence callout: equipment LOW/MEDIUM but outage HIGH/CRITICAL
  const eqLow  = ['LOW', 'MEDIUM'].includes(a.equipment_risk_label);
  const outHigh = ['HIGH', 'CRITICAL'].includes(a.outage_risk_label);
  const divergenceHtml = (eqLow && outHigh) ? `
    <div class="disclaimer" style="border-color:var(--high);margin-bottom:12px;">
      <strong style="color:var(--high)">⚡ Risk Divergence Detected</strong><br>
      This asset has <strong>${a.equipment_risk_label}</strong> equipment failure risk
      but <strong>${a.outage_risk_label}</strong> outage risk — driven by high asset criticality,
      outage history, and/or severe weather exposure rather than equipment condition.
    </div>` : '';

  document.getElementById('detail-body').innerHTML = `
    <div class="detail-title">${a.name}</div>
    <div class="detail-subtitle">${a.type} &middot; ${a.zone} &middot; Asset ID: ${a.asset_id}</div>

    ${divergenceHtml}

    <div class="risk-scores-row">
      <div class="score-block">
        <div class="score-block-label">Equipment Failure Risk</div>
        <div class="score-block-value">${Number(a.equipment_risk_score).toFixed(1)}<span style="font-size:13px;color:var(--muted)">/100</span></div>
        <div class="score-block-badge">${badgeHtml(a.equipment_risk_label)}</div>
      </div>
      <div class="score-block">
        <div class="score-block-label">Outage Risk</div>
        <div class="score-block-value">${Number(a.outage_risk_score).toFixed(1)}<span style="font-size:13px;color:var(--muted)">/100</span></div>
        <div class="score-block-badge">${badgeHtml(a.outage_risk_label)}</div>
      </div>
    </div>

    <div class="section-title" style="margin-bottom:8px;">Impact Analysis</div>
    <div class="impact-grid">
      <div class="impact-item">
        <div class="impact-item-label">Customers Affected</div>
        <div class="impact-item-value">${fmt(imp.customers_affected)}</div>
      </div>
      <div class="impact-item">
        <div class="impact-item-label">Critical Facilities</div>
        <div class="impact-item-value">${imp.critical_facilities}</div>
      </div>
      <div class="impact-item">
        <div class="impact-item-label">Est. Downtime</div>
        <div class="impact-item-value">${imp.estimated_downtime_hours}h</div>
      </div>
      <div class="impact-item">
        <div class="impact-item-label">Est. Energy Loss</div>
        <div class="impact-item-value">${fmt(imp.estimated_energy_loss_mwh, 1)} MWh</div>
      </div>
      <div class="impact-item" style="grid-column:1/-1">
        <div class="impact-item-label">Est. Economic Impact</div>
        <div class="impact-item-value" style="color:var(--high)">$${fmt(imp.estimated_economic_impact_usd)}</div>
      </div>
    </div>

    <div class="disclaimer">
      <strong>⚠ Synthetic Demo Estimates</strong><br>
      ${imp._note || 'All impact figures are synthetic demo estimates for illustration only.'}
    </div>

    <div class="section-title" style="margin-bottom:8px;">Preventive Recommendations</div>
    <ul class="recs-list">
      ${recs.map(r => `<li>${r}</li>`).join('')}
    </ul>
  `;
}

// ── 7. Outage risk by zone ───────────────────────────────────────────────────
// Endpoint: GET /api/outage-risk

async function loadOutageZones() {
  const zones = await fetchJson('/api/outage-risk');
  const container = document.getElementById('zone-list');
  container.innerHTML = '';
  zones.forEach(z => {
    const pct = Math.min(z.avg_outage_risk_score, 100).toFixed(1);
    const div = document.createElement('div');
    div.className = 'zone-row';
    div.innerHTML = `
      <div class="zone-top">
        <span class="zone-name">${z.zone}</span>
        <span style="font-size:12px;color:${zoneColor(z.avg_outage_risk_score)};font-weight:600">${pct}/100</span>
      </div>
      <div class="zone-track">
        <div class="zone-fill" style="width:${pct}%;background:${zoneColor(z.avg_outage_risk_score)}"></div>
      </div>
      <div class="zone-meta">${z.assets_at_high_or_critical} assets at HIGH/CRITICAL &middot; max ${z.max_outage_risk_score.toFixed(1)}</div>
    `;
    container.appendChild(div);
  });
}

// ── 8. Copilot ───────────────────────────────────────────────────────────────
// Endpoint: POST /api/copilot

function initCopilot() {
  const input  = document.getElementById('copilot-input');
  const send   = document.getElementById('copilot-send');
  const msgs   = document.getElementById('copilot-messages');
  const labelEl = document.getElementById('copilot-model-label');

  async function sendQuestion() {
    const q = input.value.trim();
    if (!q) return;
    input.value = '';
    send.disabled = true;

    appendMsg('user', q, msgs);
    const thinking = appendMsg('bot', '…', msgs);
    thinking.classList.add('msg-thinking');
    msgs.scrollTop = msgs.scrollHeight;

    try {
      const res = await fetch(API + '/api/copilot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json();
      thinking.remove();
      appendMsg('bot', data.answer, msgs);
      // Update model label verbatim from API
      if (labelEl && data.model) labelEl.textContent = data.model;
    } catch (e) {
      thinking.remove();
      appendMsg('bot', 'Error: could not reach the API. Is the server running?', msgs);
    } finally {
      send.disabled = false;
      msgs.scrollTop = msgs.scrollHeight;
    }
  }

  send.addEventListener('click', sendQuestion);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') sendQuestion(); });
}

function appendMsg(role, text, container) {
  const div = document.createElement('div');
  div.className = `msg msg-${role}`;
  div.textContent = text;
  container.appendChild(div);
  return div;
}

// ── Bootstrap ────────────────────────────────────────────────────────────────

async function init() {
  try {
    // Load all data sources in parallel where possible
    await Promise.all([
      loadSummary(),
      loadAllEquipment(),   // populates dist bars + sets allEquipment
      loadTopAssets(),
      loadOutageZones(),
    ]);
    hideLoading();
    initCopilot();

    // Auto-select the highest-risk asset for demo impact
    const top = await fetchJson('/api/risk/top?n=1');
    if (top.length) selectAsset(top[0].asset_id);

  } catch (e) {
    hideLoading();
    showError('Could not load data from the API. Make sure the backend is running: uvicorn main:app --reload  (' + e.message + ')');
  }
}

document.addEventListener('DOMContentLoaded', init);
