"""Photorealistic luxury jewellery render pipeline with Flux AI & curated high-resolution studio assets.
Supports multi-category jewellery: rings, necklaces, earrings, and bangles."""
import base64
import hashlib
import time
import urllib.parse
import urllib.request
from .models import DesignSpec

CACHE: dict = {}
METAL = {"gold_24k": "24 karat yellow gold", "gold_22k": "22 karat yellow gold",
         "gold_18k": "18 karat gold", "gold_14k": "14 karat gold"}
STONE = {"cz": "cubic zirconia stones", "moissanite": "moissanite", "lab_diamond": "round brilliant diamond",
         "natural_diamond": "round brilliant diamond", "none": "plain gold without stones"}
STONE_COUNT_LABEL = {1: "a single", 2: "two", 3: "three", 4: "four", 5: "five"}

CURATED_ATELIER_PHOTOS = {
    "ring_solitaire": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80",
    "ring_halo": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=800&q=80",
    "ring_band": "https://images.unsplash.com/photo-1598560917505-59a3ad559071?auto=format&fit=crop&w=800&q=80",
    "necklace_bridal": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80",
    "necklace_delicate": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=800&q=80",
    "earrings_jhumka": "https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&q=80",
    "earrings_stud": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80",
    "bangle_kada": "https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?auto=format&fit=crop&w=800&q=80",
}


def get_curated_image(s: DesignSpec) -> str:
    """Return a high-resolution, instant luxury jewellery photograph matching the spec."""
    cat = s.category
    style = (s.style or "").lower()
    if cat == "necklace":
        if "bridal" in style or "temple" in style or (s.occasion and "wedding" in s.occasion.lower()):
            return CURATED_ATELIER_PHOTOS["necklace_bridal"]
        return CURATED_ATELIER_PHOTOS["necklace_delicate"]
    elif cat == "earrings":
        if "jhumka" in style or (s.earring_type and "jhumka" in s.earring_type):
            return CURATED_ATELIER_PHOTOS["earrings_jhumka"]
        return CURATED_ATELIER_PHOTOS["earrings_stud"]
    elif cat == "bangle":
        return CURATED_ATELIER_PHOTOS["bangle_kada"]
    else:  # ring
        if "halo" in style or "cluster" in style:
            return CURATED_ATELIER_PHOTOS["ring_halo"]
        if "band" in style or s.stone.type == "none":
            return CURATED_ATELIER_PHOTOS["ring_band"]
        return CURATED_ATELIER_PHOTOS["ring_solitaire"]


def build_prompt(s: DesignSpec) -> str:
    metal_desc = METAL.get(s.metal, "22 karat yellow gold")
    stone_desc = ""
    if s.stone.type != "none":
        count_label = STONE_COUNT_LABEL.get(s.stone.count, f"{s.stone.count}")
        stone_desc = f"set with {count_label} {STONE.get(s.stone.type, 'diamond')} of about {s.stone.carat} carat each"
    else:
        stone_desc = "plain metal, no stone"

    if s.category == "ring":
        band = "slim" if s.band_width_mm < 3 else "medium" if s.band_width_mm < 4.5 else "wide"
        return (f"Studio product photograph, front view, of one {metal_desc} ring, {s.style} design, "
                f"{band} band, {stone_desc}, "
                "Indian fine jewellery catalogue, pure white background, macro lens, soft light, sharp detail")

    elif s.category == "necklace":
        return (f"Studio product photograph, flat lay view, of a {metal_desc} necklace, {s.style} design, "
                f"{stone_desc}, "
                f"{s.necklace_length_in} inch length, "
                "Indian fine jewellery catalogue, pure white background, soft professional lighting, sharp detail")

    elif s.category == "earrings":
        return (f"Studio product photograph, of a pair of {metal_desc} {s.earring_type} earrings, "
                f"{s.style} design, {stone_desc}, "
                "Indian fine jewellery catalogue, pure white background, macro lens, soft light, sharp detail")

    elif s.category == "bangle":
        return (f"Studio product photograph, of a {metal_desc} bangle bracelet, {s.style} design, "
                f"{stone_desc}, "
                "Indian fine jewellery catalogue, pure white background, macro lens, soft light, sharp detail")

    return (f"Studio photograph of {metal_desc} {s.category}, {s.style} design, {stone_desc}, "
            "Indian jewellery, white background, sharp detail")


import logging

logger = logging.getLogger("jewel_ai.render")


def render_image(s: DesignSpec) -> str | None:
    """Generate or retrieve a photorealistic jewellery studio render via Flux.
    Returns base64 data URL or None on failure."""
    p = build_prompt(s)
    key = hashlib.md5(p.encode()).hexdigest()
    if key in CACHE:
        logger.info("[Render] Cache hit for %s (%s)", s.category, key[:8])
        return CACHE[key]

    url = (f"https://image.pollinations.ai/prompt/{urllib.parse.quote(p)}"
           f"?width=640&height=640&seed={int(key[:6], 16)}&nologo=true&model=flux")
    
    t0 = time.time()
    logger.info("[Render] Initiating Flux AI render: %s | prompt: %s", s.category, p[:70])
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "jewel-ai-hackathon"})
        with urllib.request.urlopen(req, timeout=12) as r:
            data, ct = r.read(), r.headers.get("Content-Type", "")
        duration = round(time.time() - t0, 2)
        if ct.startswith("image/") and len(data) > 2000:
            out = f"data:{ct};base64," + base64.b64encode(data).decode()
            if len(CACHE) > 50:
                CACHE.clear()
            CACHE[key] = out
            logger.info("[Render] Flux render SUCCESS in %ss (%d bytes)", duration, len(data))
            return out
        else:
            logger.warning("[Render] Received unexpected content type '%s' or small payload (%d bytes)", ct, len(data))
    except Exception as e:
        duration = round(time.time() - t0, 2)
        logger.warning("[Render] Flux render failed/timed out after %ss: %s. Relying on curated studio fallback.", duration, e)

    return None
