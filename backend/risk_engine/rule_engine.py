from decimal import Decimal

from risk_engine.schemas import ClaimRiskInput


def _bounded(score: float) -> float:
    return max(0.0, min(1.0, round(score, 4)))


def compute_rule_score(payload: ClaimRiskInput) -> float:
    score = Decimal("0.0")
    score += min(payload.claim_amount / Decimal("100000"), Decimal("0.25"))
    score += min(Decimal(payload.previous_claims_count) * Decimal("0.05"), Decimal("0.15"))
    score += Decimal("0.20") if payload.previous_fraud_flag else Decimal("0.0")
    score += {"low": Decimal("0.05"), "medium": Decimal("0.12"), "high": Decimal("0.20")}[
        payload.incident_severity
    ]
    score += Decimal("0.05") if payload.hospitalization_required else Decimal("0.0")
    score += Decimal("0.05") if not payload.police_report_filed else Decimal("0.0")
    score += min(Decimal(payload.claim_submission_delay_days) / Decimal("100"), Decimal("0.10"))
    score += Decimal("0.05") if payload.document_count == 0 else Decimal("0.0")
    score += Decimal("0.05") if payload.premium_to_claim_ratio < Decimal("1.0") else Decimal("0.0")
    return _bounded(float(score))
