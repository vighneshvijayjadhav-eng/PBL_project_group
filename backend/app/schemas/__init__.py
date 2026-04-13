from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import DocumentType, PolicyStatus, UserRole
from app.schemas.claim import (
    ClaimAssignRequest as ClaimAssign,
    ClaimAssignRequest,
    ClaimAssignResponse,
    ClaimCreateRequest as ClaimCreate,
    ClaimCreateRequest,
    ClaimFilterParams,
    ClaimFilterStatus,
    ClaimDetailResponse,
    ClaimListResponse,
    ClaimSummaryStatsResponse,
    ClaimResponse,
    ClaimDetailResponse as ClaimOut,
    ClaimStatusUpdateRequest as ClaimUpdate,
    ClaimStatusUpdateRequest,
    ClaimStatusUpdateResponse,
    ClaimSubmitResponse,
    GenderValue,
    RiskLevelValue,
    RiskScoreRequest,
    RiskScoreResponse,
    SeverityValue,
    PaginationMeta,
)


class MetaSchema(BaseModel):
    timestamp: str
    request_id: str
    pagination: PaginationMeta | None = None


class ErrorSchema(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ResponseEnvelope(BaseModel):
    success: bool
    data: Any
    error: ErrorSchema | None
    meta: MetaSchema


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class LogoutResponse(BaseModel):
    message: str


class UserOut(UserBase):
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PolicyBase(BaseModel):
    user_id: int
    policy_type: str
    coverage_details: str
    start_date: datetime
    end_date: datetime
    premium_amount: Decimal
    policy_status: PolicyStatus


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    user_id: int | None = None
    policy_type: str | None = None
    coverage_details: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    premium_amount: Decimal | None = None
    policy_status: PolicyStatus | None = None


class PolicyOut(PolicyBase):
    policy_id: int

    model_config = ConfigDict(from_attributes=True)


class ClaimDocumentOut(BaseModel):
    document_id: int
    claim_id: int
    doc_type: DocumentType
    file_path: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogOut(BaseModel):
    log_id: int
    user_id: int
    event_type: str
    entity_id: int
    details: dict[str, Any]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenPayload(BaseModel):
    user_id: int
    email: EmailStr
    role: UserRole
    exp: int
    type: Literal["access", "refresh"] = "access"
    jti: str | None = None


__all__ = [
    "AuthTokenResponse",
    "AuditLogOut",
    "ClaimAssignRequest",
    "ClaimAssignResponse",
    "ClaimAssign",
    "ClaimCreate",
    "ClaimCreateRequest",
    "ClaimDetailResponse",
    "ClaimFilterParams",
    "ClaimFilterStatus",
    "ClaimListResponse",
    "ClaimSummaryStatsResponse",
    "ClaimDocumentOut",
    "ClaimOut",
    "ClaimResponse",
    "ClaimUpdate",
    "ClaimStatusUpdateRequest",
    "ClaimStatusUpdateResponse",
    "ClaimSubmitResponse",
    "ErrorSchema",
    "RefreshTokenRequest",
    "GenderValue",
    "LogoutRequest",
    "LogoutResponse",
    "MetaSchema",
    "PaginationMeta",
    "PolicyCreate",
    "PolicyOut",
    "PolicyUpdate",
    "ResponseEnvelope",
    "RiskLevelValue",
    "RiskScoreRequest",
    "RiskScoreResponse",
    "SeverityValue",
    "TokenPayload",
    "UserCreate",
    "UserLogin",
    "UserOut",
]
