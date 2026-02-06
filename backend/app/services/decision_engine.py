from backend.app.schemas.incident import PredictResponse
from backend.app.services.decision_rules import rule_based_decision
from backend.app.ml.predict import predict_incident_type


def decision_from_incident_type(incident_type: str, confidence: float) -> PredictResponse:
    # Deterministic mapping from incident_type -> severity/action/team
    if incident_type == "timeout":
        return PredictResponse(
            incident_type="timeout",
            severity="high",
            action="Retry request; check upstream latency; inspect timeouts.",
            team="devops",
            confidence=confidence,
        )

    if incident_type == "db_error":
        return PredictResponse(
            incident_type="db_error",
            severity="critical",
            action="Check DB/storage connectivity; inspect node health; verify IO and network.",
            team="data",
            confidence=confidence,
        )

    if incident_type == "auth":
        return PredictResponse(
            incident_type="auth",
            severity="high",
            action="Verify tokens/keys; check IAM/permissions; rotate credentials if needed.",
            team="security",
            confidence=confidence,
        )

    if incident_type == "config":
        return PredictResponse(
            incident_type="config",
            severity="medium",
            action="Validate configuration; compare with last known good; redeploy.",
            team="platform",
            confidence=confidence,
        )

    return PredictResponse(
        incident_type="unknown",
        severity="low",
        action="Collect more context; escalate if recurring.",
        team="backend",
        confidence=confidence,
    )


def decide(log: str) -> PredictResponse:
    """
    Prefer ML model when available; fall back to rules when model is missing or fails.
    """
    try:
        incident_type, conf = predict_incident_type(log)
        return decision_from_incident_type(incident_type, conf)
    except Exception:
        # Safe fallback (no downtime)
        return rule_based_decision(log)

