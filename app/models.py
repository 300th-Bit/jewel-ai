from typing import Literal, Optional
from pydantic import BaseModel, Field

Metal = Literal["gold_24k", "gold_22k", "gold_18k", "gold_14k"]
StoneType = Literal["none", "cz", "moissanite", "lab_diamond", "natural_diamond"]


class Stone(BaseModel):
    type: StoneType = "none"
    carat: float = Field(0.0, ge=0, le=3)
    count: int = Field(1, ge=0, le=20)


class DesignSpec(BaseModel):
    """Single source of truth: drives BOTH the price and the image prompt."""
    category: Literal["ring"] = "ring"
    style: str = "classic solitaire"
    metal: Metal = "gold_22k"
    band_width_mm: float = Field(3.0, ge=1.5, le=8)
    ring_size_in: int = Field(12, ge=6, le=24)  # Indian ring size
    stone: Stone = Field(default_factory=Stone)
    occasion: Optional[str] = None
    budget_inr: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
