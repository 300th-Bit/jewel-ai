import time
from fastapi.testclient import TestClient
from app import store, render
from app.main import app
from app.models import DesignSpec

c = TestClient(app)


def test_seed_save_insights(tmp_path):
    store.DB = str(tmp_path / "t.db")
    store.init()
    assert store.insights()["total"] == 30
    rid = store.save(DesignSpec(occasion="Wedding", budget_inr=50000), "designed")
    store.save(DesignSpec(occasion="Wedding", budget_inr=50000), "sent", rid)
    store.save(DesignSpec(occasion="Wedding", budget_inr=50000), "designed", rid)  # must not downgrade
    i = store.insights()
    assert i["total"] == 31 and i["recent"][0]["status"] == "sent" and i["suggestion"]
    assert store.inr(1234567) == "12,34,567"


def test_api_and_render_fallback(tmp_path, monkeypatch):
    store.DB = str(tmp_path / "t2.db"); store.init()
    r = c.post("/api/requests", json={"status": "designed", "spec": DesignSpec().model_dump()}).json()
    assert r["id"] and c.get("/api/insights").json()["total"] == 31
    monkeypatch.setattr(time, "sleep", lambda x: None)
    monkeypatch.setattr(render.urllib.request, "urlopen", lambda *a, **k: (_ for _ in ()).throw(OSError("offline")))
    assert c.post("/api/render", json=DesignSpec().model_dump()).json()["image"] is None
    assert "ring" in render.build_prompt(DesignSpec()).lower()
