import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_security_headers_present():
    """Verify that OWASP-recommended security headers are injected into HTTP responses."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    headers = resp.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in headers.get("Permissions-Policy", "")

def test_undertone_payload_size_limit():
    """Verify that oversized image uploads (>10MB) are rejected to prevent DoS."""
    # 11MB fake payload
    oversized = b"fake_png_header" + b"0" * (11 * 1024 * 1024)
    resp = client.post(
        "/api/undertone/analyze",
        files={"file": ("large.png", oversized, "image/png")}
    )
    assert resp.status_code == 400
    assert "too large" in resp.json().get("detail", "").lower()

def test_undertone_non_image_mime_rejected():
    """Verify that non-image MIME types are rejected."""
    resp = client.post(
        "/api/undertone/analyze",
        files={"file": ("malicious.exe", b"MZ...", "application/x-msdownload")}
    )
    assert resp.status_code == 400
    assert "image" in resp.json().get("detail", "").lower()

def test_undertone_b64_oversized_rejected():
    """Verify that base64 payloads exceeding 15MB are rejected."""
    huge_b64 = "A" * (16 * 1024 * 1024)
    resp = client.post(
        "/api/undertone/analyze-b64",
        json={"image_b64": huge_b64, "mime_type": "image/jpeg"}
    )
    assert resp.status_code == 400
    assert "too large" in resp.json().get("detail", "").lower()

def test_request_id_pattern_validation():
    """Verify that invalid request IDs with malicious characters are rejected."""
    invalid_ids = ["../../../etc/passwd", "<script>alert(1)</script>", "id with spaces!"]
    for bad_id in invalid_ids:
        resp = client.post("/api/requests", json={
            "id": bad_id,
            "status": "designed",
            "spec": {"category": "ring", "metal": "gold_22k"}
        })
        assert resp.status_code == 422  # Pydantic validation error

def test_bigquery_schema_safe_endpoint():
    """Verify BigQuery schema endpoint returns schema without path traversal."""
    resp = client.get("/api/merchant/bigquery/schema")
    assert resp.status_code == 200
    data = resp.json()
    assert "CREATE SCHEMA IF NOT EXISTS" in data["sql"]
    assert data["dataset"] == "retail_jewel_ai"
