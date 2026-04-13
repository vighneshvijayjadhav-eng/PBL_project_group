from __future__ import annotations

from datetime import datetime, timezone


_revoked_tokens: dict[str, int] = {}


def revoke_token_jti(jti: str | None, *, expires_at: int) -> None:
    if not jti:
        return
    _revoked_tokens[jti] = expires_at


def is_token_revoked(jti: str | None) -> bool:
    if not jti:
        return False

    expires_at = _revoked_tokens.get(jti)
    if expires_at is None:
        return False

    now_ts = int(datetime.now(timezone.utc).timestamp())
    if expires_at < now_ts:
        _revoked_tokens.pop(jti, None)
        return False
    return True


def prune_revoked_tokens() -> None:
    now_ts = int(datetime.now(timezone.utc).timestamp())
    expired = [jti for jti, expires_at in _revoked_tokens.items() if expires_at < now_ts]
    for jti in expired:
        _revoked_tokens.pop(jti, None)
