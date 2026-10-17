from fastapi.testclient import TestClient
from app.main import app
from app.models import DesignSpec, Stone
from app import pricing, catalog, artisan

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


def test_multi_category_pricing():
    # Necklace
    n = DesignSpec(category="necklace", necklace_length_in=18, metal="gold_22k",
                   stone=Stone(type="lab_diamond", carat=0.5, count=1), budget_inr=150000)
    pn = pricing.price(n)
    assert pn["weight_g"] > 5
    assert pn["hallmark"] == "916"
    assert pn["total"] > 0

    # Earrings
    e = DesignSpec(category="earrings", earring_type="jhumka", metal="gold_18k",
                   stone=Stone(type="moissanite", carat=0.4, count=2), budget_inr=50000)
    pe = pricing.price(e)
    assert pe["weight_g"] >= 4.0
    assert pe["hallmark"] == "750"

    # Bangles
    b = DesignSpec(category="bangle", bangle_size_in="2-6", metal="gold_22k",
                   band_width_mm=4, stone=Stone(type="none", carat=0, count=0), budget_inr=90000)
    pb = pricing.price(b)
    assert pb["weight_g"] > 6.0


def test_catalog_matcher_and_api():
    s = spec(category="ring", metal="gold_22k", style="classic solitaire")
    matches = catalog.find_matches(s)
    assert len(matches) > 0
    assert matches[0]["category"] == "ring"
    assert matches[0]["similarity"] > 0

    # API endpoint
    r = c.post("/api/catalog/match", json=s.model_dump()).json()
    assert "matches" in r
    assert len(r["matches"]) > 0

    # Catalog summary
    summary = c.get("/api/catalog/summary").json()
    assert "total_items" in summary
    assert summary["total_items"] > 0


def test_artisan_job_card_and_whatsapp():
    s = spec(category="necklace", necklace_length_in=20, metal="gold_22k")
    job = artisan.generate_job_card(s)
    assert "JOB-" in job["job_id"]
    assert "916" in job["hallmarking_grade"]
    assert "karigar_instructions" in job

    # API endpoint
    r = c.post("/api/artisan/job-card", json=s.model_dump()).json()
    assert r["job_id"] == job["job_id"]

    # WhatsApp link
    wa = c.post("/api/artisan/whatsapp", json=s.model_dump()).json()
    assert "wa.me" in wa["link"]


def test_demand_forecast_api():
    r = c.get("/api/forecast").json()
    assert "predicted_requests" in r
    assert "materials" in r
    assert r["materials"]["gold_22k_grams"] >= 0
    assert "procurement_advice" in r
