"""Artisan / Karigar manufacturing specification sheet generator.
Produces formatted job cards for goldsmith workshops with all details
needed to manufacture or quote a custom jewellery piece."""
import time
import hashlib
import urllib.parse
from .models import DesignSpec
from . import pricing

HALLMARK_NAME = {
    "gold_24k": "24K Pure Gold (999)", "gold_22k": "22K BIS Hallmark (916)",
    "gold_18k": "18K BIS Hallmark (750)", "gold_14k": "14K BIS Hallmark (585)",
    "rose_gold": "18K Rose Gold (750)", "platinum": "950 Pure Platinum (950)",
}
METAL_LABEL = {
    "gold_24k": "24 Karat Yellow Gold", "gold_22k": "22 Karat Yellow Gold",
    "gold_18k": "18 Karat Gold", "gold_14k": "14 Karat Gold",
    "rose_gold": "18 Karat Rose Gold", "platinum": "Platinum 950",
}
STONE_LABEL = {
    "none": "No Stone", "cz": "Cubic Zirconia", "moissanite": "Moissanite",
    "lab_diamond": "Lab-Grown Diamond", "natural_diamond": "Natural Diamond",
}
CATEGORY_LABEL = {
    "ring": "Ring", "necklace": "Necklace / Pendant", "earrings": "Earrings (Pair)", "bangle": "Bangle / Kada",
}
SETTING_TYPE = {
    "cz": "Prong / Bezel", "moissanite": "Prong", "lab_diamond": "4-Prong Basket",
    "natural_diamond": "4-Prong Basket",
}


def generate_job_id(spec: DesignSpec) -> str:
    """Generate a deterministic short job ID from spec content."""
    h = hashlib.md5(spec.model_dump_json().encode()).hexdigest()[:6].upper()
    prefix = {"ring": "R", "necklace": "N", "earrings": "E", "bangle": "B"}
    return f"JOB-{prefix.get(spec.category, 'X')}-{h}"


def generate_job_card(spec: DesignSpec) -> dict:
    """Generate a complete karigar job card for manufacturing."""
    p = pricing.price(spec)
    w = p["weight_g"]
    job_id = generate_job_id(spec)

    card = {
        "job_id": job_id,
        "date": time.strftime("%d-%b-%Y"),
        "category": CATEGORY_LABEL.get(spec.category, spec.category),
        "style": spec.style,
        "hallmarking_grade": HALLMARK_NAME.get(spec.metal, "BIS Hallmark"),
        "estimated_gross_weight_g": w,
        "estimated_net_gold_g": round(w * pricing.PURITY.get(spec.metal, 0.75), 2),
        "weight_tolerance": f"±{round(w * 0.05, 2)}g (5%)",
        "customer_name": spec.customer_name or "Walk-in Customer",
        "customer_phone": spec.customer_phone or "—",
        "completion_target_days": "5-7 business days",
        "customer_order": {"occasion": spec.occasion, "budget": spec.budget_inr},
        "karigar_instructions": (
            f"Cast in {HALLMARK_NAME.get(spec.metal, 'BIS Hallmark')} ({spec.metal}). "
            f"Net gold target {round(w * pricing.PURITY.get(spec.metal, 0.75), 2)}g. "
            f"{spec.artisan_notes or 'High polish mirror finish with BIS 916 laser hallmarking inspection.'}"
        ),
        "cost_breakdown": {
            "making": p["making_cost"],
            "gold": p["metal_cost"],
            "stone": p["stone_cost"],
            "gst": p["gst"],
            "total": p["total"]
        },

        # Metal specification
        "metal": {
            "type": METAL_LABEL.get(spec.metal, spec.metal),
            "hallmark": HALLMARK_NAME.get(spec.metal, "BIS Hallmark"),
            "purity": pricing.PURITY.get(spec.metal, 0.75),
            "estimated_gross_weight_g": w,
            "estimated_net_gold_weight_g": round(w * pricing.PURITY.get(spec.metal, 0.75), 2),
            "tolerance_g": round(w * 0.05, 2),  # 5% manufacturing tolerance
        },

        # Stone specification
        "stone": {
            "type": STONE_LABEL[spec.stone.type],
            "carat_per_stone": spec.stone.carat,
            "count": spec.stone.count,
            "total_carat": round(spec.stone.carat * spec.stone.count, 2),
            "setting": SETTING_TYPE.get(spec.stone.type, "N/A"),
            "quality_grade": "VS1-VS2" if spec.stone.type in ("lab_diamond", "natural_diamond") else
                            "AAA" if spec.stone.type == "moissanite" else "Standard",
        },

        # Dimensions
        "dimensions": _get_dimensions(spec),

        # Pricing
        "pricing": {
            "gold_rate_24k_per_g": p["gold_rate_24k"],
            "metal_cost": p["metal_cost"],
            "stone_cost": p["stone_cost"],
            "setting_charges": p["setting_cost"],
            "making_charges": p["making_cost"],
            "gst_3pct": p["gst"],
            "total_estimate_inr": p["total"],
        },

        # Manufacturing notes
        "finish": "High polish with rhodium plating" if spec.metal in ("gold_18k", "gold_14k") else "High polish",
        "artisan_notes": spec.artisan_notes or "Standard manufacturing. Inspect hallmark before delivery.",
        "occasion": spec.occasion or "Not specified",
    }

    if spec.budget_inr:
        card["customer_budget"] = spec.budget_inr
        card["within_budget"] = p["total"] <= spec.budget_inr

    return card


def _get_dimensions(spec: DesignSpec) -> dict:
    """Get category-specific dimensions."""
    if spec.category == "ring":
        return {
            "ring_size_indian": spec.ring_size_in,
            "band_width_mm": spec.band_width_mm,
            "band_thickness_mm": pricing.CFG.thickness_mm,
        }
    elif spec.category == "necklace":
        return {
            "chain_length_inches": spec.necklace_length_in,
            "chain_length_cm": round(spec.necklace_length_in * 2.54, 1),
        }
    elif spec.category == "earrings":
        return {
            "earring_type": spec.earring_type,
            "pair": True,
        }
    elif spec.category == "bangle":
        return {
            "bangle_size_indian": spec.bangle_size_in,
            "inner_diameter_mm": pricing.BANGLE_DIAM.get(spec.bangle_size_in, 57.15),
            "width_mm": spec.band_width_mm,
        }
    return {}


def generate_whatsapp_link(spec: DesignSpec) -> str:
    """Generate a pre-filled WhatsApp message link with the design quote."""
    p = pricing.price(spec)
    job_id = generate_job_id(spec)

    lines = [
        f"*Jewel-AI Design Quote*",
        f"Job Ref: {job_id}",
        f"",
        f"*{CATEGORY_LABEL.get(spec.category, spec.category)}*",
        f"   Style: {spec.style}",
        f"   Metal: {METAL_LABEL.get(spec.metal, spec.metal)}",
    ]

    if spec.stone.type != "none":
        lines.append(f"   Stone: {STONE_LABEL.get(spec.stone.type, spec.stone.type)} ({spec.stone.carat}ct x {spec.stone.count})")

    lines.extend([
        f"",
        f"*Estimated Price: INR {p['total']:,}*",
        f"   (Gold: INR {p['metal_cost']:,} + Stone: INR {p['stone_cost']:,} + Making: INR {p['making_cost']:,} + GST: INR {p['gst']:,})",
    ])

    if spec.budget_inr:
        status = "Within budget" if p["total"] <= spec.budget_inr else f"Over budget by INR {p['total'] - spec.budget_inr:,}"
        lines.append(f"   Budget: INR {spec.budget_inr:,} — {status}")

    lines.extend([
        f"",
        f"Powered by Jewel-AI",
    ])

    msg = "\n".join(lines)
    phone = spec.customer_phone or ""
    phone = phone.replace("+", "").replace(" ", "").replace("-", "")

    if phone:
        return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
    return f"https://wa.me/?text={urllib.parse.quote(msg)}"
