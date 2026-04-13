from __future__ import annotations

import hashlib
from datetime import datetime, timezone


_refresh_tokens: dict[str, dict[str, int]] = {}


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def store_refresh_token(token: str, *, user_id: int, expires_at: int) -> None:
    _refresh_tokens[_hash_token(token)] = {"user_id": user_id, "expires_at": expires_at}


def is_refresh_token_active(token: str, *, user_id: int) -> bool:
    token_hash = _hash_token(token)
    record = _refresh_tokens.get(token_hash)
    if not record:
        return False

    now_ts = int(datetime.now(timezone.utc).timestamp())
    if record["user_id"] != user_id or record["expires_at"] < now_ts:
        _refresh_tokens.pop(token_hash, None)
        return False

    return True


def revoke_refresh_token(token: str) -> None:
    _refresh_tokens.pop(_hash_token(token), None)


def prune_expired_refresh_tokens() -> None:
    now_ts = int(datetime.now(timezone.utc).timestamp())
    expired = [
        token_hash
        for token_hash, record in _refresh_tokens.items()
        if record["expires_at"] < now_ts
    ]
    for token_hash in expired:
        _refresh_tokens.pop(token_hash, None)
