from __future__ import annotations

from collections import defaultdict, deque
from time import time


_request_windows: dict[str, deque[float]] = defaultdict(deque)


def is_rate_limited(key: str, *, limit: int, window_seconds: int) -> bool:
    now = time()
    window = _request_windows[key]

    while window and now - window[0] > window_seconds:
        window.popleft()

    if len(window) >= limit:
        return True

    window.append(now)
    return False
