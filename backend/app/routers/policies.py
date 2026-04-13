from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.dependencies import build_response, get_current_user, get_db, raise_app_error, require_roles
from app.services.audit_logger import log_event


router = APIRouter(prefix="/api/policies", tags=["policies"])


@router.get("")
def list_policies(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    policies = [schemas.PolicyOut.model_validate(policy) for policy in crud.list_policies(db, current_user)]
    return build_response(request, success=True, data={"policies": policies}, error=None)


@router.post("")
def create_policy(
    request: Request,
    payload: schemas.PolicyCreate,
    current_user: models.User = Depends(require_roles(models.UserRole.admin)),
    db: Session = Depends(get_db),
):
    policy = crud.create_policy(db, payload)
    log_event(
        db,
        user_id=current_user.user_id,
        event_type=models.AuditEventType.POLICY_CREATE,
        entity_id=policy.policy_id,
        details={"user_id": policy.user_id},
    )
    return build_response(
        request,
        success=True,
        data={"policy": schemas.PolicyOut.model_validate(policy)},
        error=None,
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{policy_id}")
def update_policy(
    request: Request,
    policy_id: int,
    payload: schemas.PolicyUpdate,
    _: models.User = Depends(require_roles(models.UserRole.admin)),
    db: Session = Depends(get_db),
):
    policy = crud.get_policy_by_id(db, policy_id)
    if not policy:
        raise_app_error(status.HTTP_404_NOT_FOUND, "POLICY_NOT_FOUND")
    policy = crud.update_policy(db, policy, payload)
    return build_response(
        request,
        success=True,
        data={"policy": schemas.PolicyOut.model_validate(policy)},
        error=None,
    )


@router.delete("/{policy_id}")
def delete_policy(
    request: Request,
    policy_id: int,
    _: models.User = Depends(require_roles(models.UserRole.admin)),
    db: Session = Depends(get_db),
):
    policy = crud.get_policy_by_id(db, policy_id)
    if not policy:
        raise_app_error(status.HTTP_404_NOT_FOUND, "POLICY_NOT_FOUND")
    crud.delete_policy(db, policy)
    return build_response(request, success=True, data={"policy_id": policy_id}, error=None)
