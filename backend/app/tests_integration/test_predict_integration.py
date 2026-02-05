from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_predict_db_error_integration():
    r = client.post("/api/v1/predict", json={"log": "psql: connection refused", "source": "backend"})
    assert r.status_code == 200
    body = r.json()
    assert body["incident_type"] == "db_error"
    assert body["severity"] in ["low", "medium", "high", "critical"]
    assert isinstance(body["action"], str) and len(body["action"]) > 5

