"""Gemini on Vertex AI: conversation + structured preference extraction + multimodal vision."""
import os
import time
import base64
import re
from typing import Optional
from pydantic import BaseModel, field_validator

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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


# ──────────────────────────────────────────────────────────
# Conversational chat turn
# ──────────────────────────────────────────────────────────

class ChatTurn(BaseModel):
    reply: str
    ready: bool = False
    category: Optional[str] = None          # ring|necklace|earrings|bangle
    style: Optional[str] = None
    metal: Optional[str] = None             # gold_24k|gold_22k|gold_18k|gold_14k
    band_width_mm: Optional[float] = None
    ring_size_in: Optional[int] = None
    earring_type: Optional[str] = None      # stud|jhumka|drop|hoop
    necklace_length_in: Optional[float] = None
    bangle_size_in: Optional[str] = None
    stone_type: Optional[str] = None        # none|cz|moissanite|lab_diamond|natural_diamond
    stone_carat: Optional[float] = None
    stone_count: Optional[int] = None
    occasion: Optional[str] = None
    budget_inr: Optional[int] = None
    notes: Optional[str] = None
    customer_name: Optional[str] = None

    @field_validator("budget_inr", mode="before")
    @classmethod
    def _parse_budget(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, (int, float)):
            return int(v)
        s = str(v).lower().replace(",", "").replace("₹", "").replace("inr", "").replace("rs", "").strip()
        m_lakh = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|l\b)", str(v).lower())
        if m_lakh:
            return int(float(m_lakh.group(1)) * 100000)
        m_k = re.search(r"(\d+(?:\.\d+)?)\s*k\b", str(v).lower())
        if m_k:
            return int(float(m_k.group(1)) * 1000)
        digits = re.findall(r"\d+", s)
        if digits:
            return int("".join(digits))
        return None

    @field_validator("metal", mode="before")
    @classmethod
    def _parse_metal(cls, v):
        if not v:
            return None
        s = str(v).lower()
        if "24" in s:
            return "gold_24k"
        if "22" in s:
            return "gold_22k"
        if "18" in s:
            return "gold_18k"
        if "14" in s:
            return "gold_14k"
        if "gold" in s:
            return "gold_22k"
        return None

    @field_validator("category", mode="before")
    @classmethod
    def _parse_category(cls, v):
        if not v:
            return None
        s = str(v).lower()
        if any(k in s for k in ("neck", "pendant", "choker", "chain", "mangalsutra")):
            return "necklace"
        if any(k in s for k in ("ear", "jhumk", "stud", "drop", "hoop", "bali")):
            return "earrings"
        if any(k in s for k in ("bang", "kada", "bracelet", "valayal", "churi")):
            return "bangle"
        if "ring" in s or "band" in s:
            return "ring"
        return "ring"

    @field_validator("stone_type", mode="before")
    @classmethod
    def _parse_stone(cls, v):
        if not v:
            return None
        s = str(v).lower()
        if "lab" in s:
            return "lab_diamond"
        if "moiss" in s:
            return "moissanite"
        if "cz" in s or "zircon" in s:
            return "cz"
        if any(k in s for k in ("none", "plain", "no stone")):
            return "none"
        if "diamond" in s or "solitaire" in s:
            return "natural_diamond"
        return None

    @field_validator("stone_carat", mode="before")
    @classmethod
    def _parse_carat(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, (int, float)):
            return float(v)
        m = re.search(r"(\d+(?:\.\d+)?)", str(v))
        return float(m.group(1)) if m else None

    @field_validator("stone_count", mode="before")
    @classmethod
    def _parse_count(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, (int, float)):
            return int(v)
        m = re.search(r"\d+", str(v))
        return int(m.group(0)) if m else None

    @field_validator("band_width_mm", mode="before")
    @classmethod
    def _parse_band_width(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, (int, float)):
            return float(v)
        m = re.search(r"(\d+(?:\.\d+)?)", str(v))
        return float(m.group(1)) if m else None

    @field_validator("necklace_length_in", mode="before")
    @classmethod
    def _parse_necklace_len(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, (int, float)):
            return float(v)
        m = re.search(r"(\d+(?:\.\d+)?)", str(v))
        return float(m.group(1)) if m else None

    @field_validator("ring_size_in", mode="before")
    @classmethod
    def _parse_ring_size(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, (int, float)):
            return int(v)
        m = re.search(r"\d+", str(v))
        return int(m.group(0)) if m else None

    @field_validator("earring_type", mode="before")
    @classmethod
    def _parse_earring_type(cls, v):
        if not v:
            return None
        s = str(v).lower()
        if "jhumk" in s:
            return "jhumka"
        if "stud" in s:
            return "stud"
        if "drop" in s:
            return "drop"
        if "hoop" in s or "bali" in s:
            return "hoop"
        return "stud"

    @field_validator("bangle_size_in", mode="before")
    @classmethod
    def _parse_bangle_size(cls, v):
        if not v:
            return None
        s = str(v).strip()
        m = re.search(r"2[-. ]?([2468]|10)", s)
        if m:
            return f"2-{m.group(1)}"
        return "2-4"


SYSTEM = """You are a warm, expert jewellery consultant for an Indian jewellery store.
Goal: understand the customer's occasion, taste and budget (INR) for JEWELLERY, then fill the design fields.
Rules:
- Reply in the customer's language (English, Hindi, Kannada, Tamil, Telugu, etc.). Keep replies to 1-3 short sentences.
- Ask ONE question at a time. Priority: category (ring/necklace/earrings/bangle), occasion, budget, style/taste, metal, stone, size.
- Only set fields the customer stated or clearly implied; leave others null.
- If they say "lab-grown" use lab_diamond; "diamond" alone -> natural_diamond.
- Categories: ring (default), necklace (includes pendants/chains), earrings (studs/jhumkas/drops/hoops), bangle (includes kadas/bracelets).
- Set ready=true only when occasion and budget_inr are known.
- Never quote prices yourself; the store's price engine does that.
- For earrings, ask if they want studs, jhumkas, drops, or hoops.
- For necklaces, consider if they want a simple chain with pendant or a heavier choker/set."""


FALLBACKS = [m for m in os.getenv(
    "GEMINI_FALLBACKS", "gemini-2.5-flash-lite,gemini-2.0-flash").split(",") if m]


def fallback_turn(text: str) -> ChatTurn:
    """Resilient fallback extractor for when Gemini API is offline or rate-limited."""
    s = text.lower()
    
    # 1. Category
    cat = "ring"
    if any(k in s for k in ("necklace", "choker", "pendant", "mangalsutra", "chain")):
        cat = "necklace"
    elif any(k in s for k in ("earring", "jhumka", "stud", "drop", "hoop", "bali")):
        cat = "earrings"
    elif any(k in s for k in ("bangle", "kada", "bracelet", "valayal", "churi")):
        cat = "bangle"
    elif "ring" in s:
        cat = "ring"
        
    # 2. Budget
    budget = None
    m_lakh = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|l\b)", s)
    if m_lakh:
        budget = int(float(m_lakh.group(1)) * 100000)
    else:
        m_k = re.search(r"(\d+(?:\.\d+)?)\s*k\b", s)
        if m_k:
            budget = int(float(m_k.group(1)) * 1000)
        else:
            m_num = re.search(r"(?:₹|rs\.?|inr)?\s*(\d{1,3}(?:,\d{2,3})+|\d{4,7})", s)
            if m_num:
                budget = int(m_num.group(1).replace(",", ""))

    # 3. Metal
    metal = "gold_22k"
    if "24" in s:
        metal = "gold_24k"
    elif "18" in s:
        metal = "gold_18k"
    elif "14" in s:
        metal = "gold_14k"

    # 4. Occasion
    occ = "Special Occasion"
    if "wedding" in s or "bridal" in s or "shaadi" in s:
        occ = "Wedding"
    elif "engagement" in s or "roka" in s:
        occ = "Engagement"
    elif "anniversary" in s:
        occ = "Anniversary"
    elif "diwali" in s or "dhanteras" in s:
        occ = "Diwali"
    elif "akshaya" in s:
        occ = "Akshaya Tritiya"
    elif "birthday" in s:
        occ = "Birthday gift"
    elif "daily" in s or "everyday" in s:
        occ = "Daily wear"

    # 5. Stone
    stone_type = "none"
    carat = 0.0
    if "lab" in s and "diamond" in s:
        stone_type = "lab_diamond"
        carat = 0.5
    elif "diamond" in s or "solitaire" in s:
        stone_type = "natural_diamond"
        carat = 0.4
    elif "moissanite" in s:
        stone_type = "moissanite"
        carat = 0.5
    elif "cz" in s or "zircon" in s:
        stone_type = "cz"
        carat = 0.3

    # 6. Style
    style = "classic elegant"
    if "temple" in s:
        style = "temple-inspired royal"
    elif "polki" in s or "kundan" in s:
        style = "heritage polki"
    elif "floral" in s:
        style = "floral cluster"
    elif "solitaire" in s:
        style = "classic solitaire"
    elif "minimal" in s:
        style = "modern minimalist"

    cat_names = {"ring": "ring", "necklace": "bridal necklace", "earrings": "earrings", "bangle": "bangles"}
    name = cat_names.get(cat, cat)
    budget_str = f" within your ₹{budget:,} budget" if budget else ""
    reply = f"Delighted to design a bespoke {metal[5:]} {name} for your {occ}{budget_str}! I have loaded three tailored variations for you."

    return ChatTurn(
        reply=reply,
        ready=bool(budget is not None and occ is not None),
        category=cat,
        style=style,
        metal=metal,
        stone_type=stone_type,
        stone_carat=carat if stone_type != "none" else 0.0,
        stone_count=1 if stone_type != "none" else 0,
        occasion=occ,
        budget_inr=budget,
        notes=f"{style} {cat}",
    )


def chat_turn(messages: list[dict]) -> ChatTurn:
    """Try the main model with retries, then fall back to other models.
    Normalizes message sequences to guarantee alternation and handles rate limits."""
    # Normalize messages so they alternate user -> model -> user -> model
    normalized = []
    for m in messages:
        role = "user" if m.get("role") == "user" else "model"
        content = str(m.get("content") or "").strip()
        if not content:
            continue
        if normalized and normalized[-1]["role"] == role:
            normalized[-1]["content"] += "\n" + content
        else:
            normalized.append({"role": role, "content": content})

    # Ensure conversation starts with a user message
    while normalized and normalized[0]["role"] != "user":
        normalized.pop(0)

    if not normalized:
        return fallback_turn("Engagement ring, budget 60000")

    contents = [
        types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])])
        for m in normalized
    ]
    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM, response_mime_type="application/json",
        response_schema=ChatTurn, temperature=0.4)

    for model in [MODEL] + FALLBACKS:
        for attempt in range(2):
            try:
                resp = client().models.generate_content(model=model, contents=contents, config=cfg)
                text = (resp.text or "").strip()
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text)
                    text = re.sub(r"\s*```$", "", text)
                return ChatTurn.model_validate_json(text)
            except Exception as e:
                msg = str(e)
                transient = any(k in msg for k in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500"))
                if not transient:
                    break
                time.sleep(1.0 * (attempt + 1))
    
    # Graceful fallback so chat never throws an error to the user
    last_text = normalized[-1]["content"] if normalized else ""
    return fallback_turn(last_text)


# ──────────────────────────────────────────────────────────
# Multimodal inspiration image analysis
# ──────────────────────────────────────────────────────────

class InspirationResult(BaseModel):
    """What the AI sees in an uploaded jewellery photo."""
    category: Optional[str] = None
    style: Optional[str] = None
    metal: Optional[str] = None
    stone_type: Optional[str] = None
    stone_count: Optional[int] = None
    earring_type: Optional[str] = None
    occasion: Optional[str] = None
    description: str = ""
    confidence: float = 0.0


VISION_PROMPT = """You are an expert Indian jewellery analyst. Analyze this jewellery image and extract:
1. category: ring, necklace, earrings, or bangle
2. style: describe the design motif (e.g., temple-inspired, solitaire, polki, floral cluster, filigree, kundan, meenakari, halo, vintage, modern minimalist)
3. metal: identify the metal color/tone -> gold_24k, gold_22k, gold_18k, gold_14k (default gold_22k if yellow gold)
4. stone_type: none, cz, moissanite, lab_diamond, or natural_diamond (if stones visible, default to natural_diamond)
5. stone_count: estimated number of visible stones
6. earring_type: if earrings, specify stud, jhumka, drop, or hoop
7. occasion: infer likely occasion (engagement, wedding, festival, daily wear, gifting)
8. description: 1-2 sentence description of the piece
9. confidence: 0.0-1.0 how confident you are this is jewellery

If the image is NOT jewellery, set confidence to 0.0 and describe what you see."""


def analyze_inspiration(image_bytes: bytes, mime_type: str = "image/jpeg") -> InspirationResult:
    """Use Gemini Vision to analyze an uploaded jewellery image."""
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    text_part = types.Part.from_text(text=VISION_PROMPT)

    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=InspirationResult,
        temperature=0.2,
    )

    last = None
    for model in [MODEL] + FALLBACKS:
        try:
            resp = client().models.generate_content(
                model=model,
                contents=[types.Content(role="user", parts=[image_part, text_part])],
                config=cfg,
            )
            return InspirationResult.model_validate_json(resp.text)
        except Exception as e:
            last = e
            msg = str(e)
            if not any(k in msg for k in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500")):
                continue
            time.sleep(2)

    raise last


def inspiration_to_spec(result: InspirationResult) -> DesignSpec:
    """Convert an InspirationResult into a DesignSpec for pricing."""
    d = {}
    if result.category in ("ring", "necklace", "earrings", "bangle"):
        d["category"] = result.category
    if result.style:
        d["style"] = result.style
    if result.metal in ("gold_24k", "gold_22k", "gold_18k", "gold_14k"):
        d["metal"] = result.metal
    if result.earring_type in ("stud", "jhumka", "drop", "hoop"):
        d["earring_type"] = result.earring_type

    stone_d = {}
    if result.stone_type in ("none", "cz", "moissanite", "lab_diamond", "natural_diamond"):
        stone_d["type"] = result.stone_type
        if result.stone_type != "none" and not stone_d.get("carat"):
            stone_d["carat"] = 0.3
    if result.stone_count and result.stone_count > 0:
        stone_d["count"] = min(100, result.stone_count)
    if stone_d:
        d["stone"] = Stone(**{**Stone().model_dump(), **stone_d})

    return DesignSpec(**d)


# ──────────────────────────────────────────────────────────
# Merge chat turn into spec
# ──────────────────────────────────────────────────────────

def merge(spec: DesignSpec, t: ChatTurn) -> DesignSpec:
    """Apply extracted fields onto the spec, ignoring invalid values."""
    d = spec.model_dump()
    for f in ("style", "occasion", "notes", "budget_inr", "customer_name"):
        if getattr(t, f) is not None:
            d[f] = getattr(t, f)
    if t.category in ("ring", "necklace", "earrings", "bangle"):
        d["category"] = t.category
    if t.metal in ("gold_24k", "gold_22k", "gold_18k", "gold_14k"):
        d["metal"] = t.metal
    if t.band_width_mm is not None:
        d["band_width_mm"] = min(8, max(1.5, t.band_width_mm))
    if t.ring_size_in is not None:
        d["ring_size_in"] = min(24, max(6, t.ring_size_in))
    if t.earring_type in ("stud", "jhumka", "drop", "hoop"):
        d["earring_type"] = t.earring_type
    if t.necklace_length_in is not None:
        d["necklace_length_in"] = min(30, max(14, t.necklace_length_in))
    if t.bangle_size_in in ("2-2", "2-4", "2-6", "2-8", "2-10"):
        d["bangle_size_in"] = t.bangle_size_in
    if "stone" not in d or not isinstance(d.get("stone"), dict):
        d["stone"] = Stone().model_dump()
    if t.stone_type in ("none", "cz", "moissanite", "lab_diamond", "natural_diamond"):
        d["stone"]["type"] = t.stone_type
        if t.stone_type != "none" and not d["stone"].get("carat"):
            d["stone"]["carat"] = 0.3
    if t.stone_carat is not None and d["stone"].get("type") != "none":
        d["stone"]["carat"] = min(10, max(0.05, t.stone_carat))
    if t.stone_count is not None:
        d["stone"]["count"] = min(100, max(1, t.stone_count))
    return DesignSpec.model_validate(d)
