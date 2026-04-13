FEATURE_ORDER = [
    "claim_amount",
    "policy_tenure_months",
    "premium_to_claim_ratio",
    "previous_claims_count",
    "previous_fraud_flag",
    "incident_severity",
    "hospitalization_required",
    "police_report_filed",
    "document_count",
    "claim_submission_delay_days",
    "claimant_age",
    "claimant_gender",
    "claimant_location",
]

BOOLEAN_FEATURES = [
    "previous_fraud_flag",
    "hospitalization_required",
    "police_report_filed",
]

ORDINAL_MAPPINGS = {
    "incident_severity": {"low": 0, "medium": 1, "high": 2},
}

CATEGORICAL_FEATURES = [
    "claimant_gender",
    "incident_severity",
    "claimant_location",
]

TARGET_COLUMN = "fraud_label"
