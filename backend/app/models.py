import enum
from decimal import Decimal
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    policyholder = "policyholder"
    adjuster = "adjuster"
    admin = "admin"


class PolicyStatus(str, enum.Enum):
    active = "active"
    expired = "expired"


class ClaimStatus(str, enum.Enum):
    submitted = "submitted"
    risk_scored = "risk_scored"
    auto_approved = "auto_approved"
    escalated = "escalated"
    under_review = "under_review"
    approved = "approved"
    denied = "denied"
    settled = "settled"
    closed = "closed"


class ClaimType(str, enum.Enum):
    accident = "accident"
    theft = "theft"
    fire = "fire"
    other = "other"


class DocumentType(str, enum.Enum):
    photo = "photo"
    invoice = "invoice"
    report = "report"
    other = "other"


class AuditEventType(str, enum.Enum):
    LOGIN = "LOGIN"
    CLAIM_SUBMIT = "CLAIM_SUBMIT"
    CLAIM_UPDATE = "CLAIM_UPDATE"
    CLAIM_APPROVE = "CLAIM_APPROVE"
    CLAIM_DENY = "CLAIM_DENY"
    POLICY_CREATE = "POLICY_CREATE"
    USER_CREATE = "USER_CREATE"
    ASSIGN_ADJUSTER = "ASSIGN_ADJUSTER"
    RISK_SCORE_APPLIED = "RISK_SCORE_APPLIED"
    MODEL_RETRAIN = "MODEL_RETRAIN"
    DATA_VALIDATION_FAILED = "DATA_VALIDATION_FAILED"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    policies: Mapped[list["Policy"]] = relationship("Policy", back_populates="user")
    claims_as_claimant: Mapped[list["Claim"]] = relationship(
        "Claim",
        back_populates="claimant",
        foreign_keys="Claim.claimant_id",
    )
    claims_as_adjuster: Mapped[list["Claim"]] = relationship(
        "Claim",
        back_populates="adjuster",
        foreign_keys="Claim.adjuster_id",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user")


class Policy(Base):
    __tablename__ = "policies"

    policy_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    policy_type: Mapped[str] = mapped_column(String(255), nullable=False)
    coverage_details: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    premium_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    policy_status: Mapped[PolicyStatus] = mapped_column(Enum(PolicyStatus), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="policies")
    claims: Mapped[list["Claim"]] = relationship("Claim", back_populates="policy")


class Claim(Base):
    __tablename__ = "claims"

    claim_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    policy_id: Mapped[int] = mapped_column(ForeignKey("policies.policy_id"), nullable=False)
    claimant_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    adjuster_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    claim_type: Mapped[ClaimType] = mapped_column(Enum(ClaimType), nullable=False)
    incident_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    claim_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    claim_status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus), nullable=False, default=ClaimStatus.submitted, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    claimant_age: Mapped[int] = mapped_column(Integer, nullable=False)
    claimant_gender: Mapped[str] = mapped_column(String(50), nullable=False)
    claimant_location: Mapped[str] = mapped_column(String(255), nullable=False)
    policy_tenure_months: Mapped[int] = mapped_column(Integer, nullable=False)
    premium_to_claim_ratio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    previous_claims_count: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_fraud_flag: Mapped[bool] = mapped_column(nullable=False)
    incident_severity: Mapped[str] = mapped_column(String(50), nullable=False)
    hospitalization_required: Mapped[bool] = mapped_column(nullable=False)
    police_report_filed: Mapped[bool] = mapped_column(nullable=False)
    document_count: Mapped[int] = mapped_column(Integer, nullable=False)
    claim_submission_delay_days: Mapped[int] = mapped_column(Integer, nullable=False)
    rule_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    ml_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    final_risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, index=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    policy: Mapped["Policy"] = relationship("Policy", back_populates="claims")
    claimant: Mapped["User"] = relationship(
        "User",
        back_populates="claims_as_claimant",
        foreign_keys=[claimant_id],
    )
    adjuster: Mapped["User | None"] = relationship(
        "User",
        back_populates="claims_as_adjuster",
        foreign_keys=[adjuster_id],
    )
    documents: Mapped[list["ClaimDocument"]] = relationship("ClaimDocument", back_populates="claim")


class ClaimDocument(Base):
    __tablename__ = "claim_documents"

    document_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.claim_id"), nullable=False)
    doc_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    claim: Mapped["Claim"] = relationship("Claim", back_populates="documents")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    event_type: Mapped[AuditEventType] = mapped_column(Enum(AuditEventType), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="audit_logs")
