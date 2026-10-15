from fastapi.testclient import TestClient
from app.main import app
from app.models import DesignSpec, Stone
from app import pricing

c = TestClient(app)


def spec(**kw):
    base = dict(metal="gold_22k", band_width_mm=3, ring_size_in=12,
                stone=Stone(type="lab_diamond", carat=0.3, count=1), budget_inr=60000)
    base.update(kw)
    return DesignSpec(**base)


def test_total_is_sum_of_parts():
    p = pricing.price(spec())
    assert abs(p["total"] - (p["metal_cost"] + p["stone_cost"] + p["setting_cost"]
                             + p["making_cost"] + p["gst"])) <= 2
    assert 2 < p["weight_g"] < 8


def test_wider_band_costs_more():
    assert pricing.price(spec(band_width_mm=5))["total"] > pricing.price(spec())["total"]


def test_fit_to_budget_reduces_price():
    s = spec(stone=Stone(type="natural_diamond", carat=0.5, count=1), budget_inr=60000)
    new, applied = pricing.fit_to_budget(s)
    assert applied and pricing.price(new)["total"] < pricing.price(s)["total"]


def test_variants_ordering_and_api():
    r = c.post("/api/variants", json=spec().model_dump()).json()["variants"]
    totals = [v["price"]["total"] for v in r]
    assert totals[0] <= totals[1] <= totals[2]
    r2 = c.post("/api/price", json=spec().model_dump()).json()
    assert "suggestions" in r2 and c.get("/api/health").json()["ok"]
