from pydantic import BaseModel, Field
from typing import Literal, Optional


IncidentType = Literal["db_error", "timeout", "config", "auth", "unknown"]
Severity = Literal["low", "medium", "high", "critical"]


class PredictRequest(BaseModel):
    log: str = Field(..., min_length=5, description="Raw log line or error message")
    source: Optional[str] = Field(default=None, description="e.g., ci, backend, nginx")


class PredictResponse(BaseModel):
    incident_type: IncidentType
    severity: Severity
    action: str
    team: Literal["platform", "backend", "devops", "security", "data"]
    confidence: float = Field(..., ge=0.0, le=1.0)

