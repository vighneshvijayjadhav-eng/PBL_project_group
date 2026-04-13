from decimal import Decimal, ROUND_HALF_UP

from app.dependencies import raise_app_error
from app.schemas import RiskScoreRequest, RiskScoreResponse
from risk_engine import ml_model
from risk_engine.scorer import score_claim_payload


def _to_decimal(value: float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def score_claim(payload: RiskScoreRequest) -> RiskScoreResponse:
    try:
        result = score_claim_payload(payload.model_dump(mode="json"))
    except ValueError as exc:
        code = str(exc)
        if code not in {"FEATURE_MISSING", "MODEL_INPUT_INVALID", "SCHEMA_MISMATCH"}:
            code = "MODEL_INPUT_INVALID"
        raise_app_error(400, code)
    except FileNotFoundError:
        raise_app_error(503, "RISK_ENGINE_UNAVAILABLE")

    return RiskScoreResponse(
        rule_score=_to_decimal(result.rule_score),
        ml_score=_to_decimal(result.ml_score),
        final_risk_score=_to_decimal(result.final_risk_score),
        risk_level=result.risk_level,
    )


def is_model_loaded() -> bool:
    try:
        ml_model.load_model()
    except FileNotFoundError:
        return False
    return True
