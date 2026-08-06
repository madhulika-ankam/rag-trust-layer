"""
Tests for Module 5: Confidence Scorer.

Uses synthetic VerificationResult objects directly — scorer.score() only
aggregates verdicts/scores, so no models are needed here.

Run with:
    source venv/bin/activate
    pytest tests/test_scorer.py -v
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trust_layer.verifier import VerificationResult
from src.trust_layer.scorer import score


def _result(verdict, claim_score, claim="claim"):
    return VerificationResult(
        claim=claim,
        verdict=verdict,
        score=claim_score,
        best_chunk="chunk text",
        best_chunk_source="manual.pdf p.1",
    )


def test_all_supported_claims_score_high():
    results = [
        _result("SUPPORTED", 0.95),
        _result("SUPPORTED", 0.90),
        _result("SUPPORTED", 0.88),
    ]

    trust = score(results)

    assert trust.penalty_factor == 1.0
    assert trust.overall_score == trust.mean_claim_score
    assert trust.has_contradiction is False
    assert trust.num_supported == 3


def test_one_contradiction_among_strong_claims_pulls_score_down():
    # From the design discussion: [0.95, 0.90, 0.10] with the last being a
    # contradiction should land around 0.43, not the plain mean of 0.65.
    results = [
        _result("SUPPORTED", 0.95),
        _result("SUPPORTED", 0.90),
        _result("CONTRADICTION", 0.10),
    ]

    trust = score(results)

    assert trust.mean_claim_score == round((0.95 + 0.90 + 0.10) / 3, 4)
    assert trust.penalty_factor == round(1 - (1 / 3), 4)
    assert trust.overall_score < trust.mean_claim_score
    assert 0.40 <= trust.overall_score <= 0.45
    assert trust.has_contradiction is True


def test_plain_mean_would_mislead_but_weighted_score_does_not():
    # Confirms the whole point of the weighting: a plain average of these
    # scores clears the WARN threshold (0.60), the weighted score does not.
    results = [
        _result("SUPPORTED", 0.95),
        _result("SUPPORTED", 0.90),
        _result("CONTRADICTION", 0.10),
    ]

    trust = score(results)

    assert trust.mean_claim_score >= 0.60
    assert trust.overall_score < 0.60


def test_all_unsupported_claims_score_zero():
    results = [
        _result("UNSUPPORTED", 0.0),
        _result("UNSUPPORTED", 0.0),
    ]

    trust = score(results)

    assert trust.overall_score == 0.0
    assert trust.penalty_factor == 0.0
    assert trust.has_contradiction is False


def test_empty_results_returns_zero_score_without_error():
    trust = score([])

    assert trust.overall_score == 0.0
    assert trust.num_claims == 0
    assert trust.has_contradiction is False


def test_counts_match_verdicts():
    results = [
        _result("SUPPORTED", 0.9),
        _result("SUPPORTED", 0.85),
        _result("UNSUPPORTED", 0.2),
        _result("CONTRADICTION", 0.0),
    ]

    trust = score(results)

    assert trust.num_claims == 4
    assert trust.num_supported == 2
    assert trust.num_unsupported == 1
    assert trust.num_contradiction == 1
    assert trust.per_claim_scores == [0.9, 0.85, 0.2, 0.0]
