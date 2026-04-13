# Module Explanation

## Backend

- `app/main.py`: app bootstrap, middleware, structured logging, global exception handling, and rate limiting.
- `app/dependencies.py`: JWT handling, password hashing, role enforcement, response wrapping, and token lifecycle helpers.
- `app/routers/`: request-only route handlers for auth, claims, policies, users, and system health.
- `app/services/`: business logic, audit logging, risk integration, health checks, token revocation, and rate limiting.
- `app/models.py`: SQLAlchemy ORM models aligned with the insurance contract.
- `app/schemas/`: Pydantic models for validation and response serialization.

## Frontend

- `src/api/`: Axios client, auth calls, and claim API integration.
- `src/context/AuthContext.jsx`: session state, decoded JWT user info, and logout handling.
- `src/context/ToastContext.jsx`: lightweight toast notification system.
- `src/pages/`: login, claim submission, claim dashboard, and admin dashboard.
- `src/components/`: table, filters, pagination, charts, health banner, protected routes, and loading skeletons.

## Risk Engine

- `risk_engine/rule_engine.py`: deterministic fraud heuristics.
- `risk_engine/ml_model.py`: artifact-backed ML inference with strict schema validation.
- `risk_engine/scorer.py`: combines rule-based and ML scores into the final fraud score and risk level.

## Viva / Demo Narrative

1. User logs in and receives access and refresh tokens.
2. A claim is submitted and persisted through the service layer.
3. The risk engine scores the claim using both rule-based and ML pipelines.
4. The user dashboard displays claim outcomes and summary metrics.
5. The admin dashboard filters, paginates, and visualizes claim risk across the system.
6. If the access token expires, the frontend silently refreshes it and retries the request.
