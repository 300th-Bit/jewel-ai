from fastapi.testclient import TestClient
from app.main import app
from app.models import DesignSpec, Stone
from app import undertone, tradein, merchant, certification

c = TestClient(app)


def test_undertone_analysis_fallback_and_api():
    res = undertone.fallback_undertone_analysis()
    assert res.undertone in ["warm", "cool", "neutral", "olive"]
    assert len(res.recommended_metals) > 0
    assert len(res.best_gemstones) > 0

    # API Base64 endpoint
    payload = {"image_b64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="}
    r = c.post("/api/undertone/analyze-b64", json=payload).json()
    assert "undertone" in r
    assert "recommended_metals" in r


def test_old_gold_trade_in_appraisal():
    req = tradein.TradeInRequest(
        items=[
            tradein.OldGoldItem(
                description="Vintage 22K Bangles",
                gross_weight_g=25.0,
                stone_weight_g=1.0,
                karatage="22k",
                has_hallmark=True
            ),
            tradein.OldGoldItem(
                description="Broken 18K Italian Chain",
                gross_weight_g=10.0,
                stone_weight_g=0.0,
                karatage="18k",
                has_hallmark=True
            )
        ]
    )
    val = tradein.appraise_trade_in(req)
    assert val.items_count == 2
    assert val.total_gross_weight_g == 35.0
    assert val.fine_gold_yield_g > 25.0
    assert val.net_trade_in_credit_inr > 100000
    assert "EXCH-" in val.voucher_id

    # Test via API endpoint
    r = c.post("/api/tradein/appraise", json=req.model_dump()).json()
    assert "EXCH-" in r["voucher_id"]
    assert r["net_trade_in_credit_inr"] == val.net_trade_in_credit_inr
    assert r["fine_gold_yield_g"] == val.fine_gold_yield_g


def test_merchant_demand_intelligence():
    intel = merchant.get_demand_intelligence()
    assert len(intel["forecast_timeline"]) >= 3
    assert intel["total_annual_bullion_target_kg"] > 5.0

    r = c.get("/api/merchant/demand").json()
    assert "forecast_timeline" in r
    assert "category_velocity" in r


def test_bullion_volatility_stress_test():
    req = merchant.StressTestRequest(
        inventory_gold_grams=1000.0,
        open_unhedged_orders_grams=250.0,
        price_shift_pct=10.0
    )
    res = merchant.run_bullion_stress_test(req)
    assert res["inventory_valuation_delta_inr"] > 0  # inventory gains value
    assert res["unhedged_order_margin_impact_inr"] < 0  # unhedged orders lose margin
    assert "MCX" in res["hedge_strategy"] or "bullion" in res["hedge_strategy"].lower()

    # API endpoint
    r = c.post("/api/merchant/stress-test", json=req.model_dump()).json()
    assert r["simulated_gold_rate_24k"] > r["base_gold_rate_24k"]


def test_dead_stock_remounting():
    ds = merchant.get_dead_stock_remount_opportunities()
    assert ds["aged_stock_items_count"] > 0
    assert ds["total_locked_capital_inr"] > 100000

    r = c.get("/api/merchant/dead-stock").json()
    assert len(r["items"]) > 0


def test_merchant_copilot():
    req = {"query": "How should I hedge my gold risk before Diwali?"}
    r = c.post("/api/merchant/copilot", json=req).json()
    assert "answer" in r
    assert len(r["answer"]) > 10


def test_digital_certificate_and_huid():
    spec = DesignSpec(
        category="ring",
        metal="gold_18k",
        band_width_mm=3,
        stone=Stone(type="lab_diamond", carat=1.2, count=1),
        budget_inr=95000
    )
    cert = certification.issue_certificate(spec, patron_name="Rohan Mehta")
    assert len(cert.huid_number) == 6
    assert "GIA-BIS-" in cert.certificate_id
    assert "750" in cert.hallmark_grade
    assert cert.gross_weight_g > 3.0

    # API endpoint
    r = c.post("/api/certificate/generate", json={"spec": spec.model_dump(), "patron_name": "Rohan Mehta"}).json()
    assert len(r["huid_number"]) == 6
    assert "verification_url" in r
