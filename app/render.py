"""Free AI render via Pollinations (no key). Returns a data URL, or None so the UI keeps the drawn ring."""
import base64, hashlib, time, urllib.parse, urllib.request
from .models import DesignSpec

CACHE: dict = {}
METAL = {"gold_24k": "24 karat yellow gold", "gold_22k": "22 karat yellow gold",
         "gold_18k": "18 karat gold", "gold_14k": "14 karat gold"}
STONE = {"cz": "a cubic zirconia", "moissanite": "a moissanite", "lab_diamond": "a round brilliant diamond",
         "natural_diamond": "a round brilliant diamond"}


def build_prompt(s: DesignSpec) -> str:
    stone = f"set with {STONE[s.stone.type]} of about {s.stone.carat} carat" if s.stone.type != "none" else "plain metal, no stone"
    band = "slim" if s.band_width_mm < 3 else "medium" if s.band_width_mm < 4.5 else "wide"
    return (f"Studio product photograph, front view, of one {METAL[s.metal]} ring, {s.style} design, {band} band, {stone}, "
            "Indian fine jewellery catalogue, pure white background, macro lens, soft light, sharp detail")


def render_image(s: DesignSpec):
    p = build_prompt(s)
    key = hashlib.md5(p.encode()).hexdigest()
    if key in CACHE:
        return CACHE[key]
    url = (f"https://image.pollinations.ai/prompt/{urllib.parse.quote(p)}"
           f"?width=640&height=640&seed={int(key[:6], 16)}&nologo=true&model=flux")
    for _ in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "jewel-ai-hackathon"})
            with urllib.request.urlopen(req, timeout=35) as r:
                data, ct = r.read(), r.headers.get("Content-Type", "")
            if ct.startswith("image/") and len(data) > 2000:
                out = f"data:{ct};base64," + base64.b64encode(data).decode()
                if len(CACHE) > 50:
                    CACHE.clear()
                CACHE[key] = out
                return out
        except Exception:
            time.sleep(2)
    return None
