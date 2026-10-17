"""
JEWEL-AI: Hackathon Video Demonstration Automation Script
Optimized for Recordly App & Full High-Definition Screen Recording
URL Target: https://jewel-ai-162948513640.asia-south1.run.app

Target Video Duration: ~3 minutes 30 seconds (Strict Hackathon Gate: 3 to 4 minutes)
Features:
- Smooth human-like cursor interpolation with visual luxury gold cursor overlay
- Interactive lower-third teleprompter banner with live synchronized narration script
- Complete flow: GCP Architecture, AI Concierge, Guardrails, CAD Studio, Pricing,
  Skin Harmony, Old Gold Trade-In, BIS HUID Passport, Karigar Job Card & Merchant Center.
"""

import sys
import time
import math
from pathlib import Path
from playwright.sync_api import sync_playwright

DEPLOYED_URL = "https://jewel-ai-162948513640.asia-south1.run.app"

# ──────────────────────────────────────────────────────────
# Timed Voiceover Script & Narration Scenes
# ──────────────────────────────────────────────────────────
SCENES = [
    {
        "id": 1,
        "title": "Introduction & Google Cloud Architecture",
        "duration": 25,
        "script": "Welcome to Jewel-AI, an enterprise digital atelier transforming fine jewelry bespoke craftsmanship. Built on Google Cloud, we combine Vertex AI intelligence, BigQuery seasonal demand forecasting, and serverless Cloud Run in asia-south1. Let's inspect the live architecture and ping Vertex AI directly."
    },
    {
        "id": 2,
        "title": "Conversational AI Concierge & Domain Guardrails",
        "duration": 30,
        "script": "Our conversational atelier concierge is powered by Gemini 2.5 Flash. As a client describes their dream jewelry, occasion, and budget, the AI extracts structured technical parameters. Furthermore, enterprise guardrails ensure off-topic inquiries are politely steered back to fine jewelry creation."
    },
    {
        "id": 3,
        "title": "3-Tier Calibrated Variant Engine & CAD Previews",
        "duration": 35,
        "script": "From a single client consultation, Jewel-AI dynamically formulates three calibrated options: Budget-Smart, Balanced Classic, and Statement Heirloom. With a single click, clients can toggle between photorealistic luxury studio renders and real-time CAD blueprints, while viewing showroom inventory ready for instant delivery."
    },
    {
        "id": 4,
        "title": "Parametric 2D CAD Studio & Real-Time Bullion Pricing",
        "duration": 35,
        "script": "Inside the bespoke atelier customizer, master craftsmen and patrons co-create with parametric precision. Changing metal alloy, band width, stone carat, or prong count triggers real-time 2D CAD blueprint redraws and instant mathematical pricing breakdowns, including bullion weight, BIS hallmarking fee, and GST."
    },
    {
        "id": 5,
        "title": "Skin Harmony Undertone Colorimetry Harmonizer",
        "duration": 25,
        "script": "Fine jewelry should illuminate the patron's natural beauty. Our Skin Harmony engine uses Gemini 2.5 Vision to inspect skin tone, vein undertones, and melanin balance, recommending the most flattering precious metal alloys and gemstones, automatically syncing them into the customizer."
    },
    {
        "id": 6,
        "title": "Old Gold Circular Trade-In & Scrap Melting Engine",
        "duration": 25,
        "script": "In India, over 30% of fine jewelry purchases involve family heirloom gold. Our circular trade-in engine transparently assays scrap ornaments against live 24K bullion spot rates, calculates fine gold recovery with melting loss, and applies instant credit vouchers toward the bespoke commission."
    },
    {
        "id": 7,
        "title": "BIS HUID Authenticity Passport & Workshop Job Sheet",
        "duration": 25,
        "script": "Every completed commission receives a tamper-proof digital Certificate of Authenticity featuring a 6-character laser-inscribed BIS HUID and complete diamond 4Cs report. A production-ready Karigar goldsmith job sheet with CAD schematics and one-click WhatsApp quotation is generated instantly."
    },
    {
        "id": 8,
        "title": "Merchant Intelligence & Production Cloud Run Summary",
        "duration": 10,
        "script": "For jewelers, the Merchant Command Center leverages BigQuery machine learning to forecast festival demand surges across Diwali and wedding seasons. Jewel-AI: uniting heritage Indian craftsmanship with modern Google Cloud AI."
    }
]

# CSS & JavaScript for Simulated Cursor & Lower-Third Teleprompter
INJECTED_OVERLAYS = """
/* Visual Glowing Cursor for Screen Studio / Recordly Tracking */
#playwright-virtual-cursor {
  position: fixed;
  top: 0;
  left: 0;
  width: 26px;
  height: 26px;
  pointer-events: none;
  z-index: 2147483647;
  transform: translate(-50%, -50%);
  transition: transform 0.08s ease-out;
}
#playwright-virtual-cursor .cursor-dot {
  width: 14px;
  height: 14px;
  background: #B89047;
  border: 2.5px solid #FFFFFF;
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(184, 144, 71, 0.9), 0 2px 6px rgba(0,0,0,0.4);
}
#playwright-virtual-cursor .cursor-ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 14px;
  height: 14px;
  border: 2px solid #D4AF37;
  border-radius: 50%;
  transform: translate(-50%, -50%) scale(1);
  opacity: 0;
  pointer-events: none;
}
#playwright-virtual-cursor.clicking .cursor-ripple {
  animation: cursorRippleAnim 0.45s ease-out forwards;
}
@keyframes cursorRippleAnim {
  0% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(3.2); opacity: 0; }
}

/* On-Screen Lower-Third Teleprompter / Narration Guide */
#hackathon-teleprompter {
  position: fixed;
  bottom: 18px;
  left: 50%;
  transform: translateX(-50%);
  width: min(92%, 1100px);
  background: rgba(18, 16, 14, 0.94);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(184, 144, 71, 0.45);
  border-radius: 12px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.65), 0 0 20px rgba(184, 144, 71, 0.15);
  padding: 14px 20px 16px 20px;
  z-index: 2147483646;
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  color: #F7F5F0;
  pointer-events: auto;
  transition: all 0.3s ease;
}
#tp-progress-bar-track {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 10px;
}
#tp-progress-bar-fill {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, #9C7430, #D4AF37, #F5D77F);
  transition: width 0.4s linear;
}
#tp-meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
#tp-scene-tag {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #D4AF37;
  display: flex;
  align-items: center;
  gap: 8px;
}
#tp-timer {
  font-size: 12px;
  font-weight: 600;
  color: #C5BBAA;
  font-variant-numeric: tabular-nums;
}
#tp-script-text {
  font-size: 13.5px;
  line-height: 1.5;
  color: #EDE8DF;
  font-weight: 400;
}
#tp-toggle-btn {
  background: transparent;
  border: 1px solid rgba(184, 144, 71, 0.3);
  color: #D4AF37;
  font-size: 10.5px;
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
}
"""

def setup_injected_overlays(page):
    """Injects cursor element and teleprompter bar into page."""
    page.add_style_tag(content=INJECTED_OVERLAYS)
    page.evaluate("""() => {
      if (!document.getElementById('playwright-virtual-cursor')) {
        const cursor = document.createElement('div');
        cursor.id = 'playwright-virtual-cursor';
        cursor.innerHTML = '<div class="cursor-dot"></div><div class="cursor-ripple"></div>';
        document.body.appendChild(cursor);
      }
      if (!document.getElementById('hackathon-teleprompter')) {
        const tp = document.createElement('div');
        tp.id = 'hackathon-teleprompter';
        tp.innerHTML = `
          <div id="tp-progress-bar-track"><div id="tp-progress-bar-fill"></div></div>
          <div id="tp-meta-row">
            <div id="tp-scene-tag">
              <span style="display:inline-block; width:7px; height:7px; border-radius:50%; background:#D4AF37; box-shadow:0 0 6px #D4AF37;"></span>
              <span id="tp-scene-title">INITIALIZING RECORDLY SHOWCASE</span>
            </div>
            <div style="display:flex; align-items:center; gap:10px;">
              <span id="tp-timer">00:00 / 03:30</span>
              <button id="tp-toggle-btn" onclick="const p = document.getElementById('hackathon-teleprompter'); p.style.opacity = p.style.opacity === '0.2' ? '1' : '0.2';">Toggle</button>
            </div>
          </div>
          <div id="tp-script-text">Ready. Please start Recordly recording now.</div>
        `;
        document.body.appendChild(tp);
      }
    }""")

def update_teleprompter(page, scene_idx, scene_title, script_text, elapsed_sec, total_sec=210):
    """Updates the lower-third narration guide with the exact script to read."""
    m_el, s_el = divmod(int(elapsed_sec), 60)
    m_tot, s_tot = divmod(int(total_sec), 60)
    timer_str = f"{m_el:02d}:{s_el:02d} / {m_tot:02d}:{s_tot:02d}"
    pct = min(100.0, max(0.0, (elapsed_sec / total_sec) * 100))

    page.evaluate("""({ title, script, timer, pct }) => {
      const titleEl = document.getElementById('tp-scene-title');
      const scriptEl = document.getElementById('tp-script-text');
      const timerEl = document.getElementById('tp-timer');
      const fillEl = document.getElementById('tp-progress-bar-fill');
      if (titleEl) titleEl.textContent = title;
      if (scriptEl) scriptEl.textContent = script;
      if (timerEl) timerEl.textContent = timer;
      if (fillEl) fillEl.style.width = pct + '%';
    }""", {
        "title": f"SCENE {scene_idx} / {len(SCENES)}: {scene_title.upper()}",
        "script": script_text,
        "timer": timer_str,
        "pct": pct
    })

def smooth_move_cursor(page, target_x, target_y, steps=10, sleep_step=0.006):
    """Snappy yet smooth cursor movement for Recordly auto-zooms without dragging."""
    cur_pos = page.evaluate("""() => {
      const c = document.getElementById('playwright-virtual-cursor');
      if (!c) return { x: 500, y: 300 };
      const r = c.getBoundingClientRect();
      return { x: r.left, y: r.top };
    }""")
    start_x, start_y = cur_pos["x"], cur_pos["y"]

    for i in range(1, steps + 1):
        t = i / steps
        # Smooth easeInOutCubic curve
        ease = 4 * t * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 3) / 2
        cx = start_x + (target_x - start_x) * ease
        cy = start_y + (target_y - start_y) * ease

        page.evaluate("""({ x, y }) => {
          const c = document.getElementById('playwright-virtual-cursor');
          if (c) {
            c.style.transform = `translate(${x}px, ${y}px)`;
          }
        }""", {"x": cx, "y": cy})
        page.mouse.move(cx, cy)
        time.sleep(sleep_step)

def smooth_click(page, selector, hover_time=0.18):
    """Finds element, quickly glides to center, triggers Recordly zoom, and clicks."""
    el = page.query_selector(selector)
    if not el:
        return False
    box = el.bounding_box()
    if not box:
        return False
    target_x = box["x"] + box["width"] / 2
    target_y = box["y"] + box["height"] / 2

    smooth_move_cursor(page, target_x, target_y)
    time.sleep(hover_time)

    # Click animation
    page.evaluate("""() => {
      const c = document.getElementById('playwright-virtual-cursor');
      if (c) {
        c.classList.remove('clicking');
        void c.offsetWidth;
        c.classList.add('clicking');
      }
    }""")
    page.mouse.click(target_x, target_y)
    time.sleep(0.12)
    return True

def human_type(page, selector, text, delay=0.012):
    """Fast, snappy, realistic typing (12ms per char vs previous sluggish 45ms)."""
    smooth_click(page, selector)
    page.fill(selector, "")
    for ch in text:
        page.type(selector, ch, delay=int(delay * 1000))
    time.sleep(0.15)

# ──────────────────────────────────────────────────────────
# Main Automation Routine
# ──────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────
# Main Automation Routine
# ──────────────────────────────────────────────────────────
def run_hackathon_demo(is_fast=False, is_headless=False, speed_mult=1.0):
    speed_factor = 0.15 if is_fast else (1.0 / max(0.1, speed_mult))
    def s_sleep(duration):
        time.sleep(duration * speed_factor)

    TARGET_DURATION_SEC = 195  # 3 minutes 15 seconds (Safe within 3:00 - 4:00 window)

    print("=" * 70)
    print("  JEWEL-AI: RECORDLY HACKATHON DEMO AUTOMATOR (FAST & CRISP)")
    print(f"  Target URL: {DEPLOYED_URL}")
    print(f"  Target Pacing: ~3m 15s (195s) [Strictly within 3:00 - 4:00 min gate]")
    print(f"  Mode: {'6x FAST DRY-RUN' if is_fast else f'RECORDLY CAPTURE ({speed_mult}x speed)'}")
    print(f"  Display: {'Headless' if is_headless else 'Headed (1920x1080) for Screen Recording'}")
    print("=" * 70)

    recordings_dir = Path("artifacts/recordings")
    recordings_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = None
        for channel in ["msedge", None]:
            try:
                browser = p.chromium.launch(
                    channel=channel,
                    headless=is_headless,
                    args=[
                        "--start-maximized",
                        "--disable-infobars",
                        "--no-default-browser-check"
                    ]
                )
                print(f"[Browser] Successfully launched with channel: {channel or 'default'}")
                break
            except Exception as e:
                continue

        if not browser:
            print("[Error] Failed to launch Chromium or Microsoft Edge.")
            return

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(recordings_dir),
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        print(f"\n[Navigation] Navigating to {DEPLOYED_URL}...")
        page.goto(DEPLOYED_URL, wait_until="networkidle")
        setup_injected_overlays(page)

        # 3-Second Crisp Countdown Banner
        print("\n>>> PREPARE RECORDLY: Starting 3-second countdown...")
        for count in range(3, 0, -1):
            page.evaluate(f"""() => {{
              const el = document.getElementById('tp-script-text');
              if (el) el.innerHTML = '<b style="color:#D4AF37; font-size:16px;">STARTING RECORDLY VIDEO IN {count}...</b> Focus Recordly app & hit record.';
            }}""")
            s_sleep(1.0)

        start_time = time.time()
        print("\n>>> RECORDING STARTED: Executing fast & crisp demo...")

        # ──────────────────────────────────────────────────
        # SCENE 1: Introduction & GCP Architecture (~18s)
        # ──────────────────────────────────────────────────
        sc1 = SCENES[0]
        update_teleprompter(page, sc1["id"], sc1["title"], sc1["script"], time.time() - start_time, TARGET_DURATION_SEC)
        print(f"\n[Scene 1] {sc1['title']}")

        smooth_move_cursor(page, 200, 45)
        s_sleep(1.0)
        smooth_move_cursor(page, 320, 90)
        s_sleep(1.0)

        # Open GCP Architecture modal
        smooth_click(page, "#btn-nav-gcp-stack")
        s_sleep(1.5)

        # Run Live Vertex AI Ping
        smooth_click(page, "#btn-ping-gemini")
        s_sleep(2.5)

        # View BigQuery Production Schema
        smooth_click(page, "#btn-view-bq-schema")
        s_sleep(2.0)

        # Close GCP modal
        page.evaluate("() => $('#modal-gcp-stack').classList.remove('open')")
        s_sleep(1.0)

        # ──────────────────────────────────────────────────
        # SCENE 2: Conversational AI Concierge & Guardrails (~22s)
        # ──────────────────────────────────────────────────
        sc2 = SCENES[1]
        update_teleprompter(page, sc2["id"], sc2["title"], sc2["script"], time.time() - start_time, TARGET_DURATION_SEC)
        print(f"\n[Scene 2] {sc2['title']}")

        human_type(page, "#chat-input", "Design a solitaire engagement ring in 22k gold, budget ₹60,000")
        smooth_click(page, "#btn-chat-send")
        s_sleep(3.5)

        # Demonstrate Domain Guardrail
        human_type(page, "#chat-input", "Give me recipe for chocolate banana cake")
        smooth_click(page, "#btn-chat-send")
        s_sleep(3.0)

        # ──────────────────────────────────────────────────
        # SCENE 3: 3-Tier Calibrated Variant Engine & CAD Toggles (~24s)
        # ──────────────────────────────────────────────────
        sc3 = SCENES[2]
        update_teleprompter(page, sc3["id"], sc3["title"], sc3["script"], time.time() - start_time, TARGET_DURATION_SEC)
        print(f"\n[Scene 3] {sc3['title']}")

        smooth_click(page, "#btn-starter-ring")
        s_sleep(3.5)

        # Card 1 CAD toggle
        smooth_move_cursor(page, 650, 320)
        s_sleep(1.0)
        smooth_click(page, ".jewel-variant-card:nth-child(1) .view-toggle-btn:last-child")
        s_sleep(1.8)
        smooth_click(page, ".jewel-variant-card:nth-child(1) .view-toggle-btn:first-child")
        s_sleep(1.2)

        # Card 2 CAD toggle
        smooth_move_cursor(page, 1050, 320)
        s_sleep(1.0)
        smooth_click(page, ".jewel-variant-card:nth-child(2) .view-toggle-btn:last-child")
        s_sleep(1.8)

        # Scroll to Showroom Ready-to-Ship Inventory
        page.evaluate("() => window.scrollBy({ top: 400, behavior: 'smooth' })")
        s_sleep(2.0)
        page.evaluate("() => window.scrollTo({ top: 0, behavior: 'smooth' })")
        s_sleep(1.0)

        # ──────────────────────────────────────────────────
        # SCENE 4: Parametric CAD Studio & Real-Time Pricing (~25s)
        # ──────────────────────────────────────────────────
        sc4 = SCENES[3]
        update_teleprompter(page, sc4["id"], sc4["title"], sc4["script"], time.time() - start_time, TARGET_DURATION_SEC)
        print(f"\n[Scene 4] {sc4['title']}")

        smooth_click(page, ".jewel-variant-card:nth-child(2) .btn-launch-customizer")
        s_sleep(1.8)

        # Toggle CAD blueprint
        smooth_click(page, "#cust-toggle-cad")
        s_sleep(1.8)

        # Adjust precious metal alloy
        smooth_click(page, "#sel-metal")
        page.select_option("#sel-metal", "rose_gold")
        s_sleep(1.5)

        # Adjust stone quality
        smooth_click(page, "#sel-stone")
        page.select_option("#sel-stone", "natural_diamond")
        s_sleep(1.5)

        # Adjust Carat slider
        smooth_move_cursor(page, 1450, 480)
        page.fill("#rng-carat", "0.75")
        page.evaluate("() => $('#rng-carat').dispatchEvent(new Event('input'))")
        s_sleep(1.5)

        # Focus on Live Cost Breakdown Box
        smooth_move_cursor(page, 1450, 720)
        s_sleep(2.5)

        # ──────────────────────────────────────────────────
        # SCENE 5: Skin Harmony Colorimetry Harmonizer (~18s)
        # ──────────────────────────────────────────────────
        sc5 = SCENES[4]
        update_teleprompter(page, sc5["id"], sc5["title"], sc5["script"], time.time() - start_time, TARGET_DURATION_SEC)
        print(f"\n[Scene 5] {sc5['title']}")

        smooth_click(page, "#btn-nav-undertone")
        s_sleep(1.8)

        # Simulate Warm Undertone analysis
        page.evaluate("""() => {
          $('#undertone-results-box').style.display = 'block';
          $('#btn-apply-undertone-metal').style.display = 'inline-block';
          $('#ut-detected-profile').textContent = 'Fair-Medium Skin • WARM Golden Undertone';
          $('#ut-undertone-badge').textContent = 'WARM GOLDEN';
          $('#ut-styling-notes').innerHTML = 'Gemini 2.5 Vision Colorimetry: Warm yellow gold and rose gold reflect ambient luster, enhancing facial radiance.';
          $('#ut-metals-list').innerHTML = '<span class="status-badge" style="background:var(--gold-soft); color:var(--gold-dark); padding:3px 8px; border-radius:4px;">22k Yellow Gold</span><span class="status-badge" style="background:var(--gold-soft); color:var(--gold-dark); padding:3px 8px; border-radius:4px;">18k Rose Gold</span>';
          $('#ut-gems-list').innerHTML = '<span class="status-badge" style="background:#E6F4EA; color:#137333; padding:3px 8px; border-radius:4px;">Emerald</span><span class="status-badge" style="background:#E6F4EA; color:#137333; padding:3px 8px; border-radius:4px;">Polki Diamonds</span>';
        }""")
        s_sleep(3.0)

        # Apply prescribed metal
        smooth_click(page, "#btn-apply-undertone-metal")
        s_sleep(1.5)

        # ──────────────────────────────────────────────────
        # SCENE 6: Old Gold Circular Trade-In & Melting Appraisal (~18s)
        # ──────────────────────────────────────────────────
        sc6 = SCENES[5]
        update_teleprompter(page, sc6["id"], sc6["title"], sc6["script"], time.time() - start_time, TARGET_DURATION_SEC)
        print(f"\n[Scene 6] {sc6['title']}")

        smooth_click(page, "#btn-nav-tradein")
        s_sleep(2.0)

        smooth_move_cursor(page, 960, 620)
        s_sleep(2.0)

        smooth_click(page, "#btn-apply-tradein-credit")
        s_sleep(1.8)

        # ──────────────────────────────────────────────────
        # SCENE 7: BIS HUID Passport & Karigar Job Sheet (~18s)
        # ──────────────────────────────────────────────────
        sc7 = SCENES[6]
        update_teleprompter(page, sc7["id"], sc7["title"], sc7["script"], time.time() - start_time, TARGET_DURATION_SEC)
        print(f"\n[Scene 7] {sc7['title']}")

        smooth_click(page, "#btn-nav-cert")
        s_sleep(2.5)
        page.evaluate("() => $('#modal-certificate').classList.remove('open')")
        s_sleep(1.0)

        smooth_click(page, "#btn-top-jobcard")
        s_sleep(2.5)
        page.evaluate("() => $('#job-card-modal').classList.remove('open')")
        s_sleep(1.0)

        # ──────────────────────────────────────────────────
        # SCENE 8: Merchant Intelligence & Cloud Run Summary (~8s)
        # ──────────────────────────────────────────────────
        sc8 = SCENES[7]
        update_teleprompter(page, sc8["id"], sc8["title"], sc8["script"], time.time() - start_time, TARGET_DURATION_SEC)
        print(f"\n[Scene 8] {sc8['title']}")

        smooth_click(page, "#tab-mode-merchant")
        s_sleep(2.5)

        page.evaluate("() => window.scrollBy({ top: 350, behavior: 'smooth' })")
        s_sleep(2.0)

        total_elapsed = time.time() - start_time
        m_tot, s_tot = divmod(int(total_elapsed), 60)
        print(f"\n" + "=" * 70)
        print(f"  DEMO AUTOMATION COMPLETED IN {m_tot:02d}:{s_tot:02d}!")
        print("  Status: Strictly within the 3:00 to 4:00 minute Hackathon Window.")
        print(f"  Backup Video Saved To: {recordings_dir.resolve()}")
        print("=" * 70)

        s_sleep(2.0)
        context.close()
        browser.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Jewel-AI Recordly Hackathon Demo Automator")
    parser.add_argument("--fast", action="store_true", help="Run at 6x speed for quick testing (~20 seconds)")
    parser.add_argument("--headless", action="store_true", help="Run headless without opening a visible browser window")
    parser.add_argument("--speed", type=float, default=1.0, help="Speed multiplier (e.g. 1.25 to make it 25% faster)")
    args = parser.parse_args()

    run_hackathon_demo(is_fast=args.fast, is_headless=args.headless, speed_mult=args.speed)


