from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.dependencies import build_response, get_db, raise_app_error
from app.services.system_service import get_system_health


router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
def system_health(request: Request, db: Session = Depends(get_db)):
    try:
        health = get_system_health(db)
    except FileNotFoundError as exc:
        raise_app_error(503, "RISK_ENGINE_UNAVAILABLE", details={"artifact": str(exc)})
    except ValueError as exc:
        code = str(exc) if str(exc) in {"FEATURE_MISSING", "MODEL_INPUT_INVALID", "SCHEMA_MISMATCH"} else "INTERNAL_ERROR"
        raise_app_error(500 if code == "SCHEMA_MISMATCH" else 400, code)

    return build_response(
        request,
        success=True,
        data=health,
        error=None,
    )
