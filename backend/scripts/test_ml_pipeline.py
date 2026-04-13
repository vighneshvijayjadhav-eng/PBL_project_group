import json
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings
from risk_engine.feature_config import FEATURE_ORDER
from risk_engine.ml_model import (
    build_feature_vector,
    load_encoders,
    load_feature_order,
    load_model,
    load_scaler,
    predict,
)
from risk_engine.scorer import score_claim_payload
from risk_engine.schemas import ClaimRiskInput


def sample_claim() -> ClaimRiskInput:
    return ClaimRiskInput(
        claim_id=5001,
        policy_id=101,
        claimant_id=1,
        adjuster_id=None,
        claim_type="accident",
        incident_date=datetime.now(timezone.utc),
        claim_amount=Decimal("15000.00"),
        claim_status="submitted",
        description="Rear-end collision",
        claimant_age=35,
        claimant_gender="male",
        claimant_location="Pune",
        policy_tenure_months=24,
        premium_to_claim_ratio=Decimal("1.20"),
        previous_claims_count=2,
        previous_fraud_flag=False,
        incident_severity="medium",
        hospitalization_required=True,
        police_report_filed=True,
        document_count=3,
        claim_submission_delay_days=5,
        created_at=datetime.now(timezone.utc),
    )


def expect_error(code: str, fn) -> None:
    try:
        fn()
    except ValueError as exc:
        assert str(exc) == code, f"expected {code}, got {exc}"
        return
    raise AssertionError(f"expected {code} to be raised")


def main() -> None:
    model_bundle = load_model()
    scaler = load_scaler()
    encoders = load_encoders()
    feature_order = load_feature_order()

    assert feature_order == FEATURE_ORDER, "feature_order mismatch"
    assert model_bundle["feature_order"] == FEATURE_ORDER, "model bundle feature_order mismatch"
    assert set(encoders.keys()) == {"claimant_gender", "incident_severity", "claimant_location"}, "encoders mismatch"
    assert hasattr(scaler, "transform"), "scaler missing transform"

    claim = sample_claim()
    feature_vector = build_feature_vector(claim)
    assert feature_vector.shape == (1, len(FEATURE_ORDER)), "feature vector shape mismatch"

    probability = predict(claim)
    assert 0.0 <= probability <= 1.0, "probability out of range"

    missing_feature_payload = claim.model_dump()
    del missing_feature_payload["claimant_location"]
    expect_error("FEATURE_MISSING", lambda: build_feature_vector(missing_feature_payload))

    invalid_category_payload = claim.model_dump()
    invalid_category_payload["claimant_location"] = "UnknownCity"
    expect_error("MODEL_INPUT_INVALID", lambda: build_feature_vector(invalid_category_payload))

    scoring_result = score_claim_payload(claim.model_dump(mode="json"))
    assert 0.0 <= scoring_result.rule_score <= 1.0, "rule_score out of range"
    assert 0.0 <= scoring_result.ml_score <= 1.0, "ml_score out of range"
    assert 0.0 <= scoring_result.final_risk_score <= 1.0, "final_risk_score out of range"
    assert scoring_result.risk_level in {"low", "medium", "high"}, "risk_level invalid"

    result = {
        "model_path": settings.ml_model_path,
        "scaler_path": settings.scaler_path,
        "encoders_path": settings.encoders_path,
        "feature_order_path": settings.feature_order_path,
        "probability": probability,
        "risk_level": scoring_result.risk_level,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
