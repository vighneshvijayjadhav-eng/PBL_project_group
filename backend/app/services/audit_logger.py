from sqlalchemy.orm import Session

from app import crud, models


def log_event(
    db: Session,
    *,
    user_id: int,
    event_type: models.AuditEventType,
    entity_id: int,
    details: dict | None = None,
) -> None:
    crud.create_audit_log(
        db=db,
        user_id=user_id,
        event_type=event_type,
        entity_id=entity_id,
        details=details or {},
    )
