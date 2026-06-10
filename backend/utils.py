import time
import hashlib
import logging
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def rate_limit(calls: int, period: float):
    """Simple rate limiter decorator."""
    times: list[float] = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            times[:] = [t for t in times if now - t < period]
            if len(times) >= calls:
                sleep_time = period - (now - times[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
            times.append(time.time())
            return func(*args, **kwargs)

        return wrapper

    return decorator


def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1} failed: {e}. Retrying..."
                    )
                    time.sleep(delay * (2**attempt))
            return None

        return wrapper

    return decorator


def safe_get(d: dict, *keys: str, default: Any = None) -> Any:
    """Safely get nested dict value."""
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d if d is not None else default
