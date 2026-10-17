"""Store inventory catalog and similarity matcher.
Provides a realistic demo catalog of ready-to-ship items and matches
customer DesignSpecs against them for instant recommendations."""
import random
from .models import DesignSpec, Stone

# ── Demo catalog: realistic Indian jewellery store inventory ──────────

CATALOG = [
    {"sku": "R-SOL-22-001", "category": "ring", "style": "classic solitaire", "metal": "gold_22k",
     "stone": {"type": "lab_diamond", "carat": 0.3, "count": 1}, "band_width_mm": 2.5,
     "price_inr": 52000, "in_stock": 3, "description": "Elegant 22k solitaire with lab-grown diamond, daily wear"},
    {"sku": "R-TMP-22-002", "category": "ring", "style": "temple-inspired minimalist", "metal": "gold_22k",
     "stone": {"type": "none", "carat": 0, "count": 0}, "band_width_mm": 4,
     "price_inr": 28000, "in_stock": 5, "description": "Traditional temple motif band in 22k gold"},
    {"sku": "R-HAL-18-003", "category": "ring", "style": "halo cluster", "metal": "gold_18k",
     "stone": {"type": "natural_diamond", "carat": 0.5, "count": 7}, "band_width_mm": 3,
     "price_inr": 95000, "in_stock": 2, "description": "Stunning 18k halo ring with natural diamonds"},
    {"sku": "R-FLO-22-004", "category": "ring", "style": "floral cluster", "metal": "gold_22k",
     "stone": {"type": "cz", "carat": 0.15, "count": 12}, "band_width_mm": 5,
     "price_inr": 38000, "in_stock": 4, "description": "Wide floral band with CZ accents"},
    {"sku": "R-SLM-18-005", "category": "ring", "style": "stackable slim band", "metal": "gold_18k",
     "stone": {"type": "moissanite", "carat": 0.2, "count": 3}, "band_width_mm": 1.8,
     "price_inr": 22000, "in_stock": 8, "description": "Delicate stackable band with moissanite"},

    {"sku": "N-CHN-22-001", "category": "necklace", "style": "minimalist pendant", "metal": "gold_22k",
     "stone": {"type": "lab_diamond", "carat": 0.25, "count": 1}, "band_width_mm": 3,
     "price_inr": 45000, "in_stock": 3, "description": "Simple gold chain with solitaire pendant"},
    {"sku": "N-TMP-22-002", "category": "necklace", "style": "temple choker", "metal": "gold_22k",
     "stone": {"type": "none", "carat": 0, "count": 0}, "band_width_mm": 3,
     "price_inr": 185000, "in_stock": 1, "description": "Heavy bridal temple choker necklace"},
    {"sku": "N-KDN-22-003", "category": "necklace", "style": "kundan set", "metal": "gold_22k",
     "stone": {"type": "cz", "carat": 0.3, "count": 24}, "band_width_mm": 3,
     "price_inr": 125000, "in_stock": 2, "description": "Traditional kundan necklace with polki-style stones"},

    {"sku": "E-STD-22-001", "category": "earrings", "style": "classic solitaire stud", "metal": "gold_22k",
     "stone": {"type": "lab_diamond", "carat": 0.25, "count": 2}, "band_width_mm": 3,
     "price_inr": 32000, "in_stock": 6, "description": "Everyday wear solitaire studs"},
    {"sku": "E-JHM-22-002", "category": "earrings", "style": "temple jhumka", "metal": "gold_22k",
     "stone": {"type": "none", "carat": 0, "count": 0}, "band_width_mm": 3,
     "price_inr": 55000, "in_stock": 4, "description": "Traditional gold jhumka earrings"},
    {"sku": "E-DRP-18-003", "category": "earrings", "style": "modern drop", "metal": "gold_18k",
     "stone": {"type": "moissanite", "carat": 0.3, "count": 2}, "band_width_mm": 3,
     "price_inr": 28000, "in_stock": 3, "description": "Contemporary drop earrings with moissanite"},

    {"sku": "B-PLN-22-001", "category": "bangle", "style": "plain polished", "metal": "gold_22k",
     "stone": {"type": "none", "carat": 0, "count": 0}, "band_width_mm": 4,
     "price_inr": 65000, "in_stock": 6, "description": "Classic 22k gold polished bangle"},
    {"sku": "B-KDA-22-002", "category": "bangle", "style": "temple kada", "metal": "gold_22k",
     "stone": {"type": "none", "carat": 0, "count": 0}, "band_width_mm": 6,
     "price_inr": 95000, "in_stock": 3, "description": "Heavy temple-style kada bangle"},
    {"sku": "B-DIA-18-003", "category": "bangle", "style": "diamond tennis", "metal": "gold_18k",
     "stone": {"type": "lab_diamond", "carat": 0.05, "count": 30}, "band_width_mm": 3,
     "price_inr": 120000, "in_stock": 2, "description": "Elegant diamond tennis bangle"},
]


def _similarity(spec: DesignSpec, item: dict) -> float:
    """Score 0-100: how well an inventory item matches a customer's design spec."""
    score = 0.0

    # Category match is mandatory
    if spec.category != item["category"]:
        return 0.0
    score += 25

    # Style similarity (keyword overlap)
    spec_words = set(spec.style.lower().split())
    item_words = set(item["style"].lower().split())
    overlap = len(spec_words & item_words) / max(1, len(spec_words | item_words))
    score += 20 * overlap

    # Metal match
    if spec.metal == item["metal"]:
        score += 15
    elif spec.metal.startswith("gold") and item["metal"].startswith("gold"):
        score += 5

    # Stone type match
    spec_stone = spec.stone.type
    item_stone = item["stone"]["type"]
    if spec_stone == item_stone:
        score += 15
    elif spec_stone != "none" and item_stone != "none":
        score += 5

    # Budget proximity (within 30%)
    if spec.budget_inr and item["price_inr"]:
        ratio = item["price_inr"] / max(1, spec.budget_inr)
        if 0.7 <= ratio <= 1.3:
            score += 15 * (1 - abs(1 - ratio) / 0.3)

    # Availability bonus
    if item["in_stock"] >= 3:
        score += 10
    elif item["in_stock"] >= 1:
        score += 5

    return round(min(100, score), 1)


def find_matches(spec: DesignSpec, top_k: int = 3) -> list[dict]:
    """Find the top-k inventory items that best match the customer's design spec."""
    scored = []
    for item in CATALOG:
        s = _similarity(spec, item)
        if s > 20:
            scored.append({
                "sku": item["sku"],
                "title": item["description"],
                "description": item["description"],
                "style": item["style"],
                "metal": item["metal"],
                "stone": item["stone"],
                "price_inr": item["price_inr"],
                "in_stock": item["in_stock"],
                "stock_qty": item["in_stock"],
                "weight_g": item.get("weight_g", 4.5),
                "match_score": s,
                "similarity": round(s / 100.0, 2),
                "category": item["category"],
            })
    scored.sort(key=lambda x: -x["match_score"])
    return scored[:top_k]


def catalog_summary() -> dict:
    """Return a summary of the current store catalog for the dashboard."""
    cats = {}
    total_value = 0
    for item in CATALOG:
        cat = item["category"]
        if cat not in cats:
            cats[cat] = {"count": 0, "value": 0, "items": 0}
        cats[cat]["count"] += item["in_stock"]
        cats[cat]["value"] += item["price_inr"] * item["in_stock"]
        cats[cat]["items"] += 1
        total_value += item["price_inr"] * item["in_stock"]
    return {
        "total_skus": len(CATALOG),
        "total_items": len(CATALOG),
        "total_pieces": sum(c["count"] for c in cats.values()),
        "total_value_inr": total_value,
        "by_category": cats,
    }
