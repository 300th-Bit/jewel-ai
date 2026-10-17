/**
 * JEWEL-AI Procedural 2D CAD Blueprint Engine
 * Real-time parametric SVG generation for Haute Joaillerie
 */

const METALS = {
  gold_24k: ['#DFB135', '#B8860B', '24k Fine Gold (999)'],
  gold_22k: ['#C99E32', '#997318', '22k Standard Gold (916 BIS)'],
  gold_18k: ['#B88B4A', '#8C6328', '18k Bridal Gold (750)'],
  rose_gold: ['#E0A899', '#C27D6B', '18k Romantic Rose Gold (750)'],
  gold_14k: ['#AA8555', '#7A5B32', '14k Everyday Gold (585)'],
  platinum: ['#D1D5DB', '#9CA3AF', 'Platinum 950 Pure']
};

let _cadUid = 0;

// ── SVG CAD Jewel Renderers ──
function renderJewellerySVG(sp) {
  if (!sp) sp = State.cur || State.spec;
  const cat = sp.category || 'ring';
  if (cat === 'necklace') return renderNecklaceSVG(sp);
  if (cat === 'earrings') return renderEarringsSVG(sp);
  if (cat === 'bangle') return renderBangleSVG(sp);
  return renderRingSVG(sp);
}

function renderRingSVG(sp) {
  const id = 'cad_r_' + (_cadUid++);
  const [a, b] = METALS[sp.metal] || METALS.gold_22k;
  const sw = 6 + (sp.band_width_mm || 3) * 3.2;
  const hasStone = sp.stone && sp.stone.type !== 'none';
  const carat = sp.stone ? (sp.stone.carat || 0.3) : 0;
  const r = hasStone ? 10 + carat * 20 : 0;
  const cy = 72 - sw / 2 - r * 0.55;

  return `<svg viewBox="0 -25 200 230" role="img">
    <defs>
      <linearGradient id="${id}" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="${a}"/><stop offset="45%" stop-color="${b}"/><stop offset="70%" stop-color="${a}"/><stop offset="100%" stop-color="${b}"/>
      </linearGradient>
    </defs>
    <circle cx="100" cy="126" r="58" fill="none" stroke="url(#${id})" stroke-width="${sw}"/>
    <circle cx="100" cy="126" r="${58 - sw/2 + 1}" fill="none" stroke="#FFFFFF" stroke-width="1.2" opacity="0.6"/>
    ${hasStone ? `
      <polygon points="${100-r*0.65},${cy-r*0.75} ${100+r*0.65},${cy-r*0.75} ${100+r},${cy-r*0.15} 100,${cy+r*0.85} ${100-r},${cy-r*0.15}" fill="#F0F7FF" stroke="#60A5FA" stroke-width="1.2"/>
      <path d="M${100-r},${cy-r*0.15}H${100+r} M${100-r*0.65},${cy-r*0.75}L100,${cy+r*0.85}L${100+r*0.65},${cy-r*0.75} M${100-r*0.35},${cy-r*0.15}L100,${cy-r*0.75}L${100+r*0.35},${cy-r*0.15}" stroke="#93C5FD" stroke-width="0.8" fill="none"/>
      <circle cx="${100-r*0.7}" cy="${cy-r*0.7}" r="2" fill="${b}"/><circle cx="${100+r*0.7}" cy="${cy-r*0.7}" r="2" fill="${b}"/>
    ` : ''}
  </svg>`;
}

function renderNecklaceSVG(sp) {
  const id = 'cad_n_' + (_cadUid++);
  const [a, b] = METALS[sp.metal] || METALS.gold_22k;
  const hasStone = sp.stone && sp.stone.type !== 'none';
  const pr = hasStone ? 14 : 10;
  return `<svg viewBox="0 -10 200 230" role="img">
    <defs><linearGradient id="${id}" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="${a}"/><stop offset="50%" stop-color="${b}"/><stop offset="100%" stop-color="${a}"/></linearGradient></defs>
    <path d="M 30,25 Q 100,125 170,25" fill="none" stroke="url(#${id})" stroke-width="4.5" stroke-dasharray="2,2"/>
    <rect x="96" y="88" width="8" height="14" rx="3" fill="${b}" stroke="${a}"/>
    <circle cx="100" cy="118" r="${pr + 6}" fill="url(#${id})" stroke="${b}" stroke-width="2"/>
    ${hasStone ? `<polygon points="${100-pr*0.7},${118-pr*0.7} ${100+pr*0.7},${118-pr*0.7} ${100+pr},${118} 100,${118+pr} ${100-pr},${118}" fill="#F0F7FF" stroke="#60A5FA"/>` : `<circle cx="100" cy="118" r="${pr}" fill="${b}"/>`}
    <circle cx="100" cy="${118 + pr + 12}" r="3.5" fill="${a}" stroke="${b}"/>
  </svg>`;
}

function renderEarringsSVG(sp) {
  const id = 'cad_e_' + (_cadUid++);
  const [a, b] = METALS[sp.metal] || METALS.gold_22k;
  function eDrop(cx) {
    return `<circle cx="${cx}" cy="50" r="10" fill="url(#${id})" stroke="${b}"/>
    <line x1="${cx}" y1="60" x2="${cx}" y2="76" stroke="${b}" stroke-width="3"/>
    <path d="M ${cx-24},118 C ${cx-24},82 ${cx+24},82 ${cx+24},118 Z" fill="url(#${id})" stroke="${b}" stroke-width="2"/>
    <rect x="${cx-26}" y="118" width="52" height="6" rx="3" fill="${b}"/>
    ${[-18, -9, 0, 9, 18].map(dx => `<circle cx="${cx+dx}" cy="132" r="3" fill="${a}" stroke="${b}"/><line x1="${cx+dx}" y1="124" x2="${cx+dx}" y2="129" stroke="${b}"/>`).join('')}`;
  }
  return `<svg viewBox="0 0 220 180" role="img"><defs><linearGradient id="${id}" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="${a}"/><stop offset="50%" stop-color="${b}"/><stop offset="100%" stop-color="${a}"/></linearGradient></defs>${eDrop(60)}${eDrop(160)}</svg>`;
}

function renderBangleSVG(sp) {
  const id = 'cad_b_' + (_cadUid++);
  const [a, b] = METALS[sp.metal] || METALS.gold_22k;
  return `<svg viewBox="0 0 200 200" role="img"><defs><linearGradient id="${id}" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="${a}"/><stop offset="50%" stop-color="${b}"/><stop offset="100%" stop-color="${a}"/></linearGradient></defs>
    <ellipse cx="100" cy="100" rx="72" ry="54" fill="none" stroke="url(#${id})" stroke-width="12"/>
    <ellipse cx="100" cy="100" rx="66" ry="49" fill="none" stroke="#FFFFFF" stroke-width="1.2" opacity="0.6"/>
  </svg>`;
}
