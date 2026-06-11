import pytest
from .utils import url_hash, safe_get, retry, rate_limit
import time


def test_url_hash_deterministic():
    h1 = url_hash("https://vnexpress.net/test")
    h2 = url_hash("https://vnexpress.net/test")
    assert h1 == h2
    assert len(h1) == 16


def test_url_hash_different_urls():
    h1 = url_hash("https://vnexpress.net/a")
    h2 = url_hash("https://vnexpress.net/b")
    assert h1 != h2


def test_safe_get_nested():
    d = {"a": {"b": {"c": 42}}}
    assert safe_get(d, "a", "b", "c") == 42
    assert safe_get(d, "a", "x", "c", default=0) == 0
    assert safe_get({}, "a", default="missing") == "missing"


def test_retry_success():
    @retry(max_attempts=3, delay=0.1)
    def succeed():
        return "ok"

    assert succeed() == "ok"


def test_retry_fails_after_attempts():
    attempts = 0

    @retry(max_attempts=2, delay=0.05)
    def fail():
        nonlocal attempts
        attempts += 1
        raise ValueError("test error")

    with pytest.raises(ValueError):
        fail()
    assert attempts == 2


def test_rate_limit():
    calls = []

    @rate_limit(calls=3, period=0.5)
    def make_call():
        calls.append(time.time())
        return "ok"

    make_call()
    make_call()
    make_call()
    start = time.time()
    make_call()
    elapsed = time.time() - start
    assert elapsed >= 0.4
