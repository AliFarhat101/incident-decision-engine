import re
from backend.app.schemas.incident import PredictResponse


def rule_based_decision(log: str) -> PredictResponse:
    text = log.lower()

    if "timeout" in text or "timed out" in text:
        return PredictResponse(
            incident_type="timeout",
            severity="high",
            action="Retry request; check upstream latency; inspect timeouts.",
            team="devops",
            confidence=0.75,
        )

    if any(k in text for k in ["connection refused", "sql", "database", "psql", "mysql"]):
        return PredictResponse(
            incident_type="db_error",
            severity="critical",
            action="Check DB connectivity; verify credentials; inspect DB health.",
            team="data",
            confidence=0.80,
        )

    if re.search(r"\b(unauthorized|forbidden|permission denied)\b", text):
        return PredictResponse(
            incident_type="auth",
            severity="high",
            action="Verify tokens/keys; check IAM/role permissions; rotate if needed.",
            team="security",
            confidence=0.70,
        )

    if any(k in text for k in ["env", "config", "missing key", "invalid config"]):
        return PredictResponse(
            incident_type="config",
            severity="medium",
            action="Validate configuration; compare with last known good; redeploy.",
            team="platform",
            confidence=0.65,
        )

    return PredictResponse(
        incident_type="unknown",
        severity="low",
        action="Collect more context; escalate if recurring.",
        team="backend",
        confidence=0.40,
    )

