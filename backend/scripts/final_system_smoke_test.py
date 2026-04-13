import os
from datetime import datetime, timedelta, timezone

import requests


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
USER_EMAIL = os.getenv("TEST_USER_EMAIL", "policyholder@example.com")
USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "ChangeMe123!")
ADMIN_EMAIL = os.getenv("TEST_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "ChangeMe123!")
TEST_POLICY_ID = int(os.getenv("TEST_POLICY_ID", "1"))


def unwrap(response):
    response.raise_for_status()
    body = response.json()
    if not body.get("success"):
        raise RuntimeError(body)
    return body["data"]


def login(email: str, password: str) -> dict:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password},
        timeout=15,
    )
    return unwrap(response)


def logout(access_token: str, refresh_token: str) -> dict:
    response = requests.post(
        f"{BASE_URL}/api/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    return unwrap(response)


def run() -> None:
    user_session = login(USER_EMAIL, USER_PASSWORD)
    user_headers = {"Authorization": f"Bearer {user_session['access_token']}"}

    health = unwrap(requests.get(f"{BASE_URL}/system/health", timeout=15))
    print("Health:", health)

    claim_payload = {
        "policy_id": TEST_POLICY_ID,
        "claim_type": "accident",
        "incident_date": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
        "claim_amount": "12000.00",
        "description": "Final smoke test collision claim",
        "claimant_age": 33,
        "claimant_gender": "male",
        "claimant_location": "Pune",
        "policy_tenure_months": 18,
        "premium_to_claim_ratio": "1.25",
        "previous_claims_count": 1,
        "previous_fraud_flag": False,
        "incident_severity": "medium",
        "hospitalization_required": False,
        "police_report_filed": True,
        "document_count": 3,
        "claim_submission_delay_days": 2,
    }
    created_claim = unwrap(
        requests.post(f"{BASE_URL}/claims", json=claim_payload, headers=user_headers, timeout=20)
    )
    print("Created claim:", created_claim["claim_id"])

    summary = unwrap(requests.get(f"{BASE_URL}/claims/summary", headers=user_headers, timeout=15))
    print("User summary:", summary)

    refreshed = unwrap(
        requests.post(
            f"{BASE_URL}/api/auth/refresh",
            json={"refresh_token": user_session["refresh_token"]},
            timeout=15,
        )
    )
    print("Refresh issued new access token:", bool(refreshed["access_token"]))

    admin_session = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    admin_headers = {"Authorization": f"Bearer {admin_session['access_token']}"}
    admin_claims = unwrap(requests.get(f"{BASE_URL}/admin/claims", headers=admin_headers, timeout=15))
    print("Admin claim count:", len(admin_claims["claims"]))

    logout_result = logout(admin_session["access_token"], admin_session["refresh_token"])
    print("Admin logout:", logout_result["message"])


if __name__ == "__main__":
    run()
