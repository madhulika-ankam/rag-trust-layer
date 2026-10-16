"""
Module 6: Decision Module

Applies the ANSWER/WARN/REFUSE/ESCALATE thresholds to the overall TrustScore
from Module 5.

  ESCALATE  → any contradiction found, safety critical (checked first —
              overrides the score thresholds below, since one contradicted
              claim is dangerous regardless of how well everything else
              scored)
  ANSWER    → score >= 0.85, fully supported
  WARN      → 0.30 <= score < 0.85, partially supported
  REFUSE    → score < 0.30, insufficient support (also applies when there
              were no claims to verify at all)
"""
from dataclasses import dataclass

from src.trust_layer.scorer import TrustScore

ANSWER_THRESHOLD = 0.85

# 0.60 was carried over from the "current" aggregator, where the score was
# mean(claim scores) x (1 - bad fraction). Module 5 now aggregates with
# "min", so the score means "every claim scored at least this" — a different
# quantity on a different scale, and the old number does not transfer.
#
# Swept from 0.05 to 0.95 against the 30 labelled answers under the plan's
# constraint (>=3 of 4 fabrication answers withheld, <=1 of 7 off-target
# delivered). 0.25, 0.30 and 0.35 all give the same result — 6 of 13
# fully-good answers delivered — so this is the centre of the stable region
# rather than an edge of it.
#
# THIS IS SELECTED ON 30 ANSWERS, which is small enough that the difference
# between it and the old setting is a single question. It needs revisiting
# once Dr. Morkos has validated more labels; src/calibrate.py derives it
# from a stated risk tolerance instead.
WARN_THRESHOLD = 0.30


@dataclass
class Decision:
    decision: str  # ANSWER | WARN | REFUSE | ESCALATE
    reason: str
    overall_score: float


def decide(trust: TrustScore) -> Decision:
    """Turn a TrustScore into a final ANSWER/WARN/REFUSE/ESCALATE decision."""
    if trust.num_claims == 0:
        return Decision(
            decision="REFUSE",
            reason="no claims to verify",
            overall_score=trust.overall_score,
        )

    if trust.has_contradiction:
        return Decision(
            decision="ESCALATE",
            reason=(
                f"{trust.num_contradiction} claim(s) contradict retrieved "
                "evidence — safety critical"
            ),
            overall_score=trust.overall_score,
        )

    if trust.overall_score >= ANSWER_THRESHOLD:
        return Decision(
            decision="ANSWER",
            reason=f"fully supported (score={trust.overall_score:.2f})",
            overall_score=trust.overall_score,
        )

    if trust.overall_score >= WARN_THRESHOLD:
        return Decision(
            decision="WARN",
            reason=(
                f"partially supported (score={trust.overall_score:.2f}, "
                f"{trust.num_unsupported} unsupported claim(s))"
            ),
            overall_score=trust.overall_score,
        )

    return Decision(
        decision="REFUSE",
        reason=f"insufficient support (score={trust.overall_score:.2f})",
        overall_score=trust.overall_score,
    )
