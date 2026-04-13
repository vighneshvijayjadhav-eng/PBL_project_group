from risk_engine.ml_model import predict
from risk_engine.rule_engine import compute_rule_score
from risk_engine.schemas import ClaimRiskInput, RiskScoreOutput
from app.config import settings


def _map_risk_level(score: float) -> str:
    if score < 0.3:
        return "low"
    if score < 0.7:
        return "medium"
    return "high"


def score_claim_payload(payload: dict) -> RiskScoreOutput:
    try:
        claim = ClaimRiskInput(**payload)
    except Exception as exc:
        error_text = str(exc)
        if "Field required" in error_text:
            raise ValueError("FEATURE_MISSING") from exc
        raise ValueError("SCHEMA_MISMATCH") from exc

    rule_score = compute_rule_score(claim)
    ml_score = predict(claim)
    final_score = round(
        (settings.risk_weight_ml * ml_score) + (settings.risk_weight_rb * rule_score),
        4,
    )
    final_score = max(0.0, min(1.0, final_score))

    return RiskScoreOutput(
        rule_score=rule_score,
        ml_score=ml_score,
        final_risk_score=final_score,
        risk_level=_map_risk_level(final_score),
    )
