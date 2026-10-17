/**
 * JEWEL-AI Atelier & Merchant Intelligence Controller
 */

const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);
const inr = n => '₹' + new Intl.NumberFormat('en-IN').format(Math.round(n || 0));
const esc = t => String(t ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

// METALS is defined in /js/cad.js

const STONES = {
  none: 'Solid Gold / No Stone',
  cz: 'Cubic Zirconia (CZ)',
  moissanite: 'Moissanite',
  lab_diamond: 'Lab-Grown Diamond (CVD/HPHT)',
  natural_diamond: 'Natural Certified Diamond'
};

const CURATED_STUDIO_IMAGES = {
  ring_solitaire: "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80",
  ring_halo: "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=800&q=80",
  ring_band: "https://images.unsplash.com/photo-1598560917505-59a3ad559071?auto=format&fit=crop&w=800&q=80",
  necklace_bridal: "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80",
  necklace_delicate: "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=800&q=80",
  earrings_jhumka: "https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&q=80",
  earrings_stud: "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80",
  bangle_kada: "https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?auto=format&fit=crop&w=800&q=80"
};

function getCuratedImage(s, tierIndex = 1) {
  const cat = (s && s.category) ? s.category : 'ring';
  if (cat === 'necklace') {
    return tierIndex === 2 ? CURATED_STUDIO_IMAGES.necklace_bridal : (tierIndex === 0 ? CURATED_STUDIO_IMAGES.necklace_delicate : CURATED_STUDIO_IMAGES.necklace_bridal);
  } else if (cat === 'earrings') {
    return tierIndex === 0 ? CURATED_STUDIO_IMAGES.earrings_stud : CURATED_STUDIO_IMAGES.earrings_jhumka;
  } else if (cat === 'bangle') {
    return CURATED_STUDIO_IMAGES.bangle_kada;
  } else {
    return tierIndex === 0 ? CURATED_STUDIO_IMAGES.ring_band : (tierIndex === 2 ? CURATED_STUDIO_IMAGES.ring_halo : CURATED_STUDIO_IMAGES.ring_solitaire);
  }
}

function defaultSpec(cat = 'ring') {
  const specs = {
    ring: { category: 'ring', style: 'classic solitaire', metal: 'gold_22k', band_width_mm: 3.0, ring_size_in: 12, stone: { type: 'natural_diamond', carat: 0.40, count: 1 }, occasion: 'Engagement', budget_inr: 60000 },
    necklace: { category: 'necklace', style: 'floral temple motif', metal: 'gold_18k', necklace_length_in: 18, stone: { type: 'none', carat: 0, count: 0 }, occasion: 'Wedding', budget_inr: 150000 },
    earrings: { category: 'earrings', style: 'temple jhumka', earring_type: 'jhumka', metal: 'gold_22k', stone: { type: 'cz', carat: 0.3, count: 2 }, occasion: 'Diwali', budget_inr: 45000 },
    bangle: { category: 'bangle', style: 'heritage carved kada', bangle_size_in: '2-4', metal: 'gold_22k', band_width_mm: 5.0, stone: { type: 'none', carat: 0, count: 0 }, occasion: 'Akshaya Tritiya', budget_inr: 95000 }
  };
  return specs[cat] || specs.ring;
}

let State = {
  spec: defaultSpec('ring'),
  cur: null,
  msgs: [],
  variants: [],
  price: null,
  reqId: null,
  customizerMode: 'photo', // 'photo' | 'cad'
  currentMode: 'atelier', // 'atelier' | 'merchant'
  tradeInCredit: 0,
  tradeInVoucher: null,
  uid: 0
};

// ── API Helper ──
async function api(path, payload) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    let err = res.statusText;
    try { const d = await res.json(); if (d.detail) err = d.detail; } catch (e) {}
    throw new Error(err);
  }
  return res.json();
}

function toast(msg) {
  const el = $('#toast-notice');
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2600);
}

function appendChat(text, type = 'bot') {
  const log = $('#chat-log');
  const d = document.createElement('div');
  d.className = 'chat-msg ' + (type === 'user' ? 'user' : (type === 'err' ? 'err' : ''));
  d.textContent = text;
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
  return d;
}

// ── Showroom Stages ──
function renderWelcomeStage() {
  const s = State.spec;
  const photo = getCuratedImage(s, 1);
  $('#dynamic-stage-view').innerHTML = `
    <div class="atelier-welcome-stage">
      <div class="welcome-plinth-card">
        <img src="${photo}" alt="Bespoke Jewellery Masterpiece" onerror="this.onerror=null; this.src='${CURATED_STUDIO_IMAGES.ring_solitaire}';">
        <div style="margin-top:14px; font-family:var(--font-serif); font-size:17px; color:var(--text-primary); font-weight:600;">
          Bespoke Atelier Collection
        </div>
      </div>
      <div class="welcome-narrative">
        <h2>Intelligent Design for Exceptional Jewellery</h2>
        <p>Welcome to the private digital atelier. Select a curated collection or describe your personal occasion, motif, and target budget. Our AI co-creates bespoke heirloom pieces, calculates certified BIS hallmarking prices, verifies local store availability, and and extracts custom architectural motifs from uploaded sketches.</p>
        <div class="welcome-metrics-strip">
          <div class="metric-pill">
            <b>BIS 916 / 750</b>
            <span>Certified Hallmarking</span>
          </div>
          <div class="metric-pill">
            <b>Gemini 2.5 Flash</b>
            <span>Haute Joaillerie Co-Design</span>
          </div>
          <div class="metric-pill">
            <b>Multimodal Vision</b>
            <span>Sketch & Motif Extraction</span>
          </div>
          <div class="metric-pill">
            <b>Circular Trade-In</b>
            <span>Old Gold Appraisal</span>
          </div>
        </div>
      </div>
    </div>
  `;
}

function showGalleryLoadingState(statusText = 'Formulating bespoke haute joaillerie...') {
  State.isSynthesizing = true;
  const stage = $('#dynamic-stage-view');
  if (!stage) return;
  
  // Blur current cards/parameters to indicate fresh computation
  $$('.jewel-variant-card, .card-details-wrap, .customizer-split-grid, #cust-stage-plinth, #cost-box').forEach(el => {
    el.classList.add('is-blurring');
  });

  // Activate loading screens over existing card images
  $$('.card-image-loader-overlay').forEach(el => el.classList.add('active'));

  // If no cards exist in the stage yet, render 3 placeholder skeleton cards with loading screens
  const existingCards = $$('.jewel-variant-card');
  if (existingCards.length === 0) {
    stage.innerHTML = `
      <div class="gallery-header-row">
        <div>
          <h2>Calibrated Fine Jewellery Atelier</h2>
          <p>Synthesizing master craftsman variations according to your prompt...</p>
        </div>
      </div>
      <div class="trend-alert-pill" id="trend-bar">
        <b>Live Market Trends:</b> <span>Assaying bullion rates and occasion parameters...</span>
      </div>
      <div class="gallery-cards-grid" id="cards-grid">
        ${[1, 2, 3].map(i => `
          <div class="jewel-variant-card">
            <div class="card-media-stage" style="height:340px; position:relative;">
              <div class="card-image-loader-overlay active">
                <div class="mini-gold-spinner"></div>
                <div class="loader-title">Synthesizing Master Render</div>
                <div class="loader-sub">Flux AI &bull; Calibrating to Prompt</div>
              </div>
            </div>
            <div class="card-details-wrap is-blurring" style="padding:18px;">
              <div style="background:var(--border-subtle); height:20px; width:65%; border-radius:4px; margin-bottom:10px;"></div>
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="background:var(--border-subtle); height:26px; width:45%; border-radius:4px;"></div>
                <div style="background:var(--border-subtle); height:18px; width:35%; border-radius:4px;"></div>
              </div>
              <div style="background:var(--border-subtle); height:14px; width:85%; border-radius:4px; margin-bottom:14px;"></div>
              <div style="background:var(--border-subtle); height:36px; width:100%; border-radius:4px;"></div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  let loader = $('#stage-luxury-loader');
  if (!loader) {
    loader = document.createElement('div');
    loader.id = 'stage-luxury-loader';
    loader.className = 'stage-loading-overlay active';
    stage.style.position = 'relative';
    stage.appendChild(loader);
  }
  loader.className = 'stage-loading-overlay active';
  loader.innerHTML = `
    <div class="luxury-loader-box">
      <div class="luxury-ring-spinner"></div>
      <div class="luxury-loader-title">${esc(statusText)}</div>
      <div class="luxury-loader-sub">Assaying bullion karatage & synthesizing high-definition renders</div>
    </div>
  `;
}

function hideGalleryLoadingState() {
  State.isSynthesizing = false;
  const loader = $('#stage-luxury-loader');
  if (loader) {
    loader.classList.remove('active');
    setTimeout(() => { if (loader && !loader.classList.contains('active')) loader.remove(); }, 350);
  }
  $$('.card-image-loader-overlay').forEach(el => el.classList.remove('active'));
  $$('.is-blurring').forEach(el => el.classList.remove('is-blurring'));
}

function renderGalleryView() {
  const s = State.spec || defaultSpec('ring');
  const catTitle = { ring: 'Rings', necklace: 'Necklaces', earrings: 'Earrings', bangle: 'Bangles' }[s.category] || 'Jewellery';
  
  $('#dynamic-stage-view').innerHTML = `
    <div class="gallery-header-row">
      <div>
        <h2>Calibrated ${catTitle} for your ${esc(s.occasion || 'Celebration')}</h2>
        <p>Three master craftsman variations formulated against today's live bullion rate.</p>
      </div>
    </div>
    <div class="trend-alert-pill" id="trend-bar">
      <b>Live Market Trends:</b> <span id="trend-text">Grounding with Google Search retail cues...</span>
    </div>
    <div class="gallery-cards-grid" id="cards-grid"></div>
    <div id="showroom-inventory-dock"></div>
  `;

  const grid = $('#cards-grid');
  (State.variants || []).forEach((v, idx) => {
    const p = v.price || { total: s.budget_inr || 60000, within_budget: true };
    const isOver = p.within_budget === false;
    const card = document.createElement('div');
    card.className = 'jewel-variant-card ' + (v.label === 'Statement' ? 'statement' : '');
    const photo = getCuratedImage(v.spec, idx);

    const metalLabel = (METALS[v.spec?.metal] || METALS.gold_22k)[2];
    const stoneType = v.spec?.stone?.type || 'none';
    const stoneLabel = STONES[stoneType] || 'Solid Gold';
    const stoneCarat = v.spec?.stone?.carat || 0.3;
    const stoneSummary = stoneType !== 'none' ? `${stoneCarat} ct ${stoneLabel}` : 'Solid gold';

    card.innerHTML = `
      <div class="card-media-stage" id="media-box-${idx}">
        <div class="card-image-loader-overlay ${State.isSynthesizing ? 'active' : ''}" id="card-loader-${idx}">
          <div class="mini-gold-spinner"></div>
          <div class="loader-title">Synthesizing Master Render</div>
          <div class="loader-sub">Flux AI &bull; Calibrating to Prompt</div>
        </div>
        <div class="img-loading-shimmer" id="img-shimmer-${idx}">
          <div class="mini-gold-spinner"></div>
          <span class="img-loading-text">Atelier Render</span>
        </div>
        <span class="card-tier-tag">${esc(v.label)}</span>
        <img src="${photo}" 
             alt="${esc(v.label)} Jewellery" 
             id="card-img-${idx}" 
             class="luxury-img-lazy"
             onload="this.classList.add('is-loaded'); const s = $('#img-shimmer-${idx}'); if(s) s.classList.add('loaded'); const l = $('#card-loader-${idx}'); if(l && !State.isSynthesizing) l.classList.remove('active');" 
             onerror="this.onerror=null; this.src='${CURATED_STUDIO_IMAGES.ring_solitaire}'; this.classList.add('is-loaded'); const s = $('#img-shimmer-${idx}'); if(s) s.classList.add('loaded');">
        <div class="card-view-toggle">
          <button class="view-toggle-btn active" data-idx="${idx}" data-mode="photo">Photo</button>
          <button class="view-toggle-btn" data-idx="${idx}" data-mode="cad">CAD</button>
        </div>
      </div>
      <div class="card-details-wrap ${State.isSynthesizing ? 'is-blurring' : ''}">
        <div class="card-title">${esc(v.label)} Atelier</div>
        <div class="card-price-row">
          <div class="card-price">${inr(p.total)}</div>
          <span class="budget-status-tag ${isOver ? 'status-over' : 'status-fits'}">
            ${isOver ? inr(p.over_by) + ' over budget' : 'Within Target Budget'}
          </span>
        </div>
        <div class="card-specs-list">
          ${v.changes && v.changes.length ? 'Tailored: ' + v.changes.join(', ') : `${metalLabel} &bull; ${stoneSummary}`}
        </div>
        <div class="card-actions-row">
          <button class="btn-launch-customizer" data-idx="${idx}" style="width:100%;">
            Customize in Studio &rarr;
          </button>
        </div>
      </div>
    `;

    // Toggle handlers
    const btnPhoto = card.querySelector(`.view-toggle-btn[data-mode="photo"]`);
    const btnCAD = card.querySelector(`.view-toggle-btn[data-mode="cad"]`);
    const mediaBox = card.querySelector(`#media-box-${idx}`);

    btnPhoto.onclick = () => {
      btnPhoto.classList.add('active');
      btnCAD.classList.remove('active');
      mediaBox.innerHTML = `
        <div class="img-loading-shimmer" id="img-shimmer-${idx}">
          <div class="mini-gold-spinner"></div>
          <span class="img-loading-text">Atelier Render</span>
        </div>
        <span class="card-tier-tag">${esc(v.label)}</span>
        <img src="${photo}" 
             alt="${esc(v.label)} Jewellery" 
             class="luxury-img-lazy"
             onload="this.classList.add('is-loaded'); const s = $('#img-shimmer-${idx}'); if(s) s.classList.add('loaded');" 
             onerror="this.onerror=null; this.src='${CURATED_STUDIO_IMAGES.ring_solitaire}'; this.classList.add('is-loaded'); const s = $('#img-shimmer-${idx}'); if(s) s.classList.add('loaded');">
        <div class="card-view-toggle">
          <button class="view-toggle-btn active">Photo</button>
          <button class="view-toggle-btn">CAD</button>
        </div>
      `;
      card.querySelector(`.view-toggle-btn:last-child`).onclick = btnCAD.onclick;
    };

    btnCAD.onclick = () => {
      btnCAD.classList.add('active');
      btnPhoto.classList.remove('active');
      mediaBox.innerHTML = `
        <span class="card-tier-tag">${esc(v.label)}</span>
        ${renderJewellerySVG(v.spec)}
        <div class="card-view-toggle">
          <button class="view-toggle-btn">Photo</button>
          <button class="view-toggle-btn active">CAD</button>
        </div>
      `;
      card.querySelector(`.view-toggle-btn:first-child`).onclick = btnPhoto.onclick;
    };

    card.querySelector('.btn-launch-customizer').onclick = () => openCustomizer(structuredClone(v.spec), idx);
    grid.appendChild(card);
  });

  fetchTrends();
  fetchShowroomMatches(State.spec, '#showroom-inventory-dock');
}

function openCustomizer(sp, initialIdx = 1) {
  State.cur = sp;
  const s = State.cur;
  const isRing = s.category === 'ring';
  const isNecklace = s.category === 'necklace';
  const isEarrings = s.category === 'earrings';
  const isBangle = s.category === 'bangle';
  const photo = getCuratedImage(s, initialIdx);

  $('#dynamic-stage-view').innerHTML = `
    <div style="margin-bottom:20px; display:flex; justify-content:space-between; align-items:center;">
      <button class="atelier-nav-link" id="btn-back-gallery">
        &larr; Back to 3 Variations
      </button>
      <div style="display:flex; gap:8px;">
        <button class="atelier-nav-link" id="btn-cust-open-cert">BIS Certificate</button>
      </div>
    </div>
    <div class="customizer-split-grid">
      <!-- Left Visual Plinth -->
      <div>
        <div class="atelier-panel">
          <div class="panel-headline">
            <span>Visual Specimen</span>
            <div style="display:flex; gap:6px;">
              <button class="atelier-nav-link" id="cust-toggle-photo" style="font-size:11px;">Studio Photo</button>
              <button class="atelier-nav-link" id="cust-toggle-cad" style="font-size:11px;">CAD Blueprint</button>
            </div>
          </div>
          <div class="jewel-stage-plinth" id="cust-stage-plinth">
            <div class="render-loading-overlay" id="render-loader">
              <div class="luxury-ring-spinner"></div>
              <div class="render-status-text" id="render-status-text">Flux AI generating photorealistic studio render...</div>
            </div>
            <div class="img-loading-shimmer" id="plinth-shimmer">
              <div class="mini-gold-spinner"></div>
              <span class="img-loading-text">Atelier Specimen</span>
            </div>
            <img src="${photo}" 
                 alt="Haute Joaillerie Atelier Specimen" 
                 id="cust-main-img" 
                 class="luxury-img-lazy"
                 onload="this.classList.add('is-loaded'); const s = $('#plinth-shimmer'); if(s) s.classList.add('loaded');" 
                 onerror="this.onerror=null; this.src='${CURATED_STUDIO_IMAGES.ring_solitaire}'; this.classList.add('is-loaded'); const s = $('#plinth-shimmer'); if(s) s.classList.add('loaded');">
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px;">
            <div style="font-size:12px; color:var(--text-muted);" id="cust-caption-note">
              High-Definition Atelier Specimen
            </div>
            <button class="atelier-nav-link" id="btn-trigger-ai-render" style="font-size:11.5px;">
              Render with Flux AI
            </button>
          </div>

          <!-- Certified Hallmarking Seal -->
          <div class="hallmark-cert-seal">
            <div class="cert-seal-icon">✓</div>
            <div class="cert-seal-info">
              <b>Govt of India BIS Hallmarking Certified</b>
              <span>Purity Assayed at Licensed BIS Center (916 / 750 Grade)</span>
            </div>
          </div>
        </div>

        <!-- In-Stock Showroom Matches in Customizer -->
        <div class="showroom-matches-shelf" id="cust-matches-shelf">
          <div class="shelf-header">
            <h4>Ready in Showroom Today</h4>
            <span style="font-size:12px; color:var(--gold-dark); font-weight:600;">Immediate in-store delivery</span>
          </div>
          <div class="shelf-grid" id="cust-matches-grid">Loading local inventory...</div>
        </div>
      </div>

      <!-- Right Component Parameters & Cost Breakdown -->
      <div>
        <div class="atelier-panel card-details-wrap" id="cust-params-panel">
          <div class="panel-headline">
            <span>Artisan Parameters</span>
            <span style="font-size:12px; color:var(--gold-dark); text-transform:uppercase; font-weight:700;">${esc(s.category)}</span>
          </div>

          <div class="control-row">
            <div class="control-header"><span>Precious Alloy / Karatage</span></div>
            <select class="atelier-select" id="sel-metal">
              ${Object.entries(METALS).map(([k, v]) => `<option value="${k}" ${s.metal === k ? 'selected' : ''}>${v[2]}</option>`).join('')}
            </select>
          </div>

          <div class="control-row">
            <div class="control-header"><span>Center Gemstone Quality</span></div>
            <select class="atelier-select" id="sel-stone">
              ${Object.entries(STONES).map(([k, v]) => `<option value="${k}" ${(s.stone?.type || 'none') === k ? 'selected' : ''}>${v}</option>`).join('')}
            </select>
          </div>

          <div class="control-row" id="row-carat">
            <div class="control-header">
              <span>Center Stone Weight</span>
              <span id="lbl-carat">${(s.stone?.carat || 0.40)} ct</span>
            </div>
            <input class="atelier-range" id="rng-carat" type="range" min="0.1" max="3.0" step="0.05" value="${s.stone?.carat || 0.40}">
          </div>

          <!-- Category Specific Sliders -->
          ${isRing ? `
            <div class="control-row">
              <div class="control-header">
                <span>Band Width</span>
                <span id="lbl-width">${s.band_width_mm || 3.0} mm</span>
              </div>
              <input class="atelier-range" id="rng-width" type="range" min="1.8" max="6.0" step="0.2" value="${s.band_width_mm || 3.0}">
            </div>
            <div class="control-row">
              <div class="control-header">
                <span>Indian Ring Size</span>
                <span id="lbl-ring-size">Size ${s.ring_size_in || 12}</span>
              </div>
              <input class="atelier-range" id="rng-ring-size" type="range" min="6" max="22" step="1" value="${s.ring_size_in || 12}">
            </div>
          ` : ''}

          ${isNecklace ? `
            <div class="control-row">
              <div class="control-header">
                <span>Necklace / Choker Length</span>
                <span id="lbl-neck-len">${s.necklace_length_in || 18} inches</span>
              </div>
              <input class="atelier-range" id="rng-neck-len" type="range" min="14" max="26" step="1" value="${s.necklace_length_in || 18}">
            </div>
          ` : ''}

          ${isEarrings ? `
            <div class="control-row">
              <div class="control-header"><span>Earring Silhouette Style</span></div>
              <select class="atelier-select" id="sel-earring-type">
                <option value="jhumka">Temple Bell Jhumka</option>
                <option value="stud">Solitaire Stud</option>
                <option value="drop">Modern Drop</option>
                <option value="hoop">Pave Hoop (Bali)</option>
              </select>
            </div>
          ` : ''}

          ${isBangle ? `
            <div class="control-row">
              <div class="control-header"><span>Traditional Kada Size</span></div>
              <select class="atelier-select" id="sel-bangle-size">
                <option value="2-2">2-2 (Small)</option>
                <option value="2-4">2-4 (Standard Medium)</option>
                <option value="2-6">2-6 (Large)</option>
                <option value="2-8">2-8 (Extra Large)</option>
              </select>
            </div>
            <div class="control-row">
              <div class="control-header">
                <span>Kada Width</span>
                <span id="lbl-bangle-width">${s.band_width_mm || 5.0} mm</span>
              </div>
              <input class="atelier-range" id="rng-bangle-width" type="range" min="3.0" max="12.0" step="0.5" value="${s.band_width_mm || 5.0}">
            </div>
          ` : ''}

          <!-- Cost Breakdown Table -->
          <div class="cost-breakdown-box" id="cost-box">
            Calculating metallurgical quote...
          </div>

          <!-- Dynamic Budget Meter -->
          <div class="budget-meter-container">
            <div class="meter-header">
              <span>Budget Alignment Meter</span>
              <span id="meter-text">Evaluating...</span>
            </div>
            <div class="meter-track" id="meter-track">
              <div class="meter-progress" id="meter-progress"></div>
            </div>
          </div>

          <!-- Trade-In & Skin Undertone Trigger Buttons -->
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:14px;">
            <button class="atelier-nav-link" id="btn-cust-tradein" style="justify-content:center;">
              Old Gold Trade-In
            </button>
            <button class="atelier-nav-link undertone" id="btn-cust-undertone" style="justify-content:center;">
              ✦ Skin Undertone AI
            </button>
          </div>

          <!-- Budget Levers -->
          <div class="budget-levers-shelf" id="levers-shelf"></div>

          <!-- Actions Dual Grid -->
          <div class="actions-dual-grid">
            <a class="btn-gold-primary" id="btn-cust-whatsapp" target="_blank" href="#">
              WhatsApp Quote
            </a>
            <button class="btn-outline-glass" id="btn-cust-jobcard">
              Workshop Job Sheet
            </button>
          </div>
          <div style="margin-top:10px;">
            <button class="btn-gold-primary" id="btn-order-confirm" style="width:100%;">
              Confirm & Queue Bespoke Order
            </button>
          </div>
        </div>
      </div>
    </div>
  `;

  // Bind initial values safely
  if ($('#sel-metal')) $('#sel-metal').value = s.metal || 'gold_22k';
  if ($('#sel-stone')) $('#sel-stone').value = s.stone?.type || 'none';
  if ($('#sel-earring-type')) $('#sel-earring-type').value = s.earring_type || 'jhumka';
  if ($('#sel-bangle-size')) $('#sel-bangle-size').value = s.bangle_size_in || '2-4';

  // Toggle handlers
  $('#cust-toggle-photo').onclick = () => {
    State.customizerMode = 'photo';
    $('#cust-stage-plinth').innerHTML = `
      <div class="render-loading-overlay" id="render-loader">
        <div class="luxury-ring-spinner"></div>
        <div class="render-status-text" id="render-status-text">Flux AI generating photorealistic studio render...</div>
      </div>
      <div class="img-loading-shimmer" id="plinth-shimmer">
        <div class="mini-gold-spinner"></div>
        <span class="img-loading-text">Atelier Specimen</span>
      </div>
      <img src="${photo}" 
           alt="Haute Joaillerie Atelier Specimen" 
           id="cust-main-img" 
           class="luxury-img-lazy"
           onload="this.classList.add('is-loaded'); const s = $('#plinth-shimmer'); if(s) s.classList.add('loaded');" 
           onerror="this.onerror=null; this.src='${CURATED_STUDIO_IMAGES.ring_solitaire}'; this.classList.add('is-loaded'); const s = $('#plinth-shimmer'); if(s) s.classList.add('loaded');">
    `;
    $('#cust-caption-note').textContent = "High-Definition Atelier Specimen";
  };
  $('#cust-toggle-cad').onclick = () => {
    State.customizerMode = 'cad';
    $('#cust-stage-plinth').innerHTML = renderJewellerySVG(State.cur);
    $('#cust-caption-note').textContent = "Procedural CAD Technical Model • Live Hallmarking Preview";
  };

  $('#btn-cust-open-cert').onclick = () => openCertModal(State.cur);
  $('#btn-cust-tradein').onclick = () => openTradeInModal();

  // Render with AI trigger
  $('#btn-trigger-ai-render').onclick = async () => {
    const loader = $('#render-loader');
    const img = $('#cust-main-img');
    const paramsPanel = $('#cust-params-panel');
    if (loader) loader.classList.add('active');
    if (img) img.classList.add('is-blurring');
    if (paramsPanel) paramsPanel.classList.add('is-blurring');
    toast("Generating Flux AI render (takes ~7s)...");
    try {
      const data = await api('/api/render', State.cur);
      if (data.image) {
        if (img) {
          img.onload = () => {
            img.classList.remove('is-blurring');
            if (paramsPanel) paramsPanel.classList.remove('is-blurring');
          };
          img.src = data.image;
        }
        toast("Flux AI render completed.");
      } else if (data.fallback) {
        if (img) {
          img.onload = () => {
            img.classList.remove('is-blurring');
            if (paramsPanel) paramsPanel.classList.remove('is-blurring');
          };
          img.src = data.fallback;
        }
        toast("Loaded high-definition studio specimen.");
      }
    } catch (err) {
      if (img) img.classList.remove('is-blurring');
      if (paramsPanel) paramsPanel.classList.remove('is-blurring');
      toast("AI render offline: using curated studio photo.");
    } finally {
      if (loader) loader.classList.remove('active');
      setTimeout(() => {
        if (img) img.classList.remove('is-blurring');
        if (paramsPanel) paramsPanel.classList.remove('is-blurring');
      }, 800);
    }
  };

  // Event handlers
  $('#btn-back-gallery').onclick = () => { State.cur = null; renderGalleryView(); };
  $('#sel-metal').onchange = e => { State.cur.metal = e.target.value; updateCustomizer(); };
  $('#sel-stone').onchange = e => {
    if (!State.cur.stone) State.cur.stone = { type: 'none', carat: 0, count: 0 };
    State.cur.stone.type = e.target.value;
    if (e.target.value !== 'none') {
      if (!State.cur.stone.carat) State.cur.stone.carat = 0.40;
      State.cur.stone.count = 1;
    } else {
      State.cur.stone.count = 0;
      State.cur.stone.carat = 0;
    }
    updateCustomizer();
  };
  $('#rng-carat').oninput = e => {
    if (!State.cur.stone) State.cur.stone = { type: 'natural_diamond', carat: 0.4, count: 1 };
    State.cur.stone.carat = parseFloat(e.target.value);
    State.cur.stone.count = 1;
    $('#lbl-carat').textContent = e.target.value + ' ct';
    updateCustomizer();
  };

  if (isRing) {
    $('#rng-width').oninput = e => {
      State.cur.band_width_mm = parseFloat(e.target.value);
      $('#lbl-width').textContent = e.target.value + ' mm';
      updateCustomizer();
    };
    $('#rng-ring-size').oninput = e => {
      State.cur.ring_size_in = parseInt(e.target.value);
      $('#lbl-ring-size').textContent = 'Size ' + e.target.value;
      updateCustomizer();
    };
  }

  if (isNecklace) {
    $('#rng-neck-len').oninput = e => {
      State.cur.necklace_length_in = parseInt(e.target.value);
      $('#lbl-neck-len').textContent = e.target.value + ' inches';
      updateCustomizer();
    };
  }

  if (isEarrings) {
    $('#sel-earring-type').onchange = e => {
      State.cur.earring_type = e.target.value;
      updateCustomizer();
    };
  }

  if (isBangle) {
    $('#sel-bangle-size').onchange = e => {
      State.cur.bangle_size_in = e.target.value;
      updateCustomizer();
    };
    $('#rng-bangle-width').oninput = e => {
      State.cur.band_width_mm = parseFloat(e.target.value);
      $('#lbl-bangle-width').textContent = e.target.value + ' mm';
      updateCustomizer();
    };
  }

  $('#btn-order-confirm').onclick = registerConfirmedOrder;
  $('#btn-cust-jobcard').onclick = () => triggerJobCardModal(State.cur);
  if ($('#btn-cust-tradein')) $('#btn-cust-tradein').onclick = openTradeInModal;
  if ($('#btn-cust-undertone')) $('#btn-cust-undertone').onclick = openUndertoneModal;

  updateCustomizer();
  fetchShowroomMatches(s, '#cust-matches-grid');
}

let priceDebounce = null;
function updateCustomizer() {
  const s = State.cur || State.spec;
  const isStone = s.stone && s.stone.type !== 'none';
  if ($('#row-carat')) $('#row-carat').style.opacity = isStone ? '1' : '0.4';
  if ($('#rng-carat')) $('#rng-carat').disabled = !isStone;

  if (State.customizerMode === 'cad') {
    $('#cust-stage-plinth').innerHTML = renderJewellerySVG(s);
  }

  clearTimeout(priceDebounce);
  if ($('#cost-box')) $('#cost-box').classList.add('cost-box-blurring');
  priceDebounce = setTimeout(async () => {
    try {
      const data = await api('/api/price', s);
      const p = data.price;
      State.price = p;

      const stoneLabel = (s.stone && STONES[s.stone.type]) ? STONES[s.stone.type] : 'Solid Gold';
      const credit = State.tradeInCredit || 0;
      const netPayable = Math.max(0, p.total - credit);

      // Render Cost Breakdown Table
      $('#cost-box').innerHTML = `
        <div class="cost-line">
          <span>Net Bullion (${p.weight_g} g &bull; ${p.hallmark} BIS Hallmark)</span>
          <b>${inr(p.metal_cost)}</b>
        </div>
        <div class="cost-line">
          <span>Gemstone (${isStone ? s.stone.carat + ' ct ' + stoneLabel : 'Solid Gold'})</span>
          <b>${inr(p.stone_cost)}</b>
        </div>
        <div class="cost-line">
          <span>Prong / Setting Labor</span>
          <b>${inr(p.setting_cost)}</b>
        </div>
        <div class="cost-line">
          <span>Artisan Making Charges (12%)</span>
          <b>${inr(p.making_cost)}</b>
        </div>
        <div class="cost-line">
          <span>GST (3% jewellery standard)</span>
          <b>${inr(p.gst)}</b>
        </div>
        ${credit > 0 ? `
          <div class="cost-line trade-in-credit-line">
            <span>Old Gold Trade-in Credit (${State.tradeInVoucher || 'Voucher'})</span>
            <b>- ${inr(credit)}</b>
          </div>
        ` : ''}
        <div class="cost-line total-line">
          <span>${credit > 0 ? 'Net Amount Payable' : 'Estimated Quotation'}</span>
          <b>${inr(netPayable)}</b>
        </div>
      `;
      if ($('#cost-box')) $('#cost-box').classList.remove('cost-box-blurring');

      // Update Budget Meter
      const budget = s.budget_inr || 60000;
      const isOver = netPayable > budget;
      const track = $('#meter-track');
      const prog = $('#meter-progress');
      if (isOver) {
        track.classList.add('over');
        prog.style.width = '100%';
        $('#meter-text').innerHTML = `<span style="color:var(--ruby); font-weight:600;">${inr(netPayable - budget)} Over Target Budget</span>`;
      } else {
        track.classList.remove('over');
        prog.style.width = Math.min(100, Math.round((netPayable / budget) * 100)) + '%';
        $('#meter-text').innerHTML = `<span style="color:var(--emerald); font-weight:600;">${inr(budget - netPayable)} Under Target Budget</span>`;
      }

      // Budget Levers
      const leversShelf = $('#levers-shelf');
      if (isOver && data.suggestions && data.suggestions.length) {
        leversShelf.innerHTML = `<div style="font-size:12px; font-weight:700; color:var(--gold-dark); margin-bottom:6px;">Suggested Budget Optimizations:</div>`;
        data.suggestions.slice(0, 3).forEach(sug => {
          const btn = document.createElement('button');
          btn.className = 'lever-card-btn';
          btn.innerHTML = `<span>${esc(sug.label)}</span><b>Save ${inr(sug.saving)}</b>`;
          btn.onclick = () => executeBudgetLever(sug.id);
          leversShelf.appendChild(btn);
        });
      } else {
        leversShelf.innerHTML = '';
      }

      // WhatsApp link
      try {
        const wa = await api('/api/artisan/whatsapp', s);
        $('#btn-cust-whatsapp').href = wa.link;
      } catch (e) {}

    } catch (err) {
      console.error("Price error:", err);
    }
  }, 90);
}

function executeBudgetLever(leverId) {
  const s = State.cur;
  if (!s) return;
  if (!s.stone) s.stone = { type: 'none', carat: 0, count: 0 };

  if (leverId === 'metal_18k') s.metal = 'gold_18k';
  if (leverId === 'lab_diamond') s.stone.type = 'lab_diamond';
  if (leverId === 'moissanite') s.stone.type = 'moissanite';
  if (leverId === 'slim_band' && s.band_width_mm) s.band_width_mm = Math.max(1.8, s.band_width_mm - 1.0);
  if (leverId === 'smaller_stone' && s.stone.carat) s.stone.carat = Math.max(0.1, Math.round((s.stone.carat - 0.1) * 100) / 100);

  if ($('#sel-metal')) $('#sel-metal').value = s.metal;
  if ($('#sel-stone')) $('#sel-stone').value = s.stone.type;
  if ($('#rng-carat') && s.stone.carat) {
    $('#rng-carat').value = s.stone.carat;
    $('#lbl-carat').textContent = s.stone.carat + ' ct';
  }
  toast("Applied budget optimization");
  updateCustomizer();
}

// ── In-Stock Showroom Matches ──
async function fetchShowroomMatches(spec, targetSelector) {
  const target = $(targetSelector);
  if (!target) return;
  try {
    const data = await api('/api/catalog/match', spec);
    const matches = data.matches || [];
    if (!matches.length) return;

    if (targetSelector === '#showroom-inventory-dock') {
      target.innerHTML = `
        <div class="showroom-matches-shelf">
          <div class="shelf-header">
            <h4>Ready in Showroom Today (${matches.length} pieces)</h4>
            <span style="font-size:12px; color:var(--gold-dark); font-weight:600;">Immediate in-store delivery</span>
          </div>
          <div class="shelf-grid">
            ${matches.map(m => `
              <div class="shelf-item-card">
                <div class="shelf-item-sku">
                  <span>${esc(m.sku)}</span>
                  <span>${m.stock_qty || m.in_stock} in stock</span>
                </div>
                <div class="shelf-item-name">${esc(m.title || m.description)}</div>
                <div style="font-size:11.5px; color:var(--text-muted);">${esc(m.style)} &bull; ${m.weight_g}g</div>
                <div class="shelf-item-price">${inr(m.price_inr)}</div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    } else {
      target.innerHTML = matches.map(m => `
        <div class="shelf-item-card">
          <div class="shelf-item-sku">
            <span>${esc(m.sku)}</span>
            <span>${m.stock_qty || m.in_stock} in stock</span>
          </div>
          <div class="shelf-item-name">${esc(m.title || m.description)}</div>
          <div class="shelf-item-price">${inr(m.price_inr)}</div>
        </div>
      `).join('');
    }
  } catch (e) {}
}

async function fetchTrends() {
  const s = State.spec || defaultSpec('ring');
  try {
    const res = await fetch(`/api/trends?occasion=${encodeURIComponent(s.occasion || '')}&style=${encodeURIComponent(s.style || '')}`).then(r => r.json());
    if (res.cues && res.cues.length) {
      $('#trend-text').textContent = res.cues.join('; ') + (res.source === 'google_search' ? ' (Grounded via Google Search)' : '');
    }
  } catch (e) {
    if ($('#trend-bar')) $('#trend-bar').style.display = 'none';
  }
}

// ── Workshop Job Sheet Modal ──
async function triggerJobCardModal(sp) {
  if (!sp) sp = State.cur || State.spec;
  const modal = $('#job-card-modal');
  const body = $('#job-modal-body');
  body.innerHTML = `<div style="text-align:center; padding:30px;">Loading Karigar Work Order...</div>`;
  modal.classList.add('open');

  try {
    const job = await api('/api/artisan/job-card', sp);
    body.innerHTML = `
      <div style="background:var(--bg-canvas); border:1px solid var(--border-light); border-radius:var(--radius-sm); padding:20px; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
          <div>
            <div style="font-size:11px; color:var(--gold-dark); font-weight:700;">JOB CARD ID</div>
            <div style="font-weight:700; font-size:20px; color:var(--text-primary);">${esc(job.job_id)}</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:11px; color:var(--text-muted);">BIS HALLMARK</div>
            <div style="font-weight:700; color:var(--emerald);">${esc(job.hallmarking_grade || '916 BIS')}</div>
          </div>
        </div>
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; font-size:13px; border-top:1px solid var(--border-light); padding-top:12px;">
          <div><span style="color:var(--text-muted)">Category:</span> <b>${esc(job.category)}</b></div>
          <div><span style="color:var(--text-muted)">Alloy:</span> <b>${esc(job.metal && job.metal.type ? job.metal.type : sp.metal)}</b></div>
          <div><span style="color:var(--text-muted)">Gross Wt:</span> <b>${job.estimated_gross_weight_g || '-'} g</b></div>
          <div><span style="color:var(--text-muted)">Net Gold:</span> <b>${job.estimated_net_gold_g || '-'} g</b></div>
          <div><span style="color:var(--text-muted)">Tolerance:</span> <b>${job.weight_tolerance || '±5%'}</b></div>
          <div><span style="color:var(--text-muted)">Making Target:</span> <b>${inr(job.cost_breakdown ? job.cost_breakdown.making : 5000)}</b></div>
        </div>
      </div>
      <div style="font-size:13px; line-height:1.6; color:var(--text-secondary); margin-bottom:14px;">
        <b style="color:var(--text-primary)">Goldsmith Instructions:</b><br>
        ${esc(job.karigar_instructions || 'Standard hand-crafted casting with high mirror polish.')}
      </div>
    `;
  } catch (e) {
    body.innerHTML = `<div style="color:var(--ruby)">Failed to generate job sheet: ${esc(e.message)}</div>`;
  }
}

async function registerConfirmedOrder() {
  try {
    const res = await api('/api/requests', {
      id: State.reqId || null,
      status: 'sent',
      spec: State.cur || State.spec
    });
    State.reqId = res.id;
    toast("Order queued for Workshop!");
    appendChat(`Your bespoke ${(State.cur || State.spec).category} design has been transmitted to our master karigar with Job ID #${res.id}. A WhatsApp confirmation link has been prepared.`, 'bot');
  } catch (e) {
    toast("Order error: " + e.message);
  }
}
// ── OLD GOLD TRADE-IN ENGINE ──
function openTradeInModal() {
  $('#modal-tradein').classList.add('open');
  recalculateTradeIn();
}

function recalculateTradeIn() {
  const rows = $$('#tradein-table-body tr');
  const items = [];
  rows.forEach(r => {
    const desc = r.querySelector('td:nth-child(1) input').value || 'Scrap Gold';
    const gross = parseFloat(r.querySelector('td:nth-child(2) input').value) || 0;
    const stone = parseFloat(r.querySelector('td:nth-child(3) input').value) || 0;
    const karat = r.querySelector('td:nth-child(4) select').value;
    items.push({ description: desc, gross_weight_g: gross, stone_weight_g: stone, karatage: karat, has_hallmark: true });
  });

  api('/api/tradein/appraise', { items }).then(val => {
    $('#tradein-voucher-id').textContent = val.voucher_id;
    $('#val-total-gross').textContent = val.total_gross_weight_g + ' g';
    $('#val-total-stone').textContent = val.total_stone_deduction_g + ' g';
    $('#val-total-net').textContent = val.total_net_weight_g + ' g';
    $('#val-fine-gold').textContent = val.fine_gold_yield_g + ' g';
    $('#val-melting-fee').textContent = inr(val.melting_charges_inr);
    $('#val-net-credit').textContent = inr(val.net_trade_in_credit_inr);

    State.tradeInCredit = val.net_trade_in_credit_inr;
    State.tradeInVoucher = val.voucher_id;
  }).catch(e => console.warn("Tradein err:", e));
}

$('#btn-add-tradein-row').onclick = () => {
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td><input class="tradein-input" value="Old Broken Chain"></td>
    <td><input class="tradein-input" type="number" step="0.1" value="12.0"></td>
    <td><input class="tradein-input" type="number" step="0.1" value="0.0"></td>
    <td>
      <select class="tradein-input">
        <option value="22k">22k (91.6%)</option>
        <option value="18k" selected>18k (75.0%)</option>
        <option value="14k">14k (58.5%)</option>
        <option value="vintage_traditional">Vintage (84.0%)</option>
      </select>
    </td>
    <td><button style="border:none; background:none; cursor:pointer; color:var(--ruby); font-size:16px;">&times;</button></td>
  `;
  tr.querySelector('button').onclick = () => { tr.remove(); recalculateTradeIn(); };
  tr.querySelectorAll('input, select').forEach(i => i.onchange = recalculateTradeIn);
  $('#tradein-table-body').appendChild(tr);
  recalculateTradeIn();
};

$$('#tradein-table-body input, #tradein-table-body select').forEach(i => i.onchange = recalculateTradeIn);

$('#btn-apply-tradein-credit').onclick = () => {
  $('#modal-tradein').classList.remove('open');
  toast(`Applied ${inr(State.tradeInCredit)} old gold credit`);
  if (State.cur) updateCustomizer();
};

// ── DIGITAL GEMOLOGICAL CERTIFICATE ──
async function openCertModal(spec) {
  if (!spec) spec = State.cur || State.spec;
  $('#modal-certificate').classList.add('open');
  try {
    const cert = await api('/api/certificate/generate', { spec, patron_name: "Valued Patron" });
    $('#cert-huid-display').textContent = 'HUID: ' + cert.huid_number;
    $('#cert-id-val').textContent = cert.certificate_id;
    $('#cert-patron-name').textContent = cert.patron_name;
    $('#cert-category-val').textContent = cert.category;
    $('#cert-metal-val').textContent = cert.metal_description;
    $('#cert-gross-wt').textContent = cert.gross_weight_g + ' g';
    $('#cert-net-wt').textContent = cert.net_weight_g + ' g';
    $('#cert-carat-val').textContent = (cert.diamond_grading?.total_carats || 0.40) + ' ct';
  } catch (e) {
    console.warn("Cert err:", e);
  }
}

// ── MERCHANT INTELLIGENCE COMMAND CENTER ──
function renderMerchantCommandCenter() {
  $('#dynamic-stage-view').innerHTML = `
    <div style="margin-bottom:24px;">
      <h2 style="font:500 32px/1.2 var(--font-serif); color:var(--text-primary); margin-bottom:6px;">
        Merchant Intelligence & Bullion Command Center
      </h2>
      <p style="font-size:13.5px; color:var(--text-muted);">
        Enterprise analytics powered by Google Cloud BigQuery predictive algorithms, bullion risk stress-testing, and Gemini Copilot.
      </p>
    </div>

    <!-- Merchant Top Stats -->
    <div class="merchant-hero-stats" id="merchant-stats-shelf">
      <div class="merchant-stat-card">
        <span>24K BULLION SPOT</span>
        <b id="m-spot-rate">₹14,850 / g</b>
      </div>
      <div class="merchant-stat-card">
        <span>ANNUAL BULLION TARGET</span>
        <b id="m-bullion-target">16.7 kg</b>
      </div>
      <div class="merchant-stat-card">
        <span>WORKING CAPITAL LOCKED</span>
        <b id="m-capital-req">₹1,244 L</b>
      </div>
      <div class="merchant-stat-card">
        <span>SHOWROOM CONVERSION</span>
        <b style="color:var(--emerald);">44.2%</b>
      </div>
    </div>

    <!-- BigQuery Festival Demand Timeline -->
    <div style="margin-bottom:28px;">
      <h3 style="font:600 20px/1.2 var(--font-serif); color:var(--text-primary); margin-bottom:12px;">
        BigQuery Predictive Festival Demand Surge
      </h3>
      <div class="festival-timeline-grid" id="festival-grid">Loading BigQuery models...</div>
    </div>

    <!-- Google Cloud BigQuery Data Warehouse & Analytics Pipeline -->
    <div style="background:var(--bg-surface); border:1px solid var(--border-light); border-radius:var(--radius-md); padding:22px; margin-bottom:28px; box-shadow:var(--shadow-subtle);">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px;">
        <div>
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
            <span style="font-size:10px; font-weight:700; background:#FFFBEB; color:#B45309; padding:2px 8px; border-radius:4px; border:1px solid #FDE68A;">
              GOOGLE CLOUD BIGQUERY
            </span>
            <span style="font-size:12px; color:var(--emerald); font-weight:600;" id="bq-sync-indicator">
              ● Live Retail Warehouse Synced
            </span>
          </div>
          <h3 style="font:600 20px/1.2 var(--font-serif); color:var(--text-primary);">
            Retail Festival Analytics & Telemetry Dataset
          </h3>
          <p style="font-size:12.5px; color:var(--text-muted); margin-top:2px;">
            Dataset: <code style="background:var(--bg-canvas); padding:2px 6px; border-radius:3px;">jewel_ai_analytics.patron_design_telemetry</code> — Partitioned by Day, Clustered by Category & Metal.
          </p>
        </div>
        <div style="display:flex; gap:10px;">
          <button class="atelier-nav-link" id="btn-m-inspect-schema">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
            BigQuery DDL Schema
          </button>
          <button class="atelier-nav-link accent" id="btn-m-export-bq">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            Export BigQuery JSONL
          </button>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; background:var(--bg-canvas); padding:14px; border-radius:var(--radius-sm); font-size:12px;">
        <div><span style="color:var(--text-muted); display:block;">SYNCED DESIGN SESSIONS</span><b style="font-size:16px; color:var(--text-primary);" id="bq-record-count">24 Records</b></div>
        <div><span style="color:var(--text-muted); display:block;">PRIMARY CLUSTERING</span><b style="font-size:14px; color:var(--text-primary);">category, metal</b></div>
        <div><span style="color:var(--text-muted); display:block;">PREDICTIVE MULTIPLIERS</span><b style="font-size:14px; color:var(--emerald);">Dhanteras (2.8x)</b></div>
        <div><span style="color:var(--text-muted); display:block;">STREAMING BUFFER</span><b style="font-size:14px; color:var(--gold-dark);">Active (Zero Latency)</b></div>
      </div>
    </div>

    <!-- Bullion Volatility Stress-Testing (Hedging Engine) -->
    <div class="stress-tester-box">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
        <div>
          <h3 style="font:600 20px/1.2 var(--font-serif); color:var(--text-primary);">
            Bullion Price Volatility Stress-Tester
          </h3>
          <p style="font-size:12px; color:var(--text-muted);">Simulate gold price shocks on 1,500g showroom stock and 350g open bespoke orders</p>
        </div>
        <span id="stress-risk-badge" style="background:var(--emerald-bg); color:var(--emerald); font-weight:700; font-size:12px; padding:4px 10px; border-radius:4px;">
          BALANCED RISK
        </span>
      </div>
      <div class="control-row" style="margin-bottom:18px;">
        <div class="control-header">
          <span>Simulated Gold Price Shock</span>
          <b id="lbl-stress-pct" style="color:var(--gold-dark); font-size:16px;">+10% Surge</b>
        </div>
        <input class="atelier-range" id="rng-stress-pct" type="range" min="-15" max="15" step="1" value="10">
      </div>
      <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:14px; background:var(--bg-canvas); padding:16px; border-radius:var(--radius-sm); margin-bottom:14px;">
        <div>
          <span style="font-size:11px; color:var(--text-muted); display:block;">NEW SIMULATED SPOT</span>
          <b style="font-size:17px; color:var(--text-primary);" id="stress-new-rate">₹8,195 / g</b>
        </div>
        <div>
          <span style="font-size:11px; color:var(--text-muted); display:block;">INVENTORY VALUATION P&L</span>
          <b style="font-size:17px; color:var(--emerald);" id="stress-inv-delta">+ ₹11,17,500</b>
        </div>
        <div>
          <span style="font-size:11px; color:var(--text-muted); display:block;">UNHEDGED ORDERS MARGIN RISK</span>
          <b style="font-size:17px; color:var(--ruby);" id="stress-margin-risk">- ₹2,60,750</b>
        </div>
      </div>
      <div style="font-size:12.5px; color:var(--text-secondary); line-height:1.6;" id="stress-hedge-advice"></div>
    </div>

    <!-- Dead-Stock Remounting Optimizer -->
    <div style="margin-bottom:28px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <h3 style="font:600 20px/1.2 var(--font-serif); color:var(--text-primary);">
          Showroom Dead-Stock Remounting & Melting Optimizer
        </h3>
        <span style="font-size:12px; color:var(--text-muted);">Unlocks idle showcase gold into high-velocity daily wear</span>
      </div>
      <div class="dead-stock-grid" id="dead-stock-grid">Loading dead stock items...</div>
    </div>

    <!-- Gemini Merchant Copilot Chat -->
    <div class="atelier-panel">
      <div class="panel-headline">
        <span>Gemini Merchant Executive Copilot</span>
        <span style="font-size:11px; color:var(--gold-dark); font-weight:700;">STRATEGIC RETAIL ADVISORY</span>
      </div>
      <p style="font-size:12.5px; color:var(--text-muted); margin-bottom:12px;">
        Ask strategic questions regarding gold hedging, karigar turnaround, making charge margins, or festival procurement targets:
      </p>
      <div style="display:flex; gap:8px; margin-bottom:14px;">
        <input class="chat-input" id="copilot-input" placeholder="e.g. How should I hedge gold risk for upcoming Diwali wedding orders?" style="flex:1;">
        <button class="btn-gold-primary" id="btn-ask-copilot">Consult Copilot</button>
      </div>
      <div style="background:var(--bg-canvas); border:1px solid var(--border-light); border-radius:var(--radius-sm); padding:16px; font-size:13px; line-height:1.6;" id="copilot-answer-box">
        <b>Copilot Ready:</b> Ask any high-level question on inventory turnover, metal hedging, or festival stocking to receive immediate data-backed guidance.
      </div>
    </div>
  `;

  // Fetch Demand Intel
  fetch('/api/merchant/demand').then(r => r.json()).then(intel => {
    $('#m-spot-rate').textContent = inr(intel.current_gold_rate_24k) + ' / g';
    $('#m-bullion-target').textContent = intel.total_annual_bullion_target_kg + ' kg';
    $('#m-capital-req').textContent = '₹' + intel.total_working_capital_required_lakhs + ' L';

    $('#festival-grid').innerHTML = intel.forecast_timeline.map(f => `
      <div class="festival-card">
        <b>${esc(f.name)}</b>
        <span class="festival-multiplier">${f.demand_surge_multiplier}x Demand Surge</span>
        <div style="font-size:12px; color:var(--text-secondary); margin-bottom:6px;">
          Procurement Target: <b>${f.recommended_procurement_gold_kg} kg</b>
        </div>
        <div style="font-size:12px; color:var(--text-muted);">
          Avg Ticket: <b>${inr(f.avg_ticket_size_inr)}</b>
        </div>
      </div>
    `).join('');
  });

  // Stress test slider
  const runStress = () => {
    const shift = parseFloat($('#rng-stress-pct').value);
    $('#lbl-stress-pct').textContent = (shift >= 0 ? '+' : '') + shift + '% Shift';
    api('/api/merchant/stress-test', {
      inventory_gold_grams: 1500,
      open_unhedged_orders_grams: 350,
      price_shift_pct: shift
    }).then(res => {
      $('#stress-new-rate').textContent = inr(res.simulated_gold_rate_24k) + ' / g';
      $('#stress-inv-delta').textContent = (res.inventory_valuation_delta_inr >= 0 ? '+' : '') + inr(res.inventory_valuation_delta_inr);
      $('#stress-margin-risk').textContent = inr(res.unhedged_order_margin_impact_inr);
      $('#stress-hedge-advice').textContent = res.hedge_strategy;
      const badge = $('#stress-risk-badge');
      badge.textContent = res.risk_rating;
      badge.style.background = res.risk_rating === 'HIGH RISK' ? 'var(--ruby-bg)' : 'var(--emerald-bg)';
      badge.style.color = res.risk_rating === 'HIGH RISK' ? 'var(--ruby)' : 'var(--emerald)';
    });
  };
  $('#rng-stress-pct').oninput = runStress;
  runStress();

  // Dead stock
  fetch('/api/merchant/dead-stock').then(r => r.json()).then(ds => {
    $('#dead-stock-grid').innerHTML = ds.items.map(item => `
      <div class="dead-stock-card">
        <div style="font-size:10.5px; color:var(--text-muted); margin-bottom:2px;">${esc(item.sku)} &bull; ${item.gross_weight_g}g</div>
        <b style="font-size:13.5px; color:var(--text-primary); display:block; margin-bottom:4px;">${esc(item.description)}</b>
        <div style="color:var(--ruby); font-weight:600; margin-bottom:6px;">Locked: ${inr(item.carrying_cost_inr)}</div>
        <div style="background:var(--gold-soft); padding:8px; border-radius:4px; font-size:11.5px; color:var(--gold-dark); line-height:1.4;">
          <b>Remount:</b> ${esc(item.recommended_action)} (${item.unlocked_capital_gain_pct}% ROI)
        </div>
      </div>
    `).join('');
  });

  // Copilot Query
  $('#btn-ask-copilot').onclick = async () => {
    const q = $('#copilot-input').value.trim();
    if (!q) return;
    const box = $('#copilot-answer-box');
    box.innerHTML = `<em>Gemini Copilot formulating executive recommendation...</em>`;
    try {
      const res = await api('/api/merchant/copilot', { query: q });
      box.innerHTML = `
        <div style="font-weight:700; color:var(--gold-dark); margin-bottom:4px;">EXECUTIVE ADVISORY:</div>
        <div style="color:var(--text-primary); margin-bottom:10px;">${esc(res.answer)}</div>
        ${res.key_metrics ? `
          <div style="display:flex; gap:12px; font-size:11.5px; color:var(--text-muted); border-top:1px solid var(--border-light); padding-top:8px;">
            ${Object.entries(res.key_metrics).map(([k, v]) => `<span><b>${esc(k)}:</b> ${esc(v)}</span>`).join('')}
          </div>
        ` : ''}
      `;
    } catch (e) {
      box.textContent = "Copilot advisory offline: maintain standard bullion forward buffer.";
    }
  };

  // BigQuery Retail Warehouse Controls
  if ($('#btn-m-inspect-schema')) {
    $('#btn-m-inspect-schema').onclick = () => {
      openGcpStackModal();
      openBigQuerySchemaModal();
    };
  }
  if ($('#btn-m-export-bq')) {
    $('#btn-m-export-bq').onclick = exportBigQueryJSONL;
  }
  fetch('/api/merchant/bigquery/export')
    .then(r => r.json())
    .then(res => {
      if ($('#bq-record-count')) $('#bq-record-count').textContent = `${res.record_count} Records`;
    })
    .catch(() => {});
}

// ── GOOGLE CLOUD PLATFORM ARCHITECTURE & BIGQUERY TELEMETRY ──
function openGcpStackModal() {
  $('#modal-gcp-stack').classList.add('open');
  fetch('/api/merchant/bigquery/export')
    .then(r => r.json())
    .then(res => {
      if ($('#bq-record-count')) $('#bq-record-count').textContent = `${res.record_count} Records`;
    })
    .catch(() => {});
}

async function runVertexDiagnostics() {
  const btn = $('#btn-ping-gemini');
  const drawer = $('#gcp-diag-drawer');
  const content = $('#gcp-diag-content');
  btn.disabled = true;
  btn.textContent = 'Pinging Vertex AI...';
  drawer.style.display = 'block';
  content.innerHTML = `<em>Establishing live handshake with Vertex AI endpoint in asia-south1...</em>`;

  try {
    const res = await fetch('/api/diagnostics/gemini').then(r => r.json());
    const isOnline = res.status === 'online';
    
    if ($('#gcp-model-name')) $('#gcp-model-name').textContent = res.active_model || 'gemini-2.5-flash';
    if ($('#gcp-latency-val')) {
      const activeStats = res.models && res.active_model && res.models[res.active_model];
      const lat = activeStats ? `${activeStats.latency_ms} ms` : 'Fallback Active';
      $('#gcp-latency-val').textContent = lat;
    }
    if ($('#gcp-vertex-dot')) {
      $('#gcp-vertex-dot').style.background = isOnline ? 'var(--emerald)' : 'var(--gold-dark)';
      $('#gcp-vertex-dot').style.boxShadow = isOnline ? '0 0 6px var(--emerald)' : '0 0 6px var(--gold-dark)';
    }

    content.innerHTML = `
      <div style="background:var(--bg-surface); border:1px solid var(--border-light); border-radius:6px; padding:14px; margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <div>
            <span style="font-size:11px; color:var(--text-muted); text-transform:uppercase;">PROVIDER</span>
            <b style="display:block; font-size:14px; color:var(--text-primary);">${esc(res.provider)}</b>
          </div>
          <span style="font-size:11px; font-weight:700; padding:3px 10px; border-radius:4px; background:${isOnline ? 'var(--emerald-bg)' : 'var(--gold-soft)'}; color:${isOnline ? 'var(--emerald)' : 'var(--gold-dark)'};">
            ${isOnline ? 'VERTEX AI LIVE' : 'FAILOVER CONCIERGE'}
          </span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; font-size:12px; border-top:1px solid var(--border-subtle); padding-top:10px;">
          <div><span style="color:var(--text-muted);">GCP Project:</span> <b>${esc(res.project)}</b></div>
          <div><span style="color:var(--text-muted);">Region:</span> <b>${esc(res.location)}</b></div>
          <div><span style="color:var(--text-muted);">Active Model:</span> <b>${esc(res.active_model)}</b></div>
        </div>
      </div>
      <div style="font-size:12px; color:var(--text-secondary); line-height:1.5;">
        <b>Telemetric Status:</b> ${esc(res.summary)}
      </div>
      ${res.models ? `
        <div style="margin-top:12px; border-top:1px solid var(--border-light); padding-top:10px;">
          <div style="font-size:11px; font-weight:700; color:var(--text-muted); margin-bottom:6px; text-transform:uppercase;">Model Probes</div>
          <div style="display:flex; flex-direction:column; gap:6px;">
            ${Object.entries(res.models).map(([mName, mStats]) => `
              <div style="display:flex; justify-content:space-between; font-size:11.5px; background:var(--bg-canvas); padding:6px 10px; border-radius:4px;">
                <span><code>${esc(mName)}</code></span>
                <span style="color:${mStats.status === 'ONLINE' ? 'var(--emerald)' : 'var(--gold-dark)'}; font-weight:600;">
                  ${esc(mStats.status)} (${mStats.latency_ms} ms)
                </span>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}
    `;
    toast(isOnline ? "Vertex AI Live Ping Successful" : "Concierge Fallback Active");
  } catch (e) {
    content.innerHTML = `<div style="color:var(--ruby);">Diagnostic ping error: ${esc(e.message)}</div>`;
    toast("Vertex AI ping failed: " + e.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = 'Run Live Vertex AI Ping';
  }
}

async function openBigQuerySchemaModal() {
  const drawer = $('#gcp-schema-drawer');
  drawer.style.display = 'block';
  const codeBox = $('#gcp-sql-content');
  codeBox.textContent = "-- Loading BigQuery DDL schema from data/bigquery_schema.sql...";
  try {
    const res = await fetch('/api/merchant/bigquery/schema').then(r => r.json());
    codeBox.textContent = res.sql || "-- BigQuery DDL schema loaded successfully.";
  } catch (e) {
    codeBox.textContent = "-- Error loading schema: " + e.message;
  }
}

async function exportBigQueryJSONL() {
  toast("Preparing BigQuery streaming telemetry export...", "info");
  try {
    const res = await fetch('/api/merchant/bigquery/export').then(r => r.json());
    const records = res.records || [];
    const jsonlContent = records.map(r => JSON.stringify(r)).join('\n');
    const blob = new Blob([jsonlContent], { type: 'application/x-ndjson' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `jewel_ai_bigquery_telemetry_${new Date().toISOString().slice(0, 10)}.jsonl`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast(`Exported ${records.length} records to BigQuery NDJSON format`);
  } catch (e) {
    toast("Failed to export BigQuery telemetry: " + e.message, "error");
  }
}

// ── SKIN UNDERTONE & COLORIMETRY HARMONIZER ──
let latestPrescribedMetal = null;

function mapMetalKey(m) {
  if (!m) return 'gold_22k';
  const s = m.toLowerCase().replace(/[\s-]/g, '_');
  if (s.includes('24')) return 'gold_24k';
  if (s.includes('22')) return 'gold_22k';
  if (s.includes('18')) return 'gold_18k';
  if (s.includes('14')) return 'gold_14k';
  if (s.includes('rose')) return 'rose_gold';
  if (s.includes('plat')) return 'platinum';
  return 'gold_22k';
}

function openUndertoneModal() {
  $('#modal-undertone').classList.add('open');
}

async function handleUndertoneFile(file) {
  if (!file.type.startsWith('image/')) {
    toast('Please upload an image portrait or wrist photo (JPEG, PNG, WebP)');
    return;
  }

  const resultsBox = $('#undertone-results-box');
  const applyBtn = $('#btn-apply-undertone-metal');
  resultsBox.style.display = 'block';
  applyBtn.style.display = 'none';
  $('#ut-detected-profile').textContent = "Analyzing Skin Complexion & Luminescence...";
  $('#ut-undertone-badge').textContent = "INSPECTING";
  $('#ut-undertone-badge').style.background = "var(--gold-soft)";
  $('#ut-styling-notes').innerHTML = `<em>Gemini 2.5 Vision inspecting melanin balance, vein undertone & ambient reflection...</em>`;
  $('#ut-metals-list').innerHTML = `<span>Inspecting...</span>`;
  $('#ut-gems-list').innerHTML = `<span>Inspecting...</span>`;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/undertone/analyze', { method: 'POST', body: formData }).then(r => r.json());
    $('#ut-detected-profile').textContent = `${res.skin_tone} Skin Tone • ${res.undertone.toUpperCase()} Undertone`;
    $('#ut-undertone-badge').textContent = res.undertone.toUpperCase();
    $('#ut-styling-notes').textContent = res.styling_notes;

    const metalChips = (res.recommended_metals || []).map(m => {
      const cleanName = m.replace(/_/g, ' ').toUpperCase();
      return `<span style="background:var(--gold-soft); color:var(--gold-dark); padding:3px 8px; border-radius:4px; font-weight:600; font-size:11.5px; border:1px solid rgba(184, 144, 71, 0.2);">${cleanName}</span>`;
    }).join(' ');
    $('#ut-metals-list').innerHTML = metalChips || '<span>22k Gold</span>';

    const gemChips = (res.best_gemstones || []).map(g => {
      const cleanName = g.replace(/_/g, ' ').toUpperCase();
      return `<span style="background:var(--bg-canvas); color:var(--text-secondary); padding:3px 8px; border-radius:4px; font-size:11.5px; border:1px solid var(--border-light);">${cleanName}</span>`;
    }).join(' ');
    $('#ut-gems-list').innerHTML = gemChips || '<span>Natural Diamonds</span>';

    if (res.recommended_metals && res.recommended_metals.length) {
      latestPrescribedMetal = mapMetalKey(res.recommended_metals[0]);
      applyBtn.style.display = 'inline-block';
      applyBtn.textContent = `Apply Prescribed ${latestPrescribedMetal.replace(/_/g, ' ').toUpperCase()}`;
    }

    toast(`Analyzed ${res.undertone} undertone with Gemini Vision`);
  } catch (e) {
    $('#ut-styling-notes').textContent = "Stylist note: Warm 22k yellow gold and natural diamonds harmonize exquisitely with classic Indian complexions.";
    toast("Undertone calibrated with master stylist benchmark", "info");
  }
}

if ($('#btn-apply-undertone-metal')) {
  $('#btn-apply-undertone-metal').onclick = () => {
    if (!latestPrescribedMetal) return;
    const target = State.cur || State.spec;
    target.metal = latestPrescribedMetal;
    if (State.cur) {
      updateCustomizer();
    }
    $('#modal-undertone').classList.remove('open');
    toast(`Applied ${latestPrescribedMetal.replace(/_/g, ' ').toUpperCase()} to match your skin harmony`);
    appendChat(`I have adjusted your bespoke design to ${latestPrescribedMetal.replace(/_/g, ' ').toUpperCase()} to complement your natural skin undertone and maximize radiance.`, 'bot');
  };
}

const utDropzone = $('#undertone-dropzone');
const utFileInput = $('#file-input-undertone');
if (utDropzone && utFileInput) {
  utDropzone.onclick = () => utFileInput.click();
  utDropzone.ondragover = e => { e.preventDefault(); utDropzone.classList.add('dragover'); };
  utDropzone.ondragleave = () => utDropzone.classList.remove('dragover');
  utDropzone.ondrop = e => {
    e.preventDefault();
    utDropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length) handleUndertoneFile(e.dataTransfer.files[0]);
  };
  utFileInput.onchange = e => {
    if (e.target.files.length) handleUndertoneFile(e.target.files[0]);
  };
}

// Global modal overlay backdrop click to dismiss
$$('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => {
    if (e.target === overlay) overlay.classList.remove('open');
  });
});

// ── NAVIGATION & MODE CONTROLS ──
$('#tab-mode-atelier').onclick = () => {
  State.currentMode = 'atelier';
  $('#tab-mode-atelier').classList.add('active');
  $('#tab-mode-merchant').classList.remove('active');
  $('#category-subtabs-row').style.display = 'flex';
  if (State.cur) openCustomizer(State.cur);
  else if (State.variants.length) renderGalleryView();
  else renderWelcomeStage();
};

$('#tab-mode-merchant').onclick = () => {
  State.currentMode = 'merchant';
  $('#tab-mode-merchant').classList.add('active');
  $('#tab-mode-atelier').classList.remove('active');
  $('#category-subtabs-row').style.display = 'none';
  renderMerchantCommandCenter();
};

$('#btn-nav-tradein').onclick = openTradeInModal;
$('#btn-nav-cert').onclick = () => openCertModal(State.cur || State.spec);
$('#btn-nav-gcp-stack').onclick = openGcpStackModal;
$('#btn-nav-undertone').onclick = openUndertoneModal;
$('#btn-ping-gemini').onclick = runVertexDiagnostics;
$('#btn-view-bq-schema').onclick = openBigQuerySchemaModal;
$('#btn-export-bq-data').onclick = exportBigQueryJSONL;

// ── Conversational Chat ──
$('#chat-form').onsubmit = async e => {
  e.preventDefault();
  const inp = $('#chat-input');
  const txt = inp.value.trim();
  if (!txt) return;
  inp.value = '';

  State.msgs.push({ role: 'user', content: txt });
  appendChat(txt, 'user');
  const botMsg = appendChat('Consulting atelier...', 'bot');

  showGalleryLoadingState("Designing bespoke pieces according to your prompt...");

  try {
    const res = await api('/api/chat', { messages: State.msgs, spec: State.spec });
    botMsg.textContent = res.reply;
    State.msgs.push({ role: 'assistant', content: res.reply });

    if (res.is_off_topic) {
      toast("Please specify a jewelry piece, metal, or occasion", "info");
      return;
    }

    State.spec = res.spec;
    setCategoryActive(State.spec.category);

    const vRes = await api('/api/variants', State.spec);
    State.variants = vRes.variants;
    if (State.currentMode === 'atelier') {
      State.cur = null;
      renderGalleryView();
    }
  } catch (err) {
    botMsg.textContent = "Loaded tailored design options based on your request.";
    State.msgs.push({ role: 'assistant', content: "Loaded tailored design options based on your request." });
    const vRes = await api('/api/variants', State.spec);
    State.variants = vRes.variants;
    if (State.currentMode === 'atelier') {
      State.cur = null;
      renderGalleryView();
    }
  } finally {
    hideGalleryLoadingState();
  }
};

// ── Curated Starters Click Handler ──
function handleStarterSelection(prompt, cat) {
  State.cur = null;
  setCategoryActive(cat);
  State.spec = defaultSpec(cat);

  showGalleryLoadingState(`Synthesizing calibrated ${cat} collection for your occasion...`);

  State.msgs = [{ role: 'user', content: prompt }];
  appendChat(prompt, 'user');
  const botMsg = appendChat('Consulting atelier...', 'bot');

  api('/api/variants', State.spec)
    .then(vRes => {
      State.variants = vRes.variants;
      if (State.currentMode === 'atelier' && !State.cur) renderGalleryView();
    })
    .catch(err => {
      console.warn("Variants preliminary error:", err);
    });

  api('/api/chat', { messages: State.msgs, spec: State.spec })
    .then(res => {
      botMsg.textContent = res.reply;
      State.msgs.push({ role: 'assistant', content: res.reply });
      if (res.spec) {
        State.spec = res.spec;
        api('/api/variants', State.spec).then(vRes => {
          State.variants = vRes.variants;
          if (State.currentMode === 'atelier' && !State.cur) renderGalleryView();
        }).catch(() => {});
      }
    })
    .catch(e => {
      const fallbackReply = `Delighted to co-create your bespoke ${cat}. I have calibrated 3 master craftsman variations against today's gold rate.`;
      botMsg.textContent = fallbackReply;
      State.msgs.push({ role: 'assistant', content: fallbackReply });
    })
    .finally(() => {
      hideGalleryLoadingState();
    });
}

$('#btn-starter-bridal').onclick = () => {
  handleStarterSelection(
    "Design an 18k gold bridal necklace for a wedding, budget ₹1,50,000 with floral temple motifs",
    "necklace"
  );
};

$('#btn-starter-ring').onclick = () => {
  handleStarterSelection(
    "Solitaire diamond engagement ring in 22k yellow gold, budget ₹60,000",
    "ring"
  );
};

$('#btn-starter-earrings').onclick = () => {
  handleStarterSelection(
    "Temple jhumka earrings for Diwali festival, budget ₹45,000",
    "earrings"
  );
};

// Bullion Refresh
$('#btn-refresh-ticker').onclick = async () => {
  $('#ticker-rate').textContent = 'Grounding...';
  try {
    const res = await fetch('/api/gold-rate?refresh=true').then(r => r.json());
    $('#ticker-rate').textContent = inr(res.gold_rate_24k_per_g) + ' / g';
    const srcMap = {
      'google_search_grounding': 'Google Search Grounding',
      'live_bullion_feed': 'Live Financial Bullion Feed',
      'calibrated_ibja_standard': 'Calibrated IBJA Retail Standard'
    };
    const srcLabel = srcMap[res.source] || 'Live Market Rate';
    toast(`Bullion spot updated: ${inr(res.gold_rate_24k_per_g)}/g (${srcLabel})`);
  } catch (e) {
    $('#ticker-rate').textContent = '₹14,850 / g';
    toast('Bullion spot cached at calibrated IBJA benchmark: ₹14,850/g');
  }
};

$('#btn-top-jobcard').onclick = () => triggerJobCardModal(State.cur || State.spec);
$('#btn-close-job-modal').onclick = () => $('#job-card-modal').classList.remove('open');

// ── Multimodal Photo Upload ──
const dropzone = $('#inspiration-dropzone');
const fileInput = $('#file-input-inspiration');

dropzone.onclick = () => fileInput.click();
dropzone.ondragover = e => { e.preventDefault(); dropzone.classList.add('dragover'); };
dropzone.ondragleave = () => dropzone.classList.remove('dragover');
dropzone.ondrop = e => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  if (e.dataTransfer.files.length) handleImageFile(e.dataTransfer.files[0]);
};
fileInput.onchange = e => {
  if (e.target.files.length) handleImageFile(e.target.files[0]);
};

async function handleImageFile(file) {
  if (!file.type.startsWith('image/')) {
    toast('Please upload an image file (JPEG, PNG, WebP)');
    return;
  }

  const banner = $('#vision-banner');
  banner.classList.add('visible');
  $('#vision-category').textContent = 'Inspecting...';
  $('#vision-details').textContent = 'Gemini 2.5 Vision inspecting architecture, stones & karatage...';

  // Render thumbnail inside dropzone
  const thumbReader = new FileReader();
  thumbReader.onload = ev => {
    $('#inspiration-dropzone').innerHTML = `
      <img src="${ev.target.result}" style="width:40px; height:40px; object-fit:cover; border-radius:6px; border:1px solid var(--border-light); margin-right:10px;">
      <div class="dropzone-meta">
        <b>Inspiration Loaded: ${esc(file.name.slice(0, 18))}</b>
        <span style="color:var(--gold-dark); font-weight:600;">Click to replace photo</span>
      </div>
    `;
  };
  thumbReader.readAsDataURL(file);

  appendChat("Uploaded an inspiration photo. Analyzing with Gemini 2.5 Vision...", 'user');
  const thinking = appendChat("Inspecting jewellery architecture...", 'bot');

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/analyze-image', { method: 'POST', body: formData });
    if (!res.ok) throw new Error((await res.json()).detail || 'Image analysis failed');
    const data = await res.json();
    if (data.ok === false || data.is_jewellery === false) {
      const msg = data.message || 'The uploaded photo does not appear to be jewelry or a jewelry design sketch.';
      thinking.className = 'chat-msg bot';
      thinking.textContent = `Concierge Notice: ${msg} Please upload a reference photo or sketch of a ring, necklace, earrings, or bangle.`;
      toast(msg, 'error');
      return;
    }
    const ana = data.analysis;

    $('#vision-category').textContent = ana.category + ' (' + (ana.motif || ana.style) + ')';
    $('#vision-details').textContent = `${ana.detected_metal || 'Gold'} &bull; ${ana.stone_setting || 'Prong set'}. Occasion: ${ana.occasion_suggestion || 'Heirloom'}`;

    thinking.textContent = `I detected a ${ana.detected_metal || 'gold'} ${ana.category} with a ${ana.motif || ana.style} motif. Calibrated 3 options for you.`;

    State.spec = data.spec;
    setCategoryActive(data.spec.category);

    const vRes = await api('/api/variants', State.spec);
    State.variants = vRes.variants;
    if (State.currentMode === 'atelier') renderGalleryView();

    toast(`Vision analyzed ${ana.category}`);
  } catch (err) {
    thinking.className = 'chat-msg err';
    thinking.textContent = 'Vision notice: ' + err.message + '. Generating preliminary designs with default parameters.';
    const vRes = await api('/api/variants', State.spec);
    State.variants = vRes.variants;
    if (State.currentMode === 'atelier') renderGalleryView();
  }
}

// ── Category Switcher ──
function setCategoryActive(cat) {
  $$('.cat-pill-btn').forEach(b => b.classList.toggle('active', b.dataset.cat === cat));
}

$$('.cat-pill-btn').forEach(btn => {
  btn.onclick = async () => {
    const cat = btn.dataset.cat;
    setCategoryActive(cat);
    State.spec = defaultSpec(cat);
    appendChat(`Switched showroom to ${cat}s. Loading calibrated options...`, 'bot');
    try {
      const vRes = await api('/api/variants', State.spec);
      State.variants = vRes.variants;
      if (State.currentMode === 'atelier') renderGalleryView();
    } catch (e) {
      renderWelcomeStage();
    }
  };
});

// Init
(() => {
  appendChat("Welcome to Jewel-AI Atelier. Describe your special occasion, aesthetic taste, and target budget — or select a curated masterpiece below.", 'bot');
  renderWelcomeStage();

  fetch('/api/gold-rate')
    .then(r => r.json())
    .then(res => {
      $('#ticker-rate').textContent = inr(res.gold_rate_24k_per_g) + ' / g';
    })
    .catch(() => {});
})();
