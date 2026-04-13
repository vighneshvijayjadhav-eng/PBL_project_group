from decimal import Decimal

from sqlalchemy import case, func
from sqlalchemy.orm import Session, joinedload, load_only

from app import models
from app.dependencies import raise_app_error
from app.schemas.claim import (
    ClaimAssignRequest,
    ClaimFilterParams,
    ClaimCreateRequest,
    ClaimStatusUpdateRequest,
    ClaimResponse,
    ClaimSummaryStatsResponse,
    PaginationMeta,
    RiskScoreRequest,
)
from app.services.risk_client import score_claim


PENDING_STATUSES = (
    models.ClaimStatus.submitted,
    models.ClaimStatus.risk_scored,
    models.ClaimStatus.auto_approved,
    models.ClaimStatus.escalated,
    models.ClaimStatus.under_review,
    models.ClaimStatus.settled,
    models.ClaimStatus.closed,
)


def _normalized_status(claim_status: models.ClaimStatus) -> str:
    if claim_status == models.ClaimStatus.approved:
        return "approved"
    if claim_status == models.ClaimStatus.denied:
        return "rejected"
    return "pending"


def _build_claim_response(claim: models.Claim) -> ClaimResponse:
    return ClaimResponse.model_validate(
        {
            "claim_id": claim.claim_id,
            "claimant_id": claim.claimant_id,
            "claim_amount": claim.claim_amount,
            "claim_type": claim.claim_type,
            "description": claim.description,
            "final_risk_score": claim.final_risk_score,
            "status": _normalized_status(claim.claim_status),
            "created_at": claim.created_at,
            "risk_level": claim.risk_level,
        }
    )


def _apply_common_filters(query, filters: ClaimFilterParams):
    if filters.status == "approved":
        query = query.filter(models.Claim.claim_status == models.ClaimStatus.approved)
    elif filters.status == "rejected":
        query = query.filter(models.Claim.claim_status == models.ClaimStatus.denied)
    elif filters.status == "pending":
        query = query.filter(models.Claim.claim_status.in_(PENDING_STATUSES))

    if filters.min_risk_score is not None:
        query = query.filter(models.Claim.final_risk_score >= filters.min_risk_score)
    if filters.max_risk_score is not None:
        query = query.filter(models.Claim.final_risk_score <= filters.max_risk_score)
    return query


def _apply_risk_level_filter(query, risk_level: str | None):
    if risk_level == "low":
        return query.filter(models.Claim.final_risk_score < Decimal("0.3"))
    if risk_level == "medium":
        return query.filter(
            models.Claim.final_risk_score >= Decimal("0.3"),
            models.Claim.final_risk_score < Decimal("0.7"),
        )
    if risk_level == "high":
        return query.filter(models.Claim.final_risk_score >= Decimal("0.7"))
    return query


def _paginate(query, page: int, limit: int) -> tuple[list[models.Claim], PaginationMeta]:
    total = query.order_by(None).with_entities(func.count(models.Claim.claim_id)).scalar() or 0
    pages = max((total + limit - 1) // limit, 1)
    items = query.offset((page - 1) * limit).limit(limit).all()
    pagination = PaginationMeta(page=page, limit=limit, total=total, pages=pages)
    return items, pagination


def submit_claim(db: Session, payload: ClaimCreateRequest, current_user: models.User) -> models.Claim:
    policy = (
        db.query(models.Policy)
        .options(joinedload(models.Policy.user))
        .filter(models.Policy.policy_id == payload.policy_id)
        .first()
    )
    if not policy:
        raise_app_error(404, "POLICY_NOT_FOUND")
    if policy.user_id != current_user.user_id:
        raise_app_error(403, "ACCESS_DENIED")

    claim = models.Claim(
        policy_id=payload.policy_id,
        claimant_id=current_user.user_id,
        adjuster_id=None,
        claim_type=payload.claim_type,
        incident_date=payload.incident_date,
        claim_amount=payload.claim_amount,
        claim_status=models.ClaimStatus.submitted,
        description=payload.description,
        claimant_age=payload.claimant_age,
        claimant_gender=payload.claimant_gender,
        claimant_location=payload.claimant_location,
        policy_tenure_months=payload.policy_tenure_months,
        premium_to_claim_ratio=payload.premium_to_claim_ratio,
        previous_claims_count=payload.previous_claims_count,
        previous_fraud_flag=payload.previous_fraud_flag,
        incident_severity=payload.incident_severity,
        hospitalization_required=payload.hospitalization_required,
        police_report_filed=payload.police_report_filed,
        document_count=payload.document_count,
        claim_submission_delay_days=payload.claim_submission_delay_days,
        rule_score=Decimal("0.0000"),
        ml_score=Decimal("0.0000"),
        final_risk_score=Decimal("0.0000"),
        risk_level="low",
    )
    db.add(claim)
    db.flush()

    risk_request = RiskScoreRequest(
        claim_id=claim.claim_id,
        policy_id=claim.policy_id,
        claimant_id=claim.claimant_id,
        adjuster_id=claim.adjuster_id,
        claim_type=claim.claim_type,
        incident_date=claim.incident_date,
        claim_amount=claim.claim_amount,
        claim_status=claim.claim_status,
        description=claim.description,
        claimant_age=claim.claimant_age,
        claimant_gender=claim.claimant_gender,
        claimant_location=claim.claimant_location,
        policy_tenure_months=claim.policy_tenure_months,
        premium_to_claim_ratio=claim.premium_to_claim_ratio,
        previous_claims_count=claim.previous_claims_count,
        previous_fraud_flag=claim.previous_fraud_flag,
        incident_severity=claim.incident_severity,
        hospitalization_required=claim.hospitalization_required,
        police_report_filed=claim.police_report_filed,
        document_count=claim.document_count,
        claim_submission_delay_days=claim.claim_submission_delay_days,
        created_at=claim.created_at,
    )
    scores = score_claim(risk_request)
    claim.rule_score = scores.rule_score
    claim.ml_score = scores.ml_score
    claim.final_risk_score = scores.final_risk_score
    claim.risk_level = scores.risk_level
    claim.claim_status = models.ClaimStatus.risk_scored

    db.commit()
    db.refresh(claim)
    return claim


def get_claim_by_id(db: Session, claim_id: int, current_user: models.User) -> models.Claim:
    claim = (
        db.query(models.Claim)
        .options(
            joinedload(models.Claim.policy),
            joinedload(models.Claim.claimant),
            joinedload(models.Claim.adjuster),
        )
        .filter(models.Claim.claim_id == claim_id)
        .first()
    )
    if not claim:
        raise_app_error(404, "CLAIM_NOT_FOUND")

    if claim.claimant_id != current_user.user_id:
        raise_app_error(403, "ACCESS_DENIED")

    return claim


def list_user_claims(
    db: Session,
    current_user: models.User,
    filters: ClaimFilterParams,
) -> tuple[list[ClaimResponse], PaginationMeta]:
    query = (
        db.query(models.Claim)
        .options(
            load_only(
                models.Claim.claim_id,
                models.Claim.claimant_id,
                models.Claim.claim_amount,
                models.Claim.claim_type,
                models.Claim.description,
                models.Claim.final_risk_score,
                models.Claim.claim_status,
                models.Claim.created_at,
                models.Claim.risk_level,
            )
        )
        .filter(models.Claim.claimant_id == current_user.user_id)
        .order_by(models.Claim.created_at.desc())
    )
    query = _apply_common_filters(query, filters)
    claims, pagination = _paginate(query, filters.page, filters.limit)
    return [_build_claim_response(claim) for claim in claims], pagination


def list_admin_claims(
    db: Session,
    filters: ClaimFilterParams,
) -> tuple[list[ClaimResponse], PaginationMeta]:
    query = (
        db.query(models.Claim)
        .options(
            load_only(
                models.Claim.claim_id,
                models.Claim.claimant_id,
                models.Claim.claim_amount,
                models.Claim.claim_type,
                models.Claim.description,
                models.Claim.final_risk_score,
                models.Claim.claim_status,
                models.Claim.created_at,
                models.Claim.risk_level,
            )
        )
        .order_by(models.Claim.created_at.desc())
    )
    query = _apply_common_filters(query, filters)
    query = _apply_risk_level_filter(query, filters.risk_level)

    claims, pagination = _paginate(query, filters.page, filters.limit)
    return [_build_claim_response(claim) for claim in claims], pagination


def get_claim_summary_stats(db: Session, current_user: models.User) -> ClaimSummaryStatsResponse:
    aggregates = (
        db.query(
            func.count(models.Claim.claim_id),
            func.avg(models.Claim.final_risk_score),
            func.sum(
                case(
                    (models.Claim.final_risk_score >= Decimal("0.7"), 1),
                    else_=0,
                )
            ),
        )
        .filter(models.Claim.claimant_id == current_user.user_id)
        .one()
    )

    total_claims = int(aggregates[0] or 0)
    avg_risk_score = Decimal(str(aggregates[1] or "0")).quantize(Decimal("0.0001"))
    high_risk_count = int(aggregates[2] or 0)
    high_risk_percentage = (
        (Decimal(high_risk_count) / Decimal(total_claims) * Decimal("100")).quantize(Decimal("0.01"))
        if total_claims
        else Decimal("0.00")
    )

    return ClaimSummaryStatsResponse(
        total_claims=total_claims,
        avg_risk_score=avg_risk_score,
        high_risk_percentage=high_risk_percentage,
    )


def get_claim_or_404(db: Session, claim_id: int) -> models.Claim:
    claim = (
        db.query(models.Claim)
        .options(
            joinedload(models.Claim.policy),
            joinedload(models.Claim.claimant),
            joinedload(models.Claim.adjuster),
        )
        .filter(models.Claim.claim_id == claim_id)
        .first()
    )
    if not claim:
        raise_app_error(404, "CLAIM_NOT_FOUND")
    return claim


def update_claim_status(
    db: Session,
    claim_id: int,
    payload: ClaimStatusUpdateRequest,
    current_user: models.User,
) -> models.Claim:
    claim = get_claim_or_404(db, claim_id)
    claim.claim_status = payload.claim_status
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def assign_claim(
    db: Session,
    claim_id: int,
    payload: ClaimAssignRequest,
    current_user: models.User,
) -> models.Claim:
    claim = get_claim_or_404(db, claim_id)
    adjuster = db.query(models.User).filter(models.User.user_id == payload.adjuster_id).first()
    if not adjuster or adjuster.role != models.UserRole.adjuster:
        raise_app_error(400, "VALIDATION_ERROR", details={"adjuster_id": "Adjuster not found"})

    claim.adjuster_id = payload.adjuster_id
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim
