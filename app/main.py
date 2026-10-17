import os
import json
import base64
from typing import Literal, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .models import DesignSpec
from . import pricing, store, render, trends, catalog, artisan, undertone, tradein, merchant, certification

app = FastAPI(title="Jewel-AI", description="AI design and sales assistant for independent jewellers")


class Msg(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatReq(BaseModel):
    messages: list[Msg]
    spec: DesignSpec = Field(default_factory=DesignSpec)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/chat")
def chat(req: ChatReq):
    from . import ai  # lazy: other endpoints work without GCP credentials
    try:
        turn = ai.chat_turn([m.model_dump() for m in req.messages])
    except Exception as e:
        last_text = req.messages[-1].content if req.messages else ""
        turn = ai.fallback_turn(last_text)

    is_off_topic = getattr(turn, "is_off_topic", False)
    if is_off_topic:
        return {
            "reply": turn.reply,
            "spec": req.spec.model_dump(),
            "ready": False,
            "is_off_topic": True
        }

    spec = ai.merge(req.spec, turn)
    ready = bool(turn.ready and spec.budget_inr and spec.occasion)
    return {"reply": turn.reply, "spec": spec.model_dump(), "ready": ready, "is_off_topic": False}


@app.post("/api/price")
def price(spec: DesignSpec):
    return {"price": pricing.price(spec), "suggestions": pricing.budget_levers(spec)}


@app.post("/api/variants")
def variants(spec: DesignSpec):
    return {"variants": pricing.make_variants(spec)}


# ── Store persistence ──

try:
    store.init()
except Exception as e:  # never block startup on storage
    print("store init failed:", e)


class ReqIn(BaseModel):
    id: Optional[str] = None
    status: Literal["designed", "sent"] = "designed"
    spec: DesignSpec


@app.post("/api/render")
def render_ring(spec: DesignSpec):
    return {"image": render.render_image(spec), "fallback": render.get_curated_image(spec)}


@app.post("/api/curated-image")
def curated_image(spec: DesignSpec):
    return {"image": render.get_curated_image(spec)}


@app.get("/api/trends")
def get_trends(occasion: str = "", style: str = ""):
    return trends.get_trends(occasion, style)


@app.post("/api/requests")
def save_request(r: ReqIn):
    return {"id": store.save(r.spec, r.status, r.id)}


@app.get("/api/insights")
def get_insights():
    return store.insights()


# ── New endpoints: Vision, Catalog, Artisan, Forecast ──

@app.post("/api/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    """Analyze an uploaded jewellery inspiration image using Gemini Vision."""
    from . import ai
    try:
        data = await file.read()
        mime = file.content_type or "image/jpeg"
        if not mime.startswith("image/"):
            raise HTTPException(400, "Upload must be an image file")
        if len(data) > 10 * 1024 * 1024:
            raise HTTPException(400, "Image too large (max 10MB)")
        result = ai.analyze_inspiration(data, mime)
        if not result.is_jewellery or result.confidence < 0.35:
            return {
                "ok": False,
                "is_jewellery": False,
                "error": "unrelated_image",
                "message": result.rejection_reason or result.description or "The uploaded photo does not appear to be jewelry or a jewelry design sketch. Please upload a jewelry photo or sketch.",
                "analysis": result.model_dump(),
            }
        spec = ai.inspiration_to_spec(result)
        return {
            "ok": True,
            "is_jewellery": True,
            "analysis": result.model_dump(),
            "spec": spec.model_dump(),
            "price": pricing.price(spec),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(503, f"Image analysis failed: {e}")


class AnalyzeBase64Req(BaseModel):
    image_b64: str
    mime_type: str = "image/jpeg"


@app.post("/api/analyze-image-b64")
def analyze_image_b64(req: AnalyzeBase64Req):
    """Analyze a base64-encoded jewellery inspiration image."""
    from . import ai
    try:
        data = base64.b64decode(req.image_b64)
        result = ai.analyze_inspiration(data, req.mime_type)
        if not result.is_jewellery or result.confidence < 0.35:
            return {
                "ok": False,
                "is_jewellery": False,
                "error": "unrelated_image",
                "message": result.rejection_reason or result.description or "The uploaded photo does not appear to be jewelry or a jewelry design sketch. Please upload a jewelry photo or sketch.",
                "analysis": result.model_dump(),
            }
        spec = ai.inspiration_to_spec(result)
        return {
            "ok": True,
            "is_jewellery": True,
            "analysis": result.model_dump(),
            "spec": spec.model_dump(),
            "price": pricing.price(spec),
        }
    except Exception as e:
        raise HTTPException(503, f"Image analysis failed: {e}")


@app.post("/api/catalog/match")
def catalog_match(spec: DesignSpec):
    """Find in-stock inventory items matching a customer's design spec."""
    matches = catalog.find_matches(spec)
    return {"matches": matches, "total_catalog": len(catalog.CATALOG)}


@app.get("/api/catalog/summary")
def catalog_summary_api():
    """Get store inventory summary."""
    return catalog.catalog_summary()


@app.post("/api/artisan/job-card")
def job_card(spec: DesignSpec):
    """Generate a karigar manufacturing job card."""
    return artisan.generate_job_card(spec)


@app.post("/api/artisan/whatsapp")
def whatsapp_link(spec: DesignSpec):
    """Generate a WhatsApp sharing link with the design quote."""
    return {"link": artisan.generate_whatsapp_link(spec)}


@app.get("/api/forecast")
def forecast():
    """Get 30-day demand forecast and material requirements."""
    return store.demand_forecast()


@app.get("/api/gold-rate")
def gold_rate():
    """Get current gold rate (live grounded or fallback)."""
    rate = pricing.get_gold_rate()
    live = pricing.fetch_live_gold_rate()
    return {
        "gold_rate_24k_per_g": rate,
        "source": "live_grounded" if live else "fallback_placeholder",
        "rates": {m: round(rate * p, 2) for m, p in pricing.PURITY.items()},
    }


# ── Game-Changing Pillars: Undertone, Circular Trade-In, Merchant Intelligence, Certification ──

@app.post("/api/undertone/analyze")
async def analyze_undertone_file(file: UploadFile = File(...)):
    """Analyze customer portrait/skin tone using Gemini Vision for metal & gem harmony."""
    try:
        data = await file.read()
        mime = file.content_type or "image/jpeg"
        if not mime.startswith("image/"):
            raise HTTPException(400, "Upload must be an image file")
        result = undertone.analyze_skin_undertone(data, mime)
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(503, f"Undertone analysis failed: {e}")


class UndertoneB64Req(BaseModel):
    image_b64: str
    mime_type: str = "image/jpeg"


@app.post("/api/undertone/analyze-b64")
def analyze_undertone_b64(req: UndertoneB64Req):
    """Analyze base64-encoded portrait image for skin undertone."""
    try:
        raw = req.image_b64
        if "," in raw:
            raw = raw.split(",", 1)[1]
        data = base64.b64decode(raw.strip())
        result = undertone.analyze_skin_undertone(data, req.mime_type)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(503, f"Undertone analysis failed: {e}")




@app.post("/api/tradein/appraise")
def appraise_old_gold(req: tradein.TradeInRequest):
    """Calculate transparent old gold exchange valuation and generate credit voucher."""
    return tradein.appraise_trade_in(req).model_dump()


@app.get("/api/merchant/demand")
def merchant_demand_intelligence():
    """Predictive festival demand metrics and bullion targets."""
    return merchant.get_demand_intelligence()


@app.post("/api/merchant/stress-test")
def merchant_stress_test(req: merchant.StressTestRequest):
    """Simulate gold volatility (+/- 5%, 10%, 15%) on inventory and unhedged orders."""
    return merchant.run_bullion_stress_test(req)


@app.get("/api/merchant/dead-stock")
def merchant_dead_stock_opportunities():
    """Identifies aged showroom stock and models capital gains from remounting."""
    return merchant.get_dead_stock_remount_opportunities()


@app.post("/api/merchant/copilot")
def merchant_copilot(req: merchant.MerchantCopilotReq):
    """Ask executive jewellery merchandising questions to Gemini Copilot."""
    return merchant.ask_merchant_copilot(req)


class CertReq(BaseModel):
    spec: DesignSpec
    patron_name: Optional[str] = "Valued Patron"


@app.post("/api/certificate/generate")
def generate_certificate(req: CertReq):
    """Generate tamper-proof digital certificate of authenticity with 6-digit BIS HUID."""
    return certification.issue_certificate(req.spec, req.patron_name).model_dump()


@app.get("/api/merchant/bigquery/export")
def export_bigquery_data():
    """Export design telemetry formatted for Google Cloud BigQuery retail warehousing."""
    records = store.export_bigquery_records()
    return {
        "dataset": "retail_jewel_ai",
        "table": "design_requests",
        "record_count": len(records),
        "records": records,
        "jsonl_sample": [json.dumps(r) for r in records[:5]],
        "ddl_location": "data/bigquery_schema.sql"
    }


@app.get("/api/merchant/bigquery/schema")
def get_bigquery_schema():
    """Retrieve BigQuery DDL schema and analytical queries."""
    sql_path = os.path.join("data", "bigquery_schema.sql")
    sql_content = ""
    if os.path.exists(sql_path):
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
    return {
        "dataset": "retail_jewel_ai",
        "sql": sql_content
    }



if os.path.isdir("static"):  # frontend goes here next
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
