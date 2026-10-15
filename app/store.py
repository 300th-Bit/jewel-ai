"""SQLite storage (free, zero setup). Seeds labelled demo rows so the dashboard is not empty."""
import os, random, re, sqlite3, time, uuid
from collections import Counter
from statistics import median

DB = os.getenv("DB_PATH", "data/jewel.db")
STYLES = ["temple-inspired minimalist", "classic solitaire", "floral cluster", "vintage polki", "halo", "stackable slim band"]
OCC = ["Engagement", "Wedding", "Anniversary", "Birthday gift", "Festival gift"]


def conn():
    os.makedirs(os.path.dirname(DB) or ".", exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("""create table if not exists requests(id text primary key, ts real, status text, occasion text,
        style text, metal text, stone text, carat real, budget int, demo int default 0)""")
    return c


def inr(n) -> str:
    s = str(int(n))
    return s if len(s) <= 3 else re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", s[:-3]) + "," + s[-3:]


def init():
    c = conn()
    if c.execute("select count(*) from requests").fetchone()[0] == 0:
        r, now = random.Random(7), time.time()
        for _ in range(30):
            st = r.choices(STYLES, [5, 4, 2, 2, 2, 3])[0]
            stone = r.choices(["lab_diamond", "natural_diamond", "moissanite", "cz", "none"], [5, 3, 2, 2, 1])[0]
            c.execute("insert into requests values(?,?,?,?,?,?,?,?,?,1)", (
                uuid.uuid4().hex[:10], now - r.random() * 30 * 86400, "sent" if r.random() < .35 else "designed",
                r.choice(OCC), st, r.choices(["gold_22k", "gold_18k", "gold_14k"], [5, 4, 1])[0], stone,
                0 if stone == "none" else r.choice([.2, .3, .5, .7]),
                r.choice([20000, 30000, 40000, 50000, 60000, 80000, 100000, 150000])))
        c.commit()
    c.close()


def save(spec, status: str, rid=None) -> str:
    rid = rid or uuid.uuid4().hex[:10]
    c = conn()
    c.execute("""insert into requests(id,ts,status,occasion,style,metal,stone,carat,budget,demo) values(?,?,?,?,?,?,?,?,?,0)
        on conflict(id) do update set status=case when requests.status='sent' then 'sent' else excluded.status end,
        occasion=excluded.occasion, style=excluded.style, metal=excluded.metal, stone=excluded.stone,
        carat=excluded.carat, budget=excluded.budget""",
              (rid, time.time(), status, spec.occasion or "Other", spec.style, spec.metal,
               spec.stone.type, spec.stone.carat, spec.budget_inr or 0))
    c.commit(); c.close()
    return rid


def insights() -> dict:
    c = conn()
    rows = [dict(r) for r in c.execute("select * from requests order by ts desc")]
    c.close()
    n, sent = len(rows), [r for r in rows if r["status"] == "sent"]
    top = lambda k, m=5: Counter(r[k] for r in rows if r[k]).most_common(m)
    bud = [r["budget"] for r in rows if r["budget"]]
    bins = [("Under ₹30k", 0, 30000), ("₹30k-60k", 30000, 60000), ("₹60k-1L", 60000, 100000), ("Above ₹1L", 100000, 10**9)]
    now = time.time()
    days = []
    for i in range(6, -1, -1):
        lo = now - (i + 1) * 86400
        days.append([time.strftime("%a", time.localtime(now - i * 86400)),
                     sum(1 for r in rows if lo <= r["ts"] < lo + 86400)])
    sug = None
    if rows:
        ts, tm = top("style", 1)[0][0], None
        same = [r for r in rows if r["style"] == ts]
        tm = Counter(r["metal"] for r in same).most_common(1)[0][0]
        mb = median([r["budget"] for r in same if r["budget"]] or [0])
        sug = (f"Make or stock 3 {ts} rings in {tm.replace('gold_', '')} gold, priced near ₹{inr(mb)}. "
               f"It is the most requested style ({len(same)} of {n} requests).")
    return {"total": n, "sent": len(sent), "conversion": round(100 * len(sent) / n) if n else 0,
            "median_budget": int(median(bud)) if bud else 0, "demo": sum(r["demo"] for r in rows),
            "styles": top("style"), "metals": top("metal"), "stones": top("stone"),
            "budgets": [[l, sum(1 for b in bud if lo <= b < hi)] for l, lo, hi in bins],
            "days": days, "suggestion": sug, "recent": rows[:8]}
