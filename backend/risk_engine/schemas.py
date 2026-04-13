from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

ClaimType = Literal["accident", "theft", "fire", "other"]
ClaimStatus = Literal[
    "submitted",
    "risk_scored",
    "auto_approved",
    "escalated",
    "under_review",
    "approved",
    "denied",
    "settled",
    "closed",
]
GenderValue = Literal["male", "female", "other"]
SeverityValue = Literal["low", "medium", "high"]
RiskLevelValue = Literal["low", "medium", "high"]


class ClaimRiskInput(BaseModel):
    claim_id: int
    policy_id: int
    claimant_id: int
    adjuster_id: int | None
    claim_type: ClaimType
    incident_date: datetime
    claim_amount: Decimal
    claim_status: ClaimStatus
    description: str
    claimant_age: int
    claimant_gender: GenderValue
    claimant_location: str
    policy_tenure_months: int
    premium_to_claim_ratio: Decimal
    previous_claims_count: int
    previous_fraud_flag: bool
    incident_severity: SeverityValue
    hospitalization_required: bool
    police_report_filed: bool
    document_count: int
    claim_submission_delay_days: int
    created_at: datetime

    model_config = ConfigDict(extra="forbid")


class RiskScoreOutput(BaseModel):
    rule_score: float
    ml_score: float
    final_risk_score: float
    risk_level: RiskLevelValue

    model_config = ConfigDict(extra="forbid")
