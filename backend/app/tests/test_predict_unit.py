from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_predict_timeout_shape():
    r = client.post("/api/v1/predict", json={"log": "Request timed out after 30s", "source": "ci"})
    assert r.status_code == 200
    body = r.json()
    assert body["incident_type"] == "timeout"
    assert "severity" in body
    assert "action" in body
    assert "team" in body
    assert 0.0 <= body["confidence"] <= 1.0

