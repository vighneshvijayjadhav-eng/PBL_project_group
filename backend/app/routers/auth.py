from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.dependencies import (
    authenticate_user,
    build_response,
    create_token_pair,
    get_db,
    get_current_user,
    get_password_hash,
    logout_user,
    refresh_access_token,
    raise_app_error,
)
from app.services.audit_logger import log_event


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(request: Request, payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, payload.email):
        raise_app_error(
            status.HTTP_400_BAD_REQUEST,
            "VALIDATION_ERROR",
            details={"email": "Email already exists"},
        )

    user = crud.create_user(db, payload, get_password_hash(payload.password))
    log_event(
        db,
        user_id=user.user_id,
        event_type=models.AuditEventType.USER_CREATE,
        entity_id=user.user_id,
        details={"role": user.role.value},
    )
    return build_response(request, success=True, data={"user": schemas.UserOut.model_validate(user)}, error=None)


@router.post("/login")
def login(request: Request, payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise_app_error(status.HTTP_401_UNAUTHORIZED, "AUTH_INVALID")

    tokens = create_token_pair(user)
    log_event(
        db,
        user_id=user.user_id,
        event_type=models.AuditEventType.LOGIN,
        entity_id=user.user_id,
        details={},
    )
    return build_response(
        request,
        success=True,
        data=tokens,
        error=None,
    )


@router.post("/refresh")
def refresh(request: Request, payload: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    tokens = refresh_access_token(db, payload.refresh_token)
    return build_response(
        request,
        success=True,
        data=tokens,
        error=None,
    )


@router.post("/logout")
def logout(
    request: Request,
    payload: schemas.LogoutRequest,
    current_user: models.User = Depends(get_current_user),
):
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise_app_error(status.HTTP_401_UNAUTHORIZED, "AUTH_INVALID")

    access_token = authorization.removeprefix("Bearer ").strip()
    logout_user(access_token, payload.refresh_token)
    return build_response(
        request,
        success=True,
        data=schemas.LogoutResponse(message="Logged out successfully"),
        error=None,
    )
