from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.dependencies import build_response, get_current_user, get_db, require_roles


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me")
def get_me(request: Request, current_user: models.User = Depends(get_current_user)):
    return build_response(
        request,
        success=True,
        data={"user": schemas.UserOut.model_validate(current_user)},
        error=None,
    )


@router.get("")
def list_all_users(
    request: Request,
    _: models.User = Depends(require_roles(models.UserRole.admin)),
    db: Session = Depends(get_db),
):
    users = [schemas.UserOut.model_validate(user) for user in crud.list_users(db)]
    return build_response(request, success=True, data={"users": users}, error=None)
