# API Documentation Summary

## Authentication

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`

Login returns an access token and refresh token inside the standard response wrapper. Access tokens carry `user_id`, `email`, `role`, `exp`, `type`, and `jti`.

## Claims

- `GET /claims`
- `GET /claims/summary`
- `GET /claims/{claim_id}`
- `POST /claims`
- `PATCH /claims/{claim_id}/status`
- `PATCH /claims/{claim_id}/assign`

List endpoints include pagination metadata under `meta.pagination`. Summary returns:

- `total_claims`
- `avg_risk_score`
- `high_risk_percentage`

## Admin

- `GET /admin/claims`

Supports filters for:

- `status`
- `risk_level`
- `min_risk_score`
- `max_risk_score`
- `page`
- `limit`

## System

- `GET /system/health`

Returns:

- `database`
- `risk_engine`
- `ml_model_loaded`
- `auth_system`
- `api_latency_ms`

## Response Wrapper

All APIs return:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "timestamp": "2026-04-10T12:00:00Z",
    "request_id": "uuid",
    "pagination": null
  }
}
```
