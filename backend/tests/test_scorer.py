import pytest
from backend.services.scorer import calculate_score, _calc_source_reputation, _calc_claim_consistency, _calc_amplification_pattern


def test_source_reputation_vnexpress():
    score = _calc_source_reputation({"source": "vnexpress.net"})
    assert score == 8.0


def test_source_reputation_unknown():
    score = _calc_source_reputation({"source": "unknown-site.com"})
    assert score == 5.0


def test_claim_consistency_all_verified():
    fact_checks = [
        {"status": "verified"},
        {"status": "verified"},
        {"status": "verified"},
    ]
    score = _calc_claim_consistency([], fact_checks)
    assert score == 10.0


def test_claim_consistency_mixed():
    fact_checks = [
        {"status": "verified"},
        {"status": "unverified"},
        {"status": "false"},
    ]
    score = _calc_claim_consistency([], fact_checks)
    assert score == pytest.approx(5.33,0.1)


def test_amplification_pattern_no_low_trust():
    propagation = {
        "timeline": [
            {"source_domain": "vnexpress.net"},
            {"source_domain": "dantri.com.vn"},
        ]
    }
    score = _calc_amplification_pattern(propagation)
    assert score == 7.0


def test_calculate_score_full():
    article = {"source": "vnexpress.net"}
    claims = [{"id": 1, "text": "test claim"}]
    propagation = {"timeline": []}
    fact_checks = [{"status": "verified"}]

    result = calculate_score(article, claims, propagation, fact_checks)

    assert "total" in result
    assert "breakdown" in result
    assert result["breakdown"]["source_reputation"] == 8.0
    assert result["breakdown"]["claim_consistency"] == 10.0
    assert 0 <= result["total"] <= 10
