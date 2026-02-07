from fastapi.testclient import TestClient
from backend.app.main import app
import backend.app.ml.predict as ml_predict

client = TestClient(app)

def test_fallback_when_model_missing(monkeypatch):
    # Force the ML loader to behave as if the model file is missing
    monkeypatch.setattr(ml_predict, "MODEL_PATH", ml_predict.Path("models/__definitely_missing__.joblib"))
    # Also reset cached model to ensure it tries to load
    monkeypatch.setattr(ml_predict, "_model", None)
    monkeypatch.setattr(ml_predict, "_meta", None)

    r = client.post("/api/v1/predict", json={"log": "psql: connection refused", "source": "backend"})
    assert r.status_code == 200
    body = r.json()

    # If ML is missing, we must still return a valid decision (rule-based fallback)
    for k in ["incident_type", "severity", "action", "team", "confidence"]:
        assert k in body
