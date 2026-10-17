from typing import Literal, Optional
from pydantic import BaseModel, Field

Metal = Literal["gold_24k", "gold_22k", "gold_18k", "gold_14k", "rose_gold", "platinum"]
StoneType = Literal["none", "cz", "moissanite", "lab_diamond", "natural_diamond"]
Category = Literal["ring", "necklace", "earrings", "bangle"]
EarringType = Literal["stud", "jhumka", "drop", "hoop"]


class Stone(BaseModel):
    type: StoneType = "none"
    carat: float = Field(0.0, ge=0, le=10)
    count: int = Field(1, ge=0, le=100)


class DesignSpec(BaseModel):
    """Single source of truth: drives BOTH the price and the image prompt."""
    category: Category = "ring"
    style: str = Field("classic solitaire", max_length=150)
    metal: Metal = "gold_22k"
    
    # Ring specific
    band_width_mm: float = Field(3.0, ge=1.5, le=8.0)
    ring_size_in: int = Field(12, ge=6, le=24)  # Indian ring size
    
    # Necklace / Pendant specific
    necklace_length_in: float = Field(16.0, ge=14.0, le=30.0)
    
    # Bangle / Bracelet specific
    bangle_size_in: str = Field("2-4")  # Standard Indian sizes: 2-2, 2-4, 2-6, 2-8
    
    # Earring specific
    earring_type: EarringType = "stud"
    
    stone: Stone = Field(default_factory=Stone)
    occasion: Optional[str] = Field(None, max_length=100)
    budget_inr: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)
    
    # Commerce & Karigar metadata
    customer_name: Optional[str] = Field(None, max_length=100)
    customer_phone: Optional[str] = Field(None, max_length=30)
    artisan_notes: Optional[str] = Field(None, max_length=1000)
    matched_inventory_sku: Optional[str] = Field(None, max_length=50)

