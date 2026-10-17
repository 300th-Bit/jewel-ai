"""Skin tone and undertone color harmony analyzer for jewellery styling.
Uses Gemini Vision to determine customer skin undertone and recommend metal purity & gemstone harmony.
"""
from typing import Literal
from pydantic import BaseModel, Field

try:
    from google import genai
    from google.genai import types
    import os
    API_KEY = os.getenv("GEMINI_API_KEY", "")
except ImportError:
    genai = None
    API_KEY = ""


class UndertoneAnalysis(BaseModel):
    skin_tone: str = Field(description="Fair, Medium, Olive, Tan, or Deep")
    undertone: Literal["warm", "cool", "neutral", "olive"] = Field(description="Skin undertone")
    recommended_metals: list[str] = Field(description="Top recommended metal alloys (e.g. 18k_yellow_gold, rose_gold, platinum)")
    best_gemstones: list[str] = Field(description="Gemstones that enhance natural skin radiance")
    styling_notes: str = Field(description="Professional jewellery stylist commentary")
    contrast_level: str = Field(description="Low, Medium, or High contrast")


def fallback_undertone_analysis() -> UndertoneAnalysis:
    """Default warm-neutral bridal/festive harmony profile."""
    return UndertoneAnalysis(
        skin_tone="Medium / Olive",
        undertone="warm",
        recommended_metals=["gold_22k", "gold_18k", "rose_gold"],
        best_gemstones=["emerald", "natural_diamond", "ruby", "champagne_diamond"],
        styling_notes="Warm golden undertones achieve radiant luminescence when paired with high-karat 22K and 18K yellow gold. Deep Zambian emeralds and warm diamonds provide stunning natural contrast.",
        contrast_level="Medium"
    )


def analyze_skin_undertone(image_bytes: bytes, mime_type: str = "image/jpeg") -> UndertoneAnalysis:
    """Analyze portrait photo using Gemini 2.5 Flash to extract skin undertone & jewellery harmony."""
    if not API_KEY or genai is None:
        return fallback_undertone_analysis()

    client = genai.Client(api_key=API_KEY)
    prompt = """You are an elite haute joaillerie skin tone and color-harmony specialist.
Analyze this customer portrait or hand photo.
Determine:
1. Skin tone (Fair, Light Medium, Medium, Olive, Tan, Deep)
2. Undertone (warm, cool, neutral, or olive)
3. Recommended metals that most flatter this undertone (e.g. gold_22k, gold_18k, rose_gold, platinum, white_gold_14k)
4. Best complementary gemstones (diamonds, emeralds, rubies, sapphires, pearls)
5. Professional styling advice on metal reflection, contrast, and aesthetics.
6. Contrast level (Low, Medium, High)

Return strictly valid JSON conforming to the requested schema.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=UndertoneAnalysis,
                temperature=0.2,
            )
        )
        return UndertoneAnalysis.model_validate_json(response.text)
    except Exception as e:
        print(f"Undertone analysis fallback due to: {e}")
        return fallback_undertone_analysis()
