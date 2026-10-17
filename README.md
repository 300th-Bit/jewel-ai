# Jewel-AI: Autonomous Jewellery Design Studio and Merchant Intelligence Copilot

[![Google Cloud AI Builder Hackathon](https://img.shields.io/badge/Google%20Cloud-AI%20Builder%20Hackathon-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Built with Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash%20Vision-blue?logo=google-gemini&logoColor=white)](https://ai.google.dev/)
[![Tests Passing](https://img.shields.io/badge/Tests-17%20%2F%2017%20Passed-10B981)](tests/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Python%203.12-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

**Jewel-AI** is an enterprise-grade artificial intelligence commerce and demand intelligence platform engineered for independent jewellery retailers. It transforms how traditional jewellers engage with clients, quote bespoke heirloom pieces, and manage precious metals and gemstone inventory.

Developed for the **Google Cloud AI Builder Hackathon** (*Retail & Commerce: Intelligent Customer and Business Experiences*), Jewel-AI addresses the core challenges across physical and digital commerce:
1. **Multimodal Co-Creation**: Customers provide inspiration imagery (from social media, sketches, or family heirlooms), and **Gemini 2.5 Vision** extracts category, motif, precious alloy, gemstone parameters, and occasion context.
2. **Deterministic Indian Pricing Engine**: Replaces subjective quotes with real-time bullion rates grounded via Google Search Grounding, Bureau of Indian Standards (BIS) hallmarking grades (916, 750, 585), volumetric metal weight calculation, making charges, and GST.
3. **In-Stock Showroom Discovery**: Similarity matching connects customer design specifications to ready-to-ship showroom inventory for immediate in-store fulfillment.
4. **Artisan / Karigar Hand-off**: Generates formal workshop job sheets with gross/net gold tolerances and one-click WhatsApp quotations.
5. **Predictive Demand and Procurement BI**: Aggregates customer design telemetry to forecast 30-day bullion requirements (grams of 22k/18k gold) and diamond carats, advising merchants prior to festive surges (Diwali, Dhanteras, Akshaya Tritiya, wedding season).
6. **BigQuery Enterprise Warehousing**: Provides schema definitions and JSONL data export ready for Google Cloud BigQuery retail analytics.

---

## System Architecture

```
+------------------------------------------------------------------------+
|                        CUSTOMER DESIGN STUDIO                          |
|  Multimodal Inspiration Drop  |  Category Switcher (Rings, Necklaces)  |
|  Real-Time CAD Vector Engine  |  Interactive Metallurgical Levers      |
|  In-Stock Showroom Matcher    |  WhatsApp Quotation Generator          |
+-----------------------------------+------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
|                        FASTAPI COMMERCE GATEWAY                        |
|  /api/analyze-image  |  /api/price  |  /api/variants  |  /api/catalog   |
|  /api/artisan/job-card  |  /api/forecast  |  /api/gold-rate            |
+------+----------------------+---------------------------+--------------+
       |                      |                           |
       v                      v                           v
+--------------+      +----------------+      +-------------------------+
| GEMINI 2.5   |      | DETERMINISTIC  |      | LOCAL REPOSITORY AND    |
| VISION & AI  |      | PRICING ENGINE |      | DEMAND FORECASTER       |
| Multi-turn   |      | Weight = f(vol)|      | SQLite DB (zero setup)  |
| extraction & |      | 24k/22k/18k/14k|      | 30-day seasonal forecast|
| Search Tools |      | Making + 3% GST|      | BigQuery Schema Export  |
+--------------+      +----------------+      +-------------------------+
```

---

## Key Features and Capabilities

### 1. Multimodal Inspiration Analyzer (Gemini 2.5 Vision)
- Accepts drag-and-drop or file upload of any jewellery photo or sketch.
- Gemini 2.5 inspects the structural architecture and extracts:
  - **Category**: Ring, Necklace, Earrings, Bangle.
  - **Motif and Style**: Temple-inspired, Polki, Solitaire, Filigree, Floral Cluster.
  - **Metal and Karatage**: 24k fine, 22k standard (916 BIS), 18k bridal (750), 14k everyday (585).
  - **Center Stone and Setting**: Natural diamond, lab-grown CVD diamond, moissanite, cubic zirconia, prong, bezel, pave.
  - **Occasion Context**: Wedding, Engagement, Anniversary, Festival, Daily wear.
- Automatically translates analysis into a structured `DesignSpec` and generates 3 budget-aligned variations.

### 2. Multi-Category Procedural Vector Engine
- High-precision SVG rendering calibrated for physical dimensions:
  - **Rings**: Solitaire, halo, band widths (1.8mm - 6.0mm), prong geometry, and reflections.
  - **Necklaces**: Royal rope chains, adjustable lengths (14 to 26 inches), pendant bail, center stone, and filigree motifs.
  - **Earrings**: Temple Jhumkas with bell dome and hanging pearls, Solitaire Studs, Modern Drops, and Pave Hoops.
  - **Bangles**: Indian standard sizing (`2-2`, `2-4`, `2-6`, `2-8`), isometric rim, and bezel settings.
- Dual-mode renderer: instantaneous vector blueprint alongside photorealistic studio assets.

### 3. In-Stock Showroom Discovery Matcher (`app/catalog.py`)
- Bridges custom co-creation with immediate inventory sales:
  - Performs multi-dimensional similarity matching against ready-to-ship store items.
  - Displays SKU, matching percentage, stock quantities, and instant checkout options.

### 4. Karigar Job Sheet and WhatsApp Quotation (`app/artisan.py`)
- Generates official workshop job orders with:
  - Unique tracking ID (e.g., `JOB-N-C42948`).
  - Certified BIS Hallmarking grade (**916** for 22k, **750** for 18k).
  - Estimated Gross Weight vs. Net Gold Weight with a strict +/-5% manufacturing tolerance.
  - Exact stone counts, carat weight, and setting instructions.
  - Direct WhatsApp quote generation (`wa.me`) for transparent customer communication.

### 5. Interactive 3D WebGL CAD Viewport (Three.js)
- Real-time 360-degree orbital rotation, zoom, and inspection.
- Procedural geometries tailored for rings, necklaces, jhumkas, and bangles.
- Real-time metallic shaders (22k Royal Gold, 18k Rose Gold, Platinum 950) with surface finish toggles (Mirror High-Polish, Satin Matte, Hand-Hammered).
- Multi-environment lighting simulation (Atelier Softbox, Intimate Candlelight, Pure Sunlight).

### 6. Live Virtual Try-On & Gemini Skin Undertone Stylist (`app/undertone.py`)
- Multimodal portrait analysis using Gemini 2.5 Vision to identify skin tone and undertone (Warm, Cool, Neutral, Olive).
- AI color harmony prescription recommending metal alloys and gemstone cuts that optimize skin luminescence.
- Interactive AR canvas with real-time sliders for scale, vertical/horizontal offset, and rotation.

### 7. Circular Commerce: Old Gold Trade-In Engine (`app/tradein.py`)
- Solves the primary payment friction in retail jewellery where 60%+ of bespoke orders are funded by trading in old family gold.
- Itemized scrap ornament ledger calculating net gold recovery, certified purity factor, 1.2% refinery melting loss, and ₹35/g assay charges.
- Generates official `EXCH-XXXXXX` trade-in vouchers and applies instant balance credit against bespoke orders.

### 8. Digital Certificate & 6-Digit BIS HUID Passport (`app/certification.py`)
- Generates tamper-proof gemological provenance certificates.
- 6-character laser-inscribed BIS Hallmark Unique Identification (HUID) matching Government of India standards.
- Diamond 4Cs grading (Hearts & Arrows Cut, Colorless, VVS1 clarity) and Kimberley Process conflict-free ethical declaration.

### 9. Merchant Intelligence Command Center (`app/merchant.py`)
- **BigQuery AI Festival Demand Forecasting**: Predictive surge models across Dhanteras, Diwali, Akshaya Tritiya, and Winter Wedding Muhurats.
- **Bullion Volatility Stress-Testing (Hedging Engine)**: Interactive price shock simulator (-15% to +15%) showing inventory P&L, unhedged order margin risk, and MCX Gold Mini futures hedging guidance.
- **Dead-Stock Remounting Optimizer**: Identifies aged showcase inventory (>90 days) and recommends converting heavy ornaments into high-velocity lightweight dailywear.
- **Gemini Merchant Copilot**: Natural language executive advisory for store owners on bullion procurement, making charges, and working capital optimization.

---

## Quickstart and Local Setup

### 1. Prerequisites
- **Python 3.12+**
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### 2. Configure Environment
Create or edit `.env` in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8080
```

### 3. Install Dependencies
```powershell
pip install -r requirements-dev.txt
```

### 4. Run the Dev Server
```powershell
python -m uvicorn app.main:app --port 8080 --host 127.0.0.1 --reload
```

Access the interfaces:
- **Haute Joaillerie Atelier Studio**: [http://localhost:8080](http://localhost:8080)
- **Store Demand and Intelligence Dashboard**: [http://localhost:8080/dashboard.html](http://localhost:8080/dashboard.html)
- **Interactive OpenAPI Documentation (Swagger)**: [http://localhost:8080/docs](http://localhost:8080/docs)

---

## Automated Testing

Run the full test suite verifying deterministic pricing, multi-category models, catalog matching, artisan job cards, old gold trade-in, stress testing, and gemological certification:

```powershell
python -m pytest tests/
```

All 17 test suites pass:
```
tests/test_innovations.py ....... [ 41%]
tests/test_pricing.py ........    [ 88%]
tests/test_store.py ..            [100%]
===================== 17 passed in 4.08s =====================
```

---

## API Reference Overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/analyze-image` | `POST` | Upload photo for multimodal Gemini 2.5 Vision analysis and spec extraction |
| `/api/chat` | `POST` | Conversational design consultation with structured spec extraction |
| `/api/price` | `POST` | Deterministic pricing breakdown (bullion, stone, setting, making charges, GST) |
| `/api/variants` | `POST` | Generates 3 calibrated variants (Budget-smart, Balanced, Statement) |
| `/api/catalog/match` | `POST` | Similarity matching against ready-to-ship showroom inventory |
| `/api/artisan/job-card`| `POST` | Generates formal goldsmith workshop job sheet with BIS hallmarking |
| `/api/artisan/whatsapp`| `POST` | Creates pre-filled WhatsApp quotation link for direct sharing |
| `/api/undertone/analyze-b64`| `POST` | Gemini skin undertone analysis and metal harmony prescription |
| `/api/tradein/appraise`| `POST` | Old gold circular exchange appraisal and credit voucher generator |
| `/api/merchant/demand` | `GET` | Multi-festival predictive demand surge and bullion requirements |
| `/api/merchant/stress-test`| `POST` | Gold price shock simulation and MCX hedging risk advisor |
| `/api/merchant/dead-stock`| `GET` | Aged showroom inventory remounting recommendations |
| `/api/merchant/copilot`| `POST` | Executive retail strategy questions answered by Gemini |
| `/api/certificate/generate`| `POST` | Generates tamper-proof digital gemological certificate with 6-digit BIS HUID |
| `/api/forecast` | `GET` | 30-day predictive demand, raw material requirements, and procurement advice |
| `/api/gold-rate` | `GET` | Live 24k gold rate grounded via Google Search with fallback |
| `/api/trends` | `GET` | Real-time Indian jewellery fashion cues grounded via Google Search |
| `/api/health` | `GET` | Service liveness and health probe |

---

## Google Cloud Deployment (Cloud Run)

Deploy directly to **Google Cloud Run** using the Google Cloud CLI:

```bash
gcloud run deploy jewel-ai \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --max-instances 1 \
  --set-env-vars GEMINI_API_KEY=your_key
```

---

## Hackathon Alignment: Retail and Commerce

| Hackathon Dimension | Jewel-AI Implementation |
|---|---|
| **Hyper-personalization** | Multimodal Gemini Vision converts photos into custom designs within budget constraints. Skin undertone harmonizer selects matching alloys. |
| **Conversational Commerce** | Chat assistant co-creates jewellery across 4 categories, generates instant quotes, and powers the Executive Merchant Copilot. |
| **Product Discovery & Try-On**| Three.js 3D CAD viewport allows 360-degree inspection; AR canvas offers live Virtual Try-On; catalog similarity matches ready inventory. |
| **Circular Commerce** | Transparent Old Gold Trade-in calculator offsets high-ticket bespoke purchases with scrap bullion value. |
| **Demand Forecasting & Risk**| BigQuery AI multi-festival predictive surge modeling and bullion volatility stress-testing insulate merchant margins. |
| **Operational Efficiency** | Karigar job sheets ensure hallmarking compliance; 6-digit BIS HUID passports guarantee provenance and fraud prevention. |
| **Google Cloud Tech** | Gemini 2.5 Flash, Vertex AI Vision, Google Search Grounding, BigQuery AI schema, Cloud Run. |
