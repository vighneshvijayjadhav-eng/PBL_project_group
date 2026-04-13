import time
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app import models, schemas
from risk_engine.feature_config import FEATURE_ORDER
from risk_engine.ml_model import (
    load_model,
    load_scaler,
    load_encoders,
    load_feature_order,
    predict,
)
from risk_engine.schemas import ClaimRiskInput


def _claim_model_fields() -> set[str]:
    return {column.name for column in models.Claim.__table__.columns}


def _claim_schema_fields() -> set[str]:
    return set(schemas.ClaimSubmitResponse.model_fields.keys())


def _dummy_claim() -> ClaimRiskInput:
    return ClaimRiskInput(
        claim_id=5001,
        policy_id=101,
        claimant_id=1,
        adjuster_id=None,
        claim_type="accident",
        incident_date=datetime.now(timezone.utc),
        claim_amount=Decimal("15000.00"),
        claim_status="submitted",
        description="Rear-end collision",
        claimant_age=35,
        claimant_gender="male",
        claimant_location="Pune",
        policy_tenure_months=24,
        premium_to_claim_ratio=Decimal("1.20"),
        previous_claims_count=2,
        previous_fraud_flag=False,
        incident_severity="medium",
        hospitalization_required=True,
        police_report_filed=True,
        document_count=3,
        claim_submission_delay_days=5,
        created_at=datetime.now(timezone.utc),
    )


def get_system_health(db: Session) -> dict:
    start_time = time.perf_counter()
    db.execute(text("SELECT 1"))

    model_bundle = load_model()
    load_scaler()
    load_encoders()
    load_feature_order()
    dummy_claim = _dummy_claim()
    predict(dummy_claim)

    schema_sync = (
        _claim_schema_fields().issubset(_claim_model_fields())
        and set(FEATURE_ORDER).issubset(_claim_model_fields())
        and model_bundle["feature_order"] == FEATURE_ORDER
    )
    if not schema_sync:
        raise ValueError("SCHEMA_MISMATCH")
    api_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "database": "ok",
        "risk_engine": "ok",
        "ml_model_loaded": True,
        "auth_system": "ok" if settings.secret_key and settings.algorithm else "failed",
        "api_latency_ms": api_latency_ms,
    }
