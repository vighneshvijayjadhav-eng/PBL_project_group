import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from risk_engine.scorer import score_claim_payload


def main() -> None:
    claim_payload = {
        "claim_id": 5001,
        "policy_id": 101,
        "claimant_id": 1,
        "adjuster_id": None,
        "claim_type": "accident",
        "incident_date": datetime.now(timezone.utc).isoformat(),
        "claim_amount": "15000.00",
        "claim_status": "submitted",
        "description": "Rear-end collision",
        "claimant_age": 35,
        "claimant_gender": "male",
        "claimant_location": "Pune",
        "policy_tenure_months": 24,
        "premium_to_claim_ratio": "1.20",
        "previous_claims_count": 2,
        "previous_fraud_flag": False,
        "incident_severity": "medium",
        "hospitalization_required": True,
        "police_report_filed": True,
        "document_count": 3,
        "claim_submission_delay_days": 5,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = score_claim_payload(claim_payload)
    result_dict = result.model_dump()

    assert set(result_dict.keys()) == {"rule_score", "ml_score", "final_risk_score", "risk_level"}
    assert 0.0 <= result.rule_score <= 1.0
    assert 0.0 <= result.ml_score <= 1.0
    assert 0.0 <= result.final_risk_score <= 1.0
    assert result.risk_level in {"low", "medium", "high"}

    expected_level = (
        "low"
        if result.final_risk_score < 0.3
        else "medium"
        if result.final_risk_score < 0.7
        else "high"
    )
    assert result.risk_level == expected_level

    print(json.dumps({"claim_created": True, "stored_payload": claim_payload, "score_output": result_dict}, indent=2))


if __name__ == "__main__":
    main()
