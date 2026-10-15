import os
from typing import Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .models import DesignSpec
from . import pricing, store, render, trends

app = FastAPI(title="Jewel-AI")


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
        raise HTTPException(503, f"Gemini call failed: {e}")
    spec = ai.merge(req.spec, turn)
    ready = bool(turn.ready and spec.budget_inr and spec.occasion)
    return {"reply": turn.reply, "spec": spec.model_dump(), "ready": ready}


@app.post("/api/price")
def price(spec: DesignSpec):
    return {"price": pricing.price(spec), "suggestions": pricing.budget_levers(spec)}


@app.post("/api/variants")
def variants(spec: DesignSpec):
    return {"variants": pricing.make_variants(spec)}



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
    return {"image": render.render_image(spec)}


@app.get("/api/trends")
def get_trends(occasion: str = "", style: str = ""):
    return trends.get_trends(occasion, style)


@app.post("/api/requests")
def save_request(r: ReqIn):
    return {"id": store.save(r.spec, r.status, r.id)}


@app.get("/api/insights")
def get_insights():
    return store.insights()


if os.path.isdir("static"):  # frontend goes here next
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
