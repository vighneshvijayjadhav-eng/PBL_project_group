from typing import Iterable

from sqlalchemy.orm import Session

from app import models, schemas


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def list_users(db: Session) -> Iterable[models.User]:
    return db.query(models.User).order_by(models.User.user_id.asc()).all()


def create_user(db: Session, user_in: schemas.UserCreate, hashed_password: str) -> models.User:
    user = models.User(
        name=user_in.name,
        email=user_in.email,
        role=user_in.role,
        hashed_password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_policy_by_id(db: Session, policy_id: int) -> models.Policy | None:
    return db.query(models.Policy).filter(models.Policy.policy_id == policy_id).first()


def list_policies(db: Session, user: models.User) -> Iterable[models.Policy]:
    query = db.query(models.Policy).order_by(models.Policy.policy_id.asc())
    if user.role == models.UserRole.admin:
        return query.all()
    return query.filter(models.Policy.user_id == user.user_id).all()


def create_policy(db: Session, policy_in: schemas.PolicyCreate) -> models.Policy:
    policy = models.Policy(**policy_in.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def update_policy(db: Session, policy: models.Policy, policy_in: schemas.PolicyUpdate) -> models.Policy:
    for field, value in policy_in.model_dump(exclude_none=True).items():
        setattr(policy, field, value)
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def delete_policy(db: Session, policy: models.Policy) -> None:
    db.delete(policy)
    db.commit()


def get_claim_by_id(db: Session, claim_id: int) -> models.Claim | None:
    return db.query(models.Claim).filter(models.Claim.claim_id == claim_id).first()


def list_claims(db: Session, user: models.User) -> Iterable[models.Claim]:
    query = db.query(models.Claim).order_by(models.Claim.claim_id.desc())
    if user.role == models.UserRole.admin:
        return query.all()
    if user.role == models.UserRole.adjuster:
        return query.filter(models.Claim.adjuster_id == user.user_id).all()
    return query.filter(models.Claim.claimant_id == user.user_id).all()


def create_claim(db: Session, claim_in: schemas.ClaimCreate, claimant_id: int) -> models.Claim:
    claim = models.Claim(
        policy_id=claim_in.policy_id,
        claimant_id=claimant_id,
        claim_type=claim_in.claim_type,
        incident_date=claim_in.incident_date,
        claim_amount=claim_in.claim_amount,
        claim_status=models.ClaimStatus.submitted,
        description=claim_in.description,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def update_claim_scores(
    db: Session, claim: models.Claim, scores: schemas.RiskScoreResponse
) -> models.Claim:
    claim.rule_score = scores.rule_score
    claim.ml_score = scores.ml_score
    claim.final_risk_score = scores.final_risk_score
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def update_claim(db: Session, claim: models.Claim, claim_in: schemas.ClaimUpdate) -> models.Claim:
    for field, value in claim_in.model_dump(exclude_none=True).items():
        setattr(claim, field, value)
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def assign_claim(db: Session, claim: models.Claim, adjuster_id: int) -> models.Claim:
    claim.adjuster_id = adjuster_id
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def create_audit_log(
    db: Session,
    user_id: int,
    event_type: models.AuditEventType,
    entity_id: int,
    details: dict,
) -> models.AuditLog:
    log = models.AuditLog(
        user_id=user_id,
        event_type=event_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
