"""Gemini on Vertex AI: conversation + structured preference extraction."""
import os
import time
from typing import Optional
from pydantic import BaseModel
from google import genai
from google.genai import types
from .models import DesignSpec, Stone

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
_client = None


def client():
    """Dev: GEMINI_API_KEY (free key from aistudio.google.com).
    Deployed: Vertex AI via the Cloud Run service account."""
    global _client
    if _client is None:
        if os.getenv("GEMINI_API_KEY"):
            _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        else:
            _client = genai.Client(
                vertexai=True,
                project=os.environ["GOOGLE_CLOUD_PROJECT"],
                location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
            )
    return _client


class ChatTurn(BaseModel):
    reply: str
    ready: bool = False
    style: Optional[str] = None
    metal: Optional[str] = None            # gold_24k|gold_22k|gold_18k|gold_14k
    band_width_mm: Optional[float] = None
    ring_size_in: Optional[int] = None
    stone_type: Optional[str] = None       # none|cz|moissanite|lab_diamond|natural_diamond
    stone_carat: Optional[float] = None
    occasion: Optional[str] = None
    budget_inr: Optional[int] = None
    notes: Optional[str] = None


SYSTEM = """You are a warm, expert jewellery consultant for an Indian jewellery store.
Goal: understand the customer's occasion, taste and budget (INR) for a RING, then fill the design fields.
Rules:
- Reply in the customer's language (English, Hindi, Kannada, etc.). Keep replies to 1-3 short sentences.
- Ask ONE question at a time. Priority: occasion, budget, style/taste, metal, stone, ring size.
- Only set fields the customer stated or clearly implied; leave others null.
- If they say "lab-grown" use lab_diamond; "diamond" alone -> natural_diamond.
- Set ready=true only when occasion and budget_inr are known.
- Never quote prices yourself; the store's price engine does that."""


FALLBACKS = [m for m in os.getenv(
    "GEMINI_FALLBACKS", "gemini-2.5-flash-lite,gemini-2.0-flash").split(",") if m]


def chat_turn(messages: list[dict]) -> ChatTurn:
    """Try the main model with retries, then fall back to other models.
    Handles temporary 503 'high demand' and 429 rate-limit errors."""
    contents = [
        types.Content(role="user" if m["role"] == "user" else "model",
                      parts=[types.Part.from_text(text=m["content"])])
        for m in messages
    ]
    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM, response_mime_type="application/json",
        response_schema=ChatTurn, temperature=0.4)
    last = None
    for model in [MODEL] + FALLBACKS:
        for attempt in range(3):
            try:
                resp = client().models.generate_content(model=model, contents=contents, config=cfg)
                return ChatTurn.model_validate_json(resp.text)
            except Exception as e:  # noqa
                last = e
                msg = str(e)
                transient = any(k in msg for k in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500"))
                if not transient:
                    break  # e.g. model not found / bad key: try next model, no retry
                time.sleep(1.5 * (attempt + 1))
    raise last


def merge(spec: DesignSpec, t: ChatTurn) -> DesignSpec:
    """Apply extracted fields onto the spec, ignoring invalid values."""
    d = spec.model_dump()
    for f in ("style", "occasion", "notes", "budget_inr"):
        if getattr(t, f) is not None:
            d[f] = getattr(t, f)
    if t.metal in ("gold_24k", "gold_22k", "gold_18k", "gold_14k"):
        d["metal"] = t.metal
    if t.band_width_mm is not None:
        d["band_width_mm"] = min(8, max(1.5, t.band_width_mm))
    if t.ring_size_in is not None:
        d["ring_size_in"] = min(24, max(6, t.ring_size_in))
    if t.stone_type in ("none", "cz", "moissanite", "lab_diamond", "natural_diamond"):
        d["stone"]["type"] = t.stone_type
        if t.stone_type != "none" and not d["stone"]["carat"]:
            d["stone"]["carat"] = 0.3
    if t.stone_carat is not None and d["stone"]["type"] != "none":
        d["stone"]["carat"] = min(3, max(0.05, t.stone_carat))
    return DesignSpec.model_validate(d)
