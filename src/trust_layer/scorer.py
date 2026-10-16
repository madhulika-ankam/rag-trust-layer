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

# ── Aggregation rule ─────────────────────────────────────────────────────────
#
# How N per-claim scores become one answer score. Three rules, selectable:
#
#   "current"     mean(scores) x (1 - bad_fraction)
#                 The original. NO PUBLISHED PRECEDENT, and it penalises a
#                 bad claim TWICE — once by dragging the mean down, again
#                 through the penalty factor. With one bad claim out of n the
#                 score cannot exceed 1 - 1/n, so ANSWER (>=0.85) is
#                 unreachable at the 2-4 claims a typical answer produces.
#                 That ceiling is a large part of the 92% over-abstention
#                 measured on the 161-question benchmark.
#
#   "proportion"  supported / total
#                 This IS RAGAS faithfulness — "the proportion of claims in a
#                 response that can be inferred from the context". Note it is
#                 also exactly the penalty_factor above, used alone instead of
#                 as a multiplier.
#
#   "min"         the weakest claim decides
#                 SummaC-ZS style. Conservative, which suits a safety
#                 component.
#
# SELECTED: "min", measured against the 30 answers the author read and
# labelled herself, with the ESCALATE rule fixed to the one Step 3 chose.
# "Delivered" means ANSWER or WARN; the constraint is the one the plan set
# before any of this was run — at least 3 of the 4 answers containing
# fabrication must be withheld, and at most 1 of the 7 off-target answers
# delivered.
#
#     aggregator   deliver-at   good delivered   fabrication withheld
#     current         0.60          5/13                3/4
#     proportion      0.80          5/13                3/4
#     mean             any       never >5 within the constraint
#     min             0.30          6/13                3/4      <- this
#
# Three reasons beyond the single answer of difference, which on n=13 is not
# on its own worth acting on:
#
#   1. It is the rule that fixes what Step 4 is about. mean x (1 - bad) and
#      proportion are both BINARY when an answer has one claim — 0.000 or
#      the full score, nothing between. 23 of the 161 answers have exactly
#      one claim and 25 have none, so for 30% of the benchmark the formula
#      was a coin flip with no middle. "min" passes the claim's own score
#      through.
#   2. The original rule penalises a bad claim twice, once through the mean
#      and again through the factor, and has no published precedent. "min"
#      is SummaC-ZS's aggregation.
#   3. "An answer is only as trustworthy as its weakest claim" is the right
#      semantics for a safety component.
#
# KNOWN COST, to state in Chapter 6: "min" is the rule most sensitive to a
# single bad claim, so it is biased against LONG answers — one decomposer
# artefact in six claims sinks the answer. q100 (5 claims) and q114 (6) sit
# right on that line. If decomposition quality improves, revisit this.
AGGREGATOR = "min"


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


def _aggregate(per_claim_scores: list[float], verdicts: list[str],
               rule: str) -> float:
    """Combine per-claim scores into one answer score under the chosen rule."""
    n = len(per_claim_scores)
    if n == 0:
        return 0.0
    if rule == "proportion":
        return sum(1 for v in verdicts if v == "SUPPORTED") / n
    if rule == "min":
        return min(per_claim_scores)
    # "current" — the original double-penalising rule
    bad = sum(1 for v in verdicts if v in ("UNSUPPORTED", "CONTRADICTION"))
    return (sum(per_claim_scores) / n) * (1 - bad / n)


def score(results: list[VerificationResult],
          aggregator: str | None = None) -> TrustScore:
    """Combine per-claim verification results into one overall trust score."""
    num_claims = len(results)
    rule = aggregator or AGGREGATOR

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

    overall_score = _aggregate(per_claim_scores,
                               [r.verdict for r in results], rule)

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
