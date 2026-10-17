"""SQLite storage (free, zero setup). Seeds labelled demo rows so the dashboard is not empty.
Enhanced with multi-category support and demand forecasting."""
import math, os, random, re, sqlite3, time, uuid
from collections import Counter
from statistics import median

DB = os.getenv("DB_PATH", "data/jewel.db")
STYLES = ["temple-inspired minimalist", "classic solitaire", "floral cluster", "vintage polki",
          "halo", "stackable slim band", "kundan set", "modern drop", "temple jhumka"]
OCC = ["Engagement", "Wedding", "Anniversary", "Birthday gift", "Festival gift",
       "Diwali/Dhanteras", "Daily wear", "Akshaya Tritiya"]
CATS = ["ring", "necklace", "earrings", "bangle"]


def conn():
    os.makedirs(os.path.dirname(DB) or ".", exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("""create table if not exists requests(id text primary key, ts real, status text,
        category text default 'ring', occasion text,
        style text, metal text, stone text, carat real, budget int,
        customer_name text, customer_phone text, demo int default 0)""")
    # Migrate old schema: add category column if missing
    try:
        c.execute("select category from requests limit 1")
    except sqlite3.OperationalError:
        c.execute("alter table requests add column category text default 'ring'")
    try:
        c.execute("select customer_name from requests limit 1")
    except sqlite3.OperationalError:
        c.execute("alter table requests add column customer_name text")
        c.execute("alter table requests add column customer_phone text")
    return c


def inr(n) -> str:
    s = str(int(n))
    return s if len(s) <= 3 else re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", s[:-3]) + "," + s[-3:]


def init():
    c = conn()
    if c.execute("select count(*) from requests").fetchone()[0] == 0:
        r, now = random.Random(7), time.time()
        for _ in range(30):
            cat = r.choices(CATS, [5, 3, 3, 2])[0]
            st = r.choices(STYLES, [5, 4, 2, 2, 2, 3, 2, 2, 2])[0]
            stone = r.choices(["lab_diamond", "natural_diamond", "moissanite", "cz", "none"], [5, 3, 2, 2, 1])[0]
            name = r.choice(["Priya", "Arun", "Meera", "Rajesh", "Sunita", "Vikram", "Ananya", "Karthik", None, None])
            c.execute("insert into requests values(?,?,?,?,?,?,?,?,?,?,?,?,1)", (
                uuid.uuid4().hex[:10], now - r.random() * 30 * 86400, "sent" if r.random() < .35 else "designed",
                cat, r.choice(OCC), st,
                r.choices(["gold_22k", "gold_18k", "gold_14k"], [5, 4, 1])[0], stone,
                0 if stone == "none" else r.choice([.2, .3, .5, .7]),
                r.choice([20000, 30000, 40000, 50000, 60000, 80000, 100000, 150000]),
                name, None))
        c.commit()
    c.close()


def save(spec, status: str, rid=None) -> str:
    rid = rid or uuid.uuid4().hex[:10]
    c = conn()
    c.execute("""insert into requests(id,ts,status,category,occasion,style,metal,stone,carat,budget,customer_name,customer_phone,demo)
        values(?,?,?,?,?,?,?,?,?,?,?,?,0)
        on conflict(id) do update set status=case when requests.status='sent' then 'sent' else excluded.status end,
        category=excluded.category, occasion=excluded.occasion, style=excluded.style, metal=excluded.metal,
        stone=excluded.stone, carat=excluded.carat, budget=excluded.budget,
        customer_name=excluded.customer_name, customer_phone=excluded.customer_phone""",
              (rid, time.time(), status, spec.category, spec.occasion or "Other", spec.style, spec.metal,
               spec.stone.type, spec.stone.carat, spec.budget_inr or 0,
               spec.customer_name, spec.customer_phone))
    c.commit(); c.close()
    return rid


def insights() -> dict:
    c = conn()
    rows = [dict(r) for r in c.execute("select * from requests order by ts desc")]
    c.close()
    n, sent = len(rows), [r for r in rows if r["status"] == "sent"]
    top = lambda k, m=5: Counter(r[k] for r in rows if r.get(k)).most_common(m)
    bud = [r["budget"] for r in rows if r["budget"]]
    bins = [("Under ₹30k", 0, 30000), ("₹30k-60k", 30000, 60000), ("₹60k-1L", 60000, 100000), ("Above ₹1L", 100000, 10**9)]
    now = time.time()
    days = []
    for i in range(6, -1, -1):
        lo = now - (i + 1) * 86400
        days.append([time.strftime("%a", time.localtime(now - i * 86400)),
                     sum(1 for r in rows if lo <= r["ts"] < lo + 86400)])

    # Category distribution
    categories = top("category", 4) if any(r.get("category") for r in rows) else []

    sug = None
    if rows:
        ts, tm = top("style", 1)[0][0], None
        same = [r for r in rows if r["style"] == ts]
        tm = Counter(r["metal"] for r in same).most_common(1)[0][0]
        mb = median([r["budget"] for r in same if r["budget"]] or [0])
        sug = (f"Make or stock 3 {ts} pieces in {tm.replace('gold_', '')} gold, priced near ₹{inr(mb)}. "
               f"It is the most requested style ({len(same)} of {n} requests).")

    return {"total": n, "sent": len(sent), "conversion": round(100 * len(sent) / n) if n else 0,
            "median_budget": int(median(bud)) if bud else 0, "demo": sum(r.get("demo", 0) for r in rows),
            "styles": top("style"), "metals": top("metal"), "stones": top("stone"),
            "categories": categories,
            "budgets": [[l, sum(1 for b in bud if lo <= b < hi)] for l, lo, hi in bins],
            "days": days, "suggestion": sug, "recent": rows[:8]}


# ──────────────────────────────────────────────────────────
# Demand Forecasting & Material Planning
# ──────────────────────────────────────────────────────────

SEASON_BOOST = {
    1: 0.8, 2: 0.7, 3: 0.9,     # Jan-Mar: post-wedding lull + Akshaya Tritiya
    4: 1.3, 5: 1.1, 6: 0.8,     # Apr: Akshaya Tritiya peak
    7: 0.7, 8: 0.8, 9: 1.0,     # Monsoon lull
    10: 1.5, 11: 1.8, 12: 1.4,  # Oct-Dec: Diwali/Dhanteras/Wedding season
}


def demand_forecast() -> dict:
    """Generate a 30-day demand forecast based on historical patterns and seasonality."""
    c = conn()
    rows = [dict(r) for r in c.execute("select * from requests order by ts desc")]
    c.close()

    if not rows:
        return {"forecast_days": 30, "predicted_requests": 0, "materials": {},
                "seasonal_factor": 1.0, "segments": []}

    now = time.time()
    month = int(time.strftime("%m"))
    seasonal = SEASON_BOOST.get(month, 1.0)

    # Calculate daily run rate from last 30 days
    last_30 = [r for r in rows if now - r["ts"] < 30 * 86400]
    daily_rate = len(last_30) / 30.0 if last_30 else len(rows) / 90.0
    predicted_requests = round(daily_rate * 30 * seasonal)

    # Material requirements (aggregate from recent patterns)
    metal_counts = Counter(r["metal"] for r in last_30 if r.get("metal"))
    stone_counts = Counter(r["stone"] for r in last_30 if r.get("stone") and r["stone"] != "none")
    cat_counts = Counter(r.get("category", "ring") for r in last_30)
    avg_budget = median([r["budget"] for r in last_30 if r["budget"]] or [50000])

    # Estimate gold requirement (grams) and diamond requirement (carats)
    avg_weight_per_piece = 4.5  # grams average
    total_gold_g = round(predicted_requests * avg_weight_per_piece * seasonal, 1)

    diamond_pieces_pct = sum(v for k, v in stone_counts.items() if "diamond" in k) / max(1, len(last_30))
    avg_carat = median([r["carat"] for r in last_30 if r.get("carat") and r["carat"] > 0] or [0.3])
    total_carats = round(predicted_requests * diamond_pieces_pct * avg_carat * seasonal, 1)

    # Customer segments
    budgets = [r["budget"] for r in last_30 if r["budget"]]
    segments = []
    if budgets:
        low = [b for b in budgets if b < 40000]
        mid = [b for b in budgets if 40000 <= b < 80000]
        high = [b for b in budgets if b >= 80000]
        if low:
            segments.append({"name": "Budget-Conscious", "count": len(low),
                            "avg_budget": round(sum(low) / len(low)), "pct": round(100 * len(low) / len(budgets))})
        if mid:
            segments.append({"name": "Mid-Range Buyers", "count": len(mid),
                            "avg_budget": round(sum(mid) / len(mid)), "pct": round(100 * len(mid) / len(budgets))})
        if high:
            segments.append({"name": "Premium / Bridal", "count": len(high),
                            "avg_budget": round(sum(high) / len(high)), "pct": round(100 * len(high) / len(budgets))})

    # Top categories forecast
    cat_forecast = []
    for cat, cnt in cat_counts.most_common(4):
        ratio = cnt / max(1, len(last_30))
        cat_forecast.append({
            "category": cat, "current_count": cnt,
            "predicted_30d": round(predicted_requests * ratio),
        })

    return {
        "forecast_days": 30,
        "predicted_requests": predicted_requests,
        "daily_rate": round(daily_rate, 1),
        "seasonal_factor": seasonal,
        "current_month": time.strftime("%B"),
        "materials": {
            "gold_22k_grams": round(total_gold_g * 0.6),   # ~60% 22k demand
            "gold_18k_grams": round(total_gold_g * 0.35),  # ~35% 18k demand
            "gold_14k_grams": round(total_gold_g * 0.05),  # ~5% 14k demand
            "diamond_carats": total_carats,
            "moissanite_carats": round(total_carats * 0.3, 1),
        },
        "avg_budget": round(avg_budget),
        "segments": segments,
        "category_forecast": cat_forecast,
        "metals_distribution": dict(metal_counts.most_common(4)),
        "procurement_advice": _procurement_advice(total_gold_g, total_carats, seasonal),
    }


def _procurement_advice(gold_g: float, carats: float, seasonal: float) -> str:
    """Generate human-readable procurement advice."""
    urgency = "high" if seasonal > 1.3 else "moderate" if seasonal > 0.9 else "low"
    lines = []
    if gold_g > 0:
        lines.append(f"Procure approximately {round(gold_g)}g of gold (split 60% 22k / 35% 18k)")
    if carats > 0:
        lines.append(f"Source {round(carats, 1)} carats of diamonds (lab-grown preferred for margins)")
    if urgency == "high":
        lines.append("⚠️ Peak season approaching — order materials NOW to avoid supply delays")
    elif urgency == "low":
        lines.append("💡 Lean season — focus on clearing existing inventory and custom orders")
    return ". ".join(lines) + "." if lines else "Insufficient data for procurement advice."
