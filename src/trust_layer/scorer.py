"""
Module 5: Confidence Scorer

Combines the per-claim VerificationResults from Module 3 into a single
overall trust score for the answer.

Aggregation: mean of per-claim scores, multiplied down by a penalty based on
the fraction of claims that are UNSUPPORTED or CONTRADICTION. A plain mean
would let a few strong claims mask one dangerous unsupported claim; the
penalty factor keeps bad claims from hiding in the average.

    overall_score = mean(claim_scores) * (1 - bad_claim_fraction)

Module 6 (Decision) applies the ANSWER/WARN/REFUSE/ESCALATE thresholds to
overall_score, and uses has_contradiction directly for the ESCALATE rule
(any contradiction is safety-critical regardless of overall_score).
"""
from dataclasses import dataclass, field

from src.trust_layer.verifier import VerificationResult


@dataclass
class TrustScore:
    overall_score: float
    mean_claim_score: float
    penalty_factor: float
    num_claims: int
    num_supported: int
    num_unsupported: int
    num_contradiction: int
    has_contradiction: bool
    per_claim_scores: list[float] = field(default_factory=list)


def score(results: list[VerificationResult]) -> TrustScore:
    """Combine per-claim verification results into one overall trust score."""
    num_claims = len(results)

    if num_claims == 0:
        return TrustScore(
            overall_score=0.0,
            mean_claim_score=0.0,
            penalty_factor=0.0,
            num_claims=0,
            num_supported=0,
            num_unsupported=0,
            num_contradiction=0,
            has_contradiction=False,
            per_claim_scores=[],
        )

    num_supported = sum(1 for r in results if r.verdict == "SUPPORTED")
    num_unsupported = sum(1 for r in results if r.verdict == "UNSUPPORTED")
    num_contradiction = sum(1 for r in results if r.verdict == "CONTRADICTION")

    per_claim_scores = [r.score for r in results]
    mean_claim_score = sum(per_claim_scores) / num_claims

    bad_claim_fraction = (num_unsupported + num_contradiction) / num_claims
    penalty_factor = 1.0 - bad_claim_fraction

    overall_score = mean_claim_score * penalty_factor

    return TrustScore(
        overall_score=round(overall_score, 4),
        mean_claim_score=round(mean_claim_score, 4),
        penalty_factor=round(penalty_factor, 4),
        num_claims=num_claims,
        num_supported=num_supported,
        num_unsupported=num_unsupported,
        num_contradiction=num_contradiction,
        has_contradiction=num_contradiction > 0,
        per_claim_scores=per_claim_scores,
    )
