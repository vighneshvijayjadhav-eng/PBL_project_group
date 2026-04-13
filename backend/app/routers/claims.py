from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import build_response, get_current_user, get_db, require_roles
from app.services.audit_logger import log_event
from app.services import claim_service


claims_router = APIRouter(prefix="/claims", tags=["claims"])
admin_router = APIRouter(prefix="/admin", tags=["claims"])
router = APIRouter()
router.include_router(claims_router)
router.include_router(admin_router)


@claims_router.get("")
def list_claims(
    request: Request,
    filters: schemas.ClaimFilterParams = Depends(),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    claims, pagination = claim_service.list_user_claims(db, current_user, filters)
    return build_response(
        request,
        success=True,
        data=schemas.ClaimListResponse(claims=claims),
        error=None,
        pagination=pagination,
    )


@claims_router.get("/summary")
def get_claim_summary(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    summary = claim_service.get_claim_summary_stats(db, current_user)
    return build_response(
        request,
        success=True,
        data=summary,
        error=None,
    )


@claims_router.post("")
def submit_claim(
    request: Request,
    payload: schemas.ClaimCreateRequest,
    current_user: models.User = Depends(require_roles(models.UserRole.policyholder)),
    db: Session = Depends(get_db),
):
    claim = claim_service.submit_claim(db, payload, current_user)

    log_event(
        db,
        user_id=current_user.user_id,
        event_type=models.AuditEventType.CLAIM_SUBMIT,
        entity_id=claim.claim_id,
        details={"policy_id": claim.policy_id},
    )
    return build_response(
        request,
        success=True,
        data=schemas.ClaimSubmitResponse.model_validate(claim),
        error=None,
        status_code=status.HTTP_201_CREATED,
    )


@claims_router.get("/{claim_id}")
def get_claim(
    request: Request,
    claim_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    claim = claim_service.get_claim_by_id(db, claim_id, current_user)
    return build_response(
        request,
        success=True,
        data=schemas.ClaimDetailResponse.model_validate(claim),
        error=None,
    )


@claims_router.patch("/{claim_id}/status")
def update_claim_status(
    request: Request,
    claim_id: int,
    payload: schemas.ClaimStatusUpdateRequest,
    current_user: models.User = Depends(
        require_roles(models.UserRole.adjuster, models.UserRole.admin)
    ),
    db: Session = Depends(get_db),
):
    claim = claim_service.update_claim_status(db, claim_id, payload, current_user)
    if claim.claim_status == models.ClaimStatus.approved:
        event_type = models.AuditEventType.CLAIM_APPROVE
    elif claim.claim_status == models.ClaimStatus.denied:
        event_type = models.AuditEventType.CLAIM_DENY
    else:
        event_type = models.AuditEventType.CLAIM_UPDATE
    log_event(
        db,
        user_id=current_user.user_id,
        event_type=event_type,
        entity_id=claim.claim_id,
        details={},
    )
    return build_response(
        request,
        success=True,
        data=schemas.ClaimStatusUpdateResponse.model_validate(claim),
        error=None,
    )


@claims_router.patch("/{claim_id}/assign")
def assign_claim(
    request: Request,
    claim_id: int,
    payload: schemas.ClaimAssignRequest,
    current_user: models.User = Depends(require_roles(models.UserRole.admin)),
    db: Session = Depends(get_db),
):
    claim = claim_service.assign_claim(db, claim_id, payload, current_user)
    log_event(
        db,
        user_id=current_user.user_id,
        event_type=models.AuditEventType.ASSIGN_ADJUSTER,
        entity_id=claim.claim_id,
        details={"adjuster_id": payload.adjuster_id},
    )
    return build_response(
        request,
        success=True,
        data=schemas.ClaimAssignResponse.model_validate(claim),
        error=None,
    )


@admin_router.get("/claims")
def list_admin_claims(
    request: Request,
    filters: schemas.ClaimFilterParams = Depends(),
    _: models.User = Depends(require_roles(models.UserRole.admin)),
    db: Session = Depends(get_db),
):
    claims, pagination = claim_service.list_admin_claims(db, filters)
    return build_response(
        request,
        success=True,
        data=schemas.ClaimListResponse(claims=claims),
        error=None,
        pagination=pagination,
    )
