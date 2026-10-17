import os
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
from . import pricing, store, render, trends, catalog, artisan

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
    spec = ai.merge(req.spec, turn)
    ready = bool(turn.ready and spec.budget_inr and spec.occasion)
    return {"reply": turn.reply, "spec": spec.model_dump(), "ready": ready}


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
        spec = ai.inspiration_to_spec(result)
        return {
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
        spec = ai.inspiration_to_spec(result)
        return {
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


if os.path.isdir("static"):  # frontend goes here next
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
