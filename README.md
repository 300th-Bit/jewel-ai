# Jewel-AI: Autonomous Jewellery Design Studio and Merchant Intelligence Copilot

[![Google Cloud AI Builder Hackathon](https://img.shields.io/badge/Google%20Cloud-AI%20Builder%20Hackathon-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Built with Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash%20Vision-blue?logo=google-gemini&logoColor=white)](https://ai.google.dev/)
[![Tests Passing](https://img.shields.io/badge/Tests-10%20%2F%2010%20Passed-10B981)](tests/)
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

### 5. Merchant BI and Demand Forecasting (`app/store.py`)
- **Executive KPI Metrics**: Demand pipeline value, conversion velocity, forecasted gold weight and diamond carats.
- **Predictive Demand Model**: Incorporates seasonal multipliers based on the Indian commercial calendar (Peak Wedding Season, Akshaya Tritiya, Diwali/Dhanteras).
- **Raw Material Procurement Advisor**: Actionable guidance for store owners on purchasing bullion grain and sourcing gemstones prior to demand surges.
- **Customer Segmentation**: Automatic categorization into Budget-Conscious, Mid-Range, and High-Net-Worth Bridal buyers.
- **BigQuery Warehouse Integration**: Generates table schemas and JSONL data streams for enterprise Google Cloud warehousing.

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
- **Customer Studio**: [http://localhost:8080](http://localhost:8080)
- **Store Demand and Intelligence Dashboard**: [http://localhost:8080/dashboard.html](http://localhost:8080/dashboard.html)
- **Interactive OpenAPI Documentation (Swagger)**: [http://localhost:8080/docs](http://localhost:8080/docs)

---

## Automated Testing

Run the full test suite to verify deterministic pricing, multi-category models, catalog matching, artisan job cards, and demand forecasting:

```powershell
python -m pytest
```

All test suites pass:
```
tests/test_pricing.py ........  [ 80%]
tests/test_store.py ..          [100%]
===================== 10 passed in 4.30s =====================
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
| `/api/catalog/summary`| `GET` | Summary of inventory SKUs, stock counts, and total inventory value |
| `/api/artisan/job-card`| `POST` | Generates formal goldsmith workshop job sheet with BIS hallmarking |
| `/api/artisan/whatsapp`| `POST` | Creates pre-filled WhatsApp quotation link for direct sharing |
| `/api/forecast` | `GET` | 30-day predictive demand, raw material requirements, and procurement advice |
| `/api/gold-rate` | `GET` | Live 24k gold rate grounded via Google Search with fallback |
| `/api/trends` | `GET` | Real-time Indian jewellery fashion cues grounded via Google Search |
| `/api/insights` | `GET` | Retailer store analytics, category mix, velocity, and recent orders |
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
| **Hyper-personalization** | Multimodal Gemini Vision converts photos into custom designs within budget constraints. |
| **Conversational Commerce** | Chat assistant co-creates jewellery across 4 categories and produces instant quotes. |
| **Product Discovery** | In-stock showroom similarity engine bridges custom design with instant sales. |
| **Demand Forecasting** | 30-day predictive modeling aggregates metal weight and gemstone carats for seasonal surges. |
| **Operational Efficiency** | Karigar job sheets ensure hallmarking compliance and strict +/-5% gross/net tolerances. |
| **Google Cloud Tech** | Gemini 2.5 Flash, Vertex AI Vision, Google Search Grounding, BigQuery AI schema, Cloud Run. |
