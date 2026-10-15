"""Trend cues via Gemini + Google Search grounding. Falls back to sample cues (labelled) if unavailable."""
import re, time
from google.genai import types

CACHE: dict = {}
FALLBACK = ["Lightweight 18k and 22k daily-wear rings",
            "Lab-grown diamonds in minimalist solitaires",
            "Temple and floral motifs in modern, slim bands",
            "Stackable thin rings for gifting and festivals"]


def get_trends(occasion: str = "", style: str = "") -> dict:
    key = (occasion.lower(), style.lower())
    hit = CACHE.get(key)
    if hit and time.time() < hit[0]:
        return hit[1]
    out, ttl = {"cues": FALLBACK, "source": "fallback"}, 300
    try:
        from . import ai
        q = (f"List 4 current jewellery trends in India for {occasion or 'everyday'} rings"
             f"{', ' + style + ' style' if style else ''}. One short line each (max 12 words), no intro.")
        r = ai.client().models.generate_content(
            model=ai.MODEL, contents=q,
            config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())]))
        lines = [re.sub(r"^\s*(?:[-•*]|\d+[.)])\s*", "", l).strip() for l in (r.text or "").splitlines() if l.strip()]
        lines = [l for l in lines if 8 < len(l) < 140][:4]
        if len(lines) >= 3:
            out, ttl = {"cues": lines, "source": "google_search"}, 21600
    except Exception:
        pass
    CACHE[key] = (time.time() + ttl, out)
    return out
