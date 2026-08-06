"""
Tests for Module 6: Decision Module.

Builds TrustScore objects directly — decide() only reads overall_score,
has_contradiction, num_claims, num_unsupported, and num_contradiction, so no
models or verifier calls are needed here.

Run with:
    source venv/bin/activate
    pytest tests/test_decision.py -v
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trust_layer.scorer import TrustScore
from src.trust_layer.decision import decide


def _trust(overall_score, has_contradiction=False, num_claims=3,
           num_unsupported=0, num_contradiction=0):
    return TrustScore(
        overall_score=overall_score,
        mean_claim_score=overall_score,
        penalty_factor=1.0,
        num_claims=num_claims,
        num_supported=num_claims - num_unsupported - num_contradiction,
        num_unsupported=num_unsupported,
        num_contradiction=num_contradiction,
        has_contradiction=has_contradiction,
        per_claim_scores=[overall_score] * num_claims,
    )


def test_high_score_no_contradiction_answers():
    result = decide(_trust(0.90))
    assert result.decision == "ANSWER"


def test_score_exactly_at_answer_threshold_answers():
    result = decide(_trust(0.85))
    assert result.decision == "ANSWER"


def test_score_just_below_answer_threshold_warns():
    result = decide(_trust(0.84))
    assert result.decision == "WARN"


def test_mid_score_warns():
    result = decide(_trust(0.70, num_unsupported=1))
    assert result.decision == "WARN"


def test_score_exactly_at_warn_threshold_warns():
    result = decide(_trust(0.60))
    assert result.decision == "WARN"


def test_score_just_below_warn_threshold_refuses():
    result = decide(_trust(0.59))
    assert result.decision == "REFUSE"


def test_low_score_refuses():
    result = decide(_trust(0.20))
    assert result.decision == "REFUSE"


def test_contradiction_escalates_even_with_high_overall_score():
    # A contradiction hiding in one claim shouldn't be masked by a strong
    # overall score from the rest — ESCALATE must take precedence.
    result = decide(_trust(0.90, has_contradiction=True, num_contradiction=1))
    assert result.decision == "ESCALATE"


def test_contradiction_escalates_over_low_score_too():
    result = decide(_trust(0.10, has_contradiction=True, num_contradiction=1))
    assert result.decision == "ESCALATE"


def test_no_claims_refuses():
    result = decide(_trust(0.0, num_claims=0))
    assert result.decision == "REFUSE"
    assert "no claims" in result.reason


def test_reason_is_populated_for_every_decision():
    for trust in [
        _trust(0.90),
        _trust(0.70),
        _trust(0.20),
        _trust(0.90, has_contradiction=True, num_contradiction=1),
    ]:
        result = decide(trust)
        assert result.reason
        assert result.overall_score == trust.overall_score
