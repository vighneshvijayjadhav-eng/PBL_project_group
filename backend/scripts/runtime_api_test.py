import json
import os
from datetime import datetime, timezone

import requests


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
TOKEN = os.getenv("API_TOKEN", "")


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers


def main() -> None:
    health_response = requests.get(f"{BASE_URL}/system/health", timeout=30)
    print("GET /system/health")
    print(json.dumps(health_response.json(), indent=2))

    claim_payload = {
        "policy_id": int(os.getenv("TEST_POLICY_ID", "101")),
        "claim_type": os.getenv("TEST_CLAIM_TYPE", "accident"),
        "incident_date": datetime.now(timezone.utc).isoformat(),
        "claim_amount": os.getenv("TEST_CLAIM_AMOUNT", "15000.00"),
        "description": os.getenv("TEST_DESCRIPTION", "Rear-end collision"),
        "claimant_age": int(os.getenv("TEST_CLAIMANT_AGE", "35")),
        "claimant_gender": os.getenv("TEST_CLAIMANT_GENDER", "male"),
        "claimant_location": os.getenv("TEST_CLAIMANT_LOCATION", "Pune"),
        "policy_tenure_months": int(os.getenv("TEST_POLICY_TENURE_MONTHS", "24")),
        "premium_to_claim_ratio": os.getenv("TEST_PREMIUM_TO_CLAIM_RATIO", "1.20"),
        "previous_claims_count": int(os.getenv("TEST_PREVIOUS_CLAIMS_COUNT", "2")),
        "previous_fraud_flag": os.getenv("TEST_PREVIOUS_FRAUD_FLAG", "false").lower() == "true",
        "incident_severity": os.getenv("TEST_INCIDENT_SEVERITY", "medium"),
        "hospitalization_required": os.getenv("TEST_HOSPITALIZATION_REQUIRED", "true").lower() == "true",
        "police_report_filed": os.getenv("TEST_POLICE_REPORT_FILED", "true").lower() == "true",
        "document_count": int(os.getenv("TEST_DOCUMENT_COUNT", "3")),
        "claim_submission_delay_days": int(os.getenv("TEST_CLAIM_SUBMISSION_DELAY_DAYS", "5")),
    }
    claim_response = requests.post(
        f"{BASE_URL}/claims/",
        json=claim_payload,
        headers=_headers(),
        timeout=30,
    )
    print("POST /claims/")
    print(json.dumps(claim_response.json(), indent=2))


if __name__ == "__main__":
    main()
