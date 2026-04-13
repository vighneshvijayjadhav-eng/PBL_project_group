from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import ClaimStatus, ClaimType


GenderValue = Literal["male", "female", "other"]
SeverityValue = Literal["low", "medium", "high"]
RiskLevelValue = Literal["low", "medium", "high"]
ClaimFilterStatus = Literal["approved", "rejected", "pending"]


class ClaimCreateRequest(BaseModel):
    policy_id: int
    claim_type: ClaimType
    incident_date: datetime
    claim_amount: Decimal = Field(gt=0)
    description: str
    claimant_age: int = Field(ge=0)
    claimant_gender: GenderValue
    claimant_location: str
    policy_tenure_months: int = Field(ge=0)
    premium_to_claim_ratio: Decimal = Field(ge=0)
    previous_claims_count: int = Field(ge=0)
    previous_fraud_flag: bool
    incident_severity: SeverityValue
    hospitalization_required: bool
    police_report_filed: bool
    document_count: int = Field(ge=0)
    claim_submission_delay_days: int = Field(ge=0)

    @field_validator("incident_date")
    @classmethod
    def validate_incident_date(cls, value: datetime) -> datetime:
        now = datetime.now(timezone.utc)
        compare_value = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if compare_value > now:
            raise ValueError("incident_date must not be in the future")
        return value


class ClaimSubmitResponse(BaseModel):
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
    rule_score: Decimal
    ml_score: Decimal
    final_risk_score: Decimal
    risk_level: RiskLevelValue
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClaimDetailResponse(ClaimSubmitResponse):
    pass


class ClaimResponse(BaseModel):
    claim_id: int
    claimant_id: int
    claim_amount: Decimal
    claim_type: ClaimType
    description: str
    fraud_score: Decimal = Field(validation_alias="final_risk_score")
    status: ClaimFilterStatus
    created_at: datetime
    risk_level: RiskLevelValue

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ClaimListResponse(BaseModel):
    claims: list[ClaimResponse]


class ClaimSummaryStatsResponse(BaseModel):
    total_claims: int
    avg_risk_score: Decimal
    high_risk_percentage: Decimal


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    pages: int


class ClaimFilterParams(BaseModel):
    status: ClaimFilterStatus | None = None
    min_risk_score: Decimal | None = Field(default=None, ge=0)
    max_risk_score: Decimal | None = Field(default=None, ge=0)
    risk_level: RiskLevelValue | None = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)

    @field_validator("max_risk_score")
    @classmethod
    def validate_risk_range(cls, value: Decimal | None, info):
        min_risk_score = info.data.get("min_risk_score")
        if value is not None and min_risk_score is not None and value < min_risk_score:
            raise ValueError("max_risk_score must be greater than or equal to min_risk_score")
        return value


class ClaimStatusUpdateRequest(BaseModel):
    claim_status: ClaimStatus


class ClaimStatusUpdateResponse(BaseModel):
    claim_id: int
    claim_status: ClaimStatus
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClaimAssignRequest(BaseModel):
    adjuster_id: int


class ClaimAssignResponse(BaseModel):
    claim_id: int
    adjuster_id: int | None
    claim_status: ClaimStatus

    model_config = ConfigDict(from_attributes=True)


class RiskScoreRequest(BaseModel):
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


class RiskScoreResponse(BaseModel):
    rule_score: Decimal
    ml_score: Decimal
    final_risk_score: Decimal
    risk_level: RiskLevelValue

    model_config = ConfigDict(extra="forbid")
