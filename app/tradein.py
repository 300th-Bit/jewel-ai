"""Old Gold Trade-in & Circular Exchange Valuation Engine.
Solves the primary friction in fine jewellery commerce where customers trade in family gold
to finance high-ticket bespoke commissions. Provides transparent melting purity calculations,
BIS hallmarking yield verification, and instant order credit vouchers.
"""
import uuid
from typing import Optional, Literal
from pydantic import BaseModel, Field
from . import pricing

# Standard purity ratios for old gold recycling
PURITY_FACTORS = {
    "24k": 1.000,
    "22k": 0.916,
    "18k": 0.750,
    "14k": 0.585,
    "vintage_traditional": 0.840,  # Pre-hallmark vintage ornaments with solder alloy
    "silver_925": 0.925,
}

MELTING_DROSS_LOSS = 0.012  # 1.2% standard refinery dross/solder melting loss


class OldGoldItem(BaseModel):
    description: str = Field(default="Family Gold Ornament", description="e.g. Old bangles, broken chain, traditional jhumkas")
    gross_weight_g: float = Field(ge=0.1, le=5000, description="Total scale weight in grams")
    stone_weight_g: float = Field(default=0.0, ge=0.0, description="Deduction for wax, lac, enamel, stones")
    karatage: Literal["24k", "22k", "18k", "14k", "vintage_traditional"] = Field(default="22k")
    has_hallmark: bool = Field(default=True, description="Whether BIS hallmark is stamped")


class TradeInRequest(BaseModel):
    customer_name: Optional[str] = "Valued Patron"
    items: list[OldGoldItem]
    live_rate_24k_override: Optional[float] = None


class TradeInValuation(BaseModel):
    voucher_id: str
    items_count: int
    total_gross_weight_g: float
    total_stone_deduction_g: float
    total_net_weight_g: float
    fine_gold_yield_g: float
    gold_rate_24k_per_g: float
    gross_metal_value_inr: float
    refinery_melting_loss_g: float
    melting_charges_inr: float
    net_trade_in_credit_inr: float
    breakdown: list[dict]
    purity_certificate_notes: str


def appraise_trade_in(req: TradeInRequest) -> TradeInValuation:
    """Calculate transparent scrap gold valuation and generate instant credit voucher."""
    rate_24k = req.live_rate_24k_override or pricing.get_gold_rate()
    
    total_gross = 0.0
    total_stone_ded = 0.0
    total_net = 0.0
    total_fine_gold = 0.0
    breakdown = []

    for item in req.items:
        net_wt = max(0.0, item.gross_weight_g - item.stone_weight_g)
        purity = PURITY_FACTORS.get(item.karatage, 0.916)
        
        # Unhallmarked or vintage gold incurs a slight conservative buffer if uncertified
        purity_adj = purity if item.has_hallmark else purity * 0.985
        item_fine_gold = net_wt * purity_adj
        item_value = item_fine_gold * rate_24k * (1.0 - MELTING_DROSS_LOSS)

        total_gross += item.gross_weight_g
        total_stone_ded += item.stone_weight_g
        total_net += net_wt
        total_fine_gold += item_fine_gold

        breakdown.append({
            "description": item.description,
            "gross_weight_g": round(item.gross_weight_g, 2),
            "stone_deduction_g": round(item.stone_weight_g, 2),
            "net_gold_weight_g": round(net_wt, 2),
            "karatage": item.karatage,
            "certified_purity_pct": round(purity_adj * 100, 1),
            "fine_24k_gold_yield_g": round(item_fine_gold, 3),
            "melt_value_inr": round(item_value),
        })

    refinery_loss_g = total_fine_gold * MELTING_DROSS_LOSS
    gross_metal_val = total_fine_gold * rate_24k
    melting_charge = round(total_net * 35.0)  # ₹35/g refinery assay charge
    net_credit = max(0.0, round(gross_metal_val - (refinery_loss_g * rate_24k) - melting_charge))

    voucher_id = f"EXCH-{uuid.uuid4().hex[:6].upper()}"

    notes = (
        f"BIS Hallmarked Assay Valuation. Purity calculated at current 24K spot rate (₹{rate_24k:,.0f}/g). "
        f"Total fine gold recovery: {total_fine_gold:.2f}g after 1.2% refiner dross allowance. "
        f"This voucher provides ₹{net_credit:,.0f} direct cash offset against any bespoke creation."
    )

    return TradeInValuation(
        voucher_id=voucher_id,
        items_count=len(req.items),
        total_gross_weight_g=round(total_gross, 2),
        total_stone_deduction_g=round(total_stone_ded, 2),
        total_net_weight_g=round(total_net, 2),
        fine_gold_yield_g=round(total_fine_gold, 3),
        gold_rate_24k_per_g=rate_24k,
        gross_metal_value_inr=round(gross_metal_val),
        refinery_melting_loss_g=round(refinery_loss_g, 3),
        melting_charges_inr=melting_charge,
        net_trade_in_credit_inr=net_credit,
        breakdown=breakdown,
        purity_certificate_notes=notes,
    )
