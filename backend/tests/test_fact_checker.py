import pytest
from backend.services.fact_checker import _claim_matches


def test_claim_matches_exact():
    assert _claim_matches("vaccine causes autism", "vaccine causes autism") is True


def test_claim_matches_partial():
    assert _claim_matches(
        "vaccine causes autism in children",
        "vaccine causes autism"
    ) is True


def test_claim_matches_no_overlap():
    assert _claim_matches(
        "5G towers cause health problems",
        "vaccine causes autism"
    ) is False


def test_claim_matches_boundary():
    assert _claim_matches("stock market rises", "stock market falls") is False
