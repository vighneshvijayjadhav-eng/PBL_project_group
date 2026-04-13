from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import settings
from app.database import SessionLocal
from app.services.refresh_token_store import is_refresh_token_active, revoke_refresh_token, store_refresh_token
from app.services.token_blacklist import is_token_revoked, revoke_token_jti


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ERROR_MESSAGES = {
    "AUTH_INVALID": "Invalid authentication credentials",
    "AUTH_EXPIRED": "Authentication token has expired",
    "ACCESS_DENIED": "You do not have access to this resource",
    "USER_NOT_FOUND": "User not found",
    "POLICY_NOT_FOUND": "Policy not found",
    "CLAIM_NOT_FOUND": "Claim does not exist",
    "INVALID_STATUS_TRANSITION": "Invalid status transition",
    "RISK_ENGINE_UNAVAILABLE": "Risk engine is unavailable",
    "MODEL_INPUT_INVALID": "Model input is invalid",
    "FEATURE_MISSING": "Required feature is missing",
    "SCHEMA_MISMATCH": "Schema mismatch detected",
    "VALIDATION_ERROR": "Request validation failed",
    "RATE_LIMITED": "Too many requests",
    "INTERNAL_ERROR": "Internal server error",
}


class AppException(Exception):
    def __init__(self, status_code: int, code: str, message: str | None = None, details: dict | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message or ERROR_MESSAGES.get(code, "Application error")
        self.details = details or {}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_response(
    request: Request,
    *,
    success: bool,
    data: object,
    error: schemas.ErrorSchema | dict | None,
    pagination: schemas.PaginationMeta | dict | None = None,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    meta = schemas.MetaSchema(
        timestamp=utc_now_iso(),
        request_id=getattr(request.state, "request_id", str(uuid4())),
        pagination=pagination,
    )
    envelope = schemas.ResponseEnvelope(success=success, data=data, error=error, meta=meta)
    return JSONResponse(status_code=status_code, content=jsonable_encoder(envelope))


def raise_app_error(status_code: int, code: str, message: str | None = None, details: dict | None = None) -> None:
    raise AppException(status_code=status_code, code=code, message=message, details=details)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(user: models.User) -> str:
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role.value,
        "type": "access",
        "jti": str(uuid4()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(user: models.User) -> str:
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role.value,
        "type": "refresh",
        "jti": str(uuid4()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    store_refresh_token(token, user_id=user.user_id, expires_at=payload["exp"])
    return token


def create_token_pair(user: models.User) -> schemas.AuthTokenResponse:
    return schemas.AuthTokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )


def decode_token(token: str, *, expected_type: str) -> schemas.TokenPayload:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_data = schemas.TokenPayload(**payload)
    except ExpiredSignatureError as exc:
        raise_app_error(status.HTTP_401_UNAUTHORIZED, "AUTH_EXPIRED")
    except JWTError as exc:
        raise_app_error(status.HTTP_401_UNAUTHORIZED, "AUTH_INVALID")

    if token_data.type != expected_type:
        raise_app_error(status.HTTP_401_UNAUTHORIZED, "AUTH_INVALID")
    if is_token_revoked(token_data.jti):
        raise_app_error(status.HTTP_401_UNAUTHORIZED, "AUTH_INVALID")
    return token_data


def refresh_access_token(db: Session, refresh_token: str) -> schemas.AuthTokenResponse:
    token_data = decode_token(refresh_token, expected_type="refresh")
    if not is_refresh_token_active(refresh_token, user_id=token_data.user_id):
        raise_app_error(status.HTTP_401_UNAUTHORIZED, "AUTH_INVALID")

    user = crud.get_user_by_id(db, token_data.user_id)
    if not user:
        revoke_refresh_token(refresh_token)
        raise_app_error(status.HTTP_401_UNAUTHORIZED, "AUTH_INVALID")

    revoke_token_jti(token_data.jti, expires_at=token_data.exp)
    revoke_refresh_token(refresh_token)
    return create_token_pair(user)


def logout_user(access_token: str, refresh_token: str) -> None:
    access_payload = decode_token(access_token, expected_type="access")
    refresh_payload = decode_token(refresh_token, expected_type="refresh")
    revoke_token_jti(access_payload.jti, expires_at=access_payload.exp)
    revoke_token_jti(refresh_payload.jti, expires_at=refresh_payload.exp)
    revoke_refresh_token(refresh_token)


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    user = crud.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    token_data = decode_token(token, expected_type="access")
    user = crud.get_user_by_id(db, token_data.user_id)
    if not user:
        raise_app_error(status.HTTP_401_UNAUTHORIZED, "AUTH_INVALID")
    return user


def require_roles(*roles: models.UserRole):
    def role_dependency(current_user: models.User = Depends(get_current_user)) -> models.User:
        if current_user.role not in roles:
            raise_app_error(status.HTTP_403_FORBIDDEN, "ACCESS_DENIED")
        return current_user

    return role_dependency
