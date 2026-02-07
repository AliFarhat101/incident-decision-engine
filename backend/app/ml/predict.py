import json
from pathlib import Path
from typing import Optional, Tuple

import joblib

MODEL_PATH = Path("models/incident_clf.joblib")
META_PATH = Path("models/model_meta.json")


_model = None
_meta = None


def load_model() -> Tuple[object, dict]:
    global _model, _meta
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        _model = joblib.load(MODEL_PATH)

    if _meta is None:
        if META_PATH.exists():
            _meta = json.loads(META_PATH.read_text())
        else:
            _meta = {}

    return _model, _meta


def predict_incident_type(log: str) -> Tuple[str, float]:
    """
    Returns: (incident_type, confidence)
    Confidence is best-effort:
      - If model supports predict_proba, use max probability.
      - Else return 0.5.
    """
    model, _ = load_model()

    incident_type = model.predict([log])[0]

    conf = 0.5
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba([log])[0]
        conf = float(max(proba))

    return str(incident_type), conf
import json
from pathlib import Path
from typing import Optional, Tuple

import joblib

MODEL_PATH = Path("models/incident_clf.joblib")
META_PATH = Path("models/model_meta.json")


_model = None
_meta = None


def load_model() -> Tuple[object, dict]:
    global _model, _meta
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        _model = joblib.load(MODEL_PATH)

    if _meta is None:
        if META_PATH.exists():
            _meta = json.loads(META_PATH.read_text())
        else:
            _meta = {}

    return _model, _meta


def predict_incident_type(log: str) -> Tuple[str, float]:
    """
    Returns: (incident_type, confidence)
    Confidence is best-effort:
      - If model supports predict_proba, use max probability.
      - Else return 0.5.
    """
    model, _ = load_model()

    incident_type = model.predict([log])[0]

    conf = 0.5
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba([log])[0]
        conf = float(max(proba))

    return str(incident_type), conf

