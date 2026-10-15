"""Deterministic price engine. No AI here: weight x rate + stone + making + GST.
All rates are PLACEHOLDERS for the demo; gold rate should come from a
Search-grounded fetch cached in Firestore (see config/pricing)."""
import math
from dataclasses import dataclass
from .models import DesignSpec

PURITY = {"gold_24k": 1.0, "gold_22k": 0.916, "gold_18k": 0.75, "gold_14k": 0.585}
DENSITY = {"gold_24k": 19.3, "gold_22k": 17.7, "gold_18k": 15.6, "gold_14k": 13.5}  # g/cm3
STONE_PER_CT = {"none": 0, "cz": 1500, "moissanite": 12000,
                "lab_diamond": 40000, "natural_diamond": 150000}  # INR/ct placeholders


@dataclass
class PricingConfig:
    gold_rate_24k_per_g: float = 12000.0   # PLACEHOLDER: update / ground via search
    making_pct: float = 0.12
    gst_pct: float = 0.03                  # verify rules before quoting exact GST in the deck
    thickness_mm: float = 1.2
    setting_per_stone: float = 800.0


CFG = PricingConfig()


def estimate_weight_g(spec: DesignSpec, cfg: PricingConfig = CFG) -> float:
    inner_d = 12.0 + 0.35 * spec.ring_size_in           # approx inner diameter, mm
    circ = math.pi * (inner_d + cfg.thickness_mm)
    vol_cm3 = circ * spec.band_width_mm * cfg.thickness_mm / 1000
    w = vol_cm3 * DENSITY[spec.metal]
    if spec.stone.type != "none":                        # head / prongs
        w += 0.3 + 0.8 * spec.stone.carat * spec.stone.count
    return round(w, 2)


def price(spec: DesignSpec, cfg: PricingConfig = CFG) -> dict:
    w = estimate_weight_g(spec, cfg)
    metal = w * cfg.gold_rate_24k_per_g * PURITY[spec.metal]
    s = spec.stone
    stone = STONE_PER_CT[s.type] * s.carat * s.count * (1 + 0.5 * s.carat)
    setting = cfg.setting_per_stone * s.count if s.type != "none" else 0
    making = metal * cfg.making_pct
    subtotal = metal + stone + setting + making
    gst = subtotal * cfg.gst_pct
    total = round(subtotal + gst)
    b = spec.budget_inr
    return {
        "weight_g": w,
        "metal_cost": round(metal), "stone_cost": round(stone),
        "setting_cost": round(setting), "making_cost": round(making),
        "gst": round(gst), "total": total,
        "budget": b,
        "within_budget": None if b is None else total <= b,
        "over_by": None if b is None else max(0, total - b),
    }


def _levers(spec: DesignSpec):
    out = []
    if spec.metal in ("gold_24k", "gold_22k"):
        out.append(("metal_18k", "Use 18k gold instead of " + spec.metal[5:],
                    spec.model_copy(update={"metal": "gold_18k"})))
    if spec.stone.type == "natural_diamond":
        out.append(("lab_diamond", "Lab-grown diamond instead of natural",
                    spec.model_copy(update={"stone": spec.stone.model_copy(update={"type": "lab_diamond"})})))
    if spec.stone.type in ("natural_diamond", "lab_diamond"):
        out.append(("moissanite", "Moissanite instead of diamond",
                    spec.model_copy(update={"stone": spec.stone.model_copy(update={"type": "moissanite"})})))
    if spec.band_width_mm > 2.0:
        out.append(("slim_band", "Slimmer band (-1 mm)",
                    spec.model_copy(update={"band_width_mm": max(2.0, spec.band_width_mm - 1)})))
    if spec.stone.type != "none" and spec.stone.carat > 0.1:
        out.append(("smaller_stone", "Slightly smaller stone (-0.1 ct)",
                    spec.model_copy(update={"stone": spec.stone.model_copy(
                        update={"carat": round(spec.stone.carat - 0.1, 2)})})))
    return out


def budget_levers(spec: DesignSpec) -> list[dict]:
    base = price(spec)["total"]
    res = []
    for id_, label, new in _levers(spec):
        t = price(new)["total"]
        res.append({"id": id_, "label": label, "saving": base - t, "new_total": t,
                    "meets_budget": spec.budget_inr is not None and t <= spec.budget_inr})
    return sorted(res, key=lambda r: -r["saving"])


def fit_to_budget(spec: DesignSpec) -> tuple[DesignSpec, list[str]]:
    """Greedily apply the biggest saving until the design fits the budget."""
    applied = []
    cur = spec
    for _ in range(6):
        if cur.budget_inr is None or price(cur)["total"] <= cur.budget_inr:
            break
        options = [(price(n)["total"], l, n) for _, l, n in _levers(cur)]
        if not options:
            break
        _, label, cur = min(options, key=lambda o: o[0])
        applied.append(label)
    return cur, applied


def make_variants(spec: DesignSpec) -> list[dict]:
    safe, applied = fit_to_budget(spec)
    stmt = spec.model_copy(update={
        "band_width_mm": min(8, spec.band_width_mm + 1),
        "stone": spec.stone.model_copy(update={
            "carat": round(spec.stone.carat + 0.15, 2) if spec.stone.type != "none" else 0}),
    })
    rows = [("Budget-smart", safe, applied), ("Balanced", spec, []), ("Statement", stmt, [])]
    return [{"label": l, "changes": ch, "spec": s.model_dump(), "price": price(s)} for l, s, ch in rows]
