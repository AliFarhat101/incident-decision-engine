from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_predict_response_contract_unit():
    r = client.post("/api/v1/predict", json={"log": "psql: connection refused", "source": "backend"})
    assert r.status_code == 200
    body = r.json()

    # Contract: required keys
    for k in ["incident_type", "severity", "action", "team", "confidence"]:
        assert k in body

    # Types / bounds
    assert isinstance(body["incident_type"], str) and body["incident_type"]
    assert isinstance(body["severity"], str) and body["severity"]
    assert isinstance(body["team"], str) and body["team"]
    assert isinstance(body["action"], str) and body["action"]
    assert isinstance(body["confidence"], (int, float))
    assert 0.0 <= float(body["confidence"]) <= 1.0
