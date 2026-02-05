from fastapi import APIRouter
from backend.app.schemas.incident import PredictRequest, PredictResponse
from backend.app.services.decision_rules import rule_based_decision

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    return rule_based_decision(req.log)

