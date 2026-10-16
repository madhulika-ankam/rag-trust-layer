"""
Module 4: Query Coverage Check

Asks whether the generated answer actually ADDRESSES the question, which is a
different question from whether it is grounded. The two come apart constantly:

    Q: "What are the spindle speed ranges?"
    A: "The gear case oil should be changed twice a year."

    every word of that is in the retrieved evidence  -> grounded
    it does not answer the question                  -> useless

Module 3 cannot see this. It checks each claim against the chunks, and an
answer faithful to irrelevant evidence passes every check. Measured on 30
hand-labelled answers, 8 were grounded but off-target, and lowering the
decision threshold admitted them at the same rate as good answers — because
to a groundedness score they are indistinguishable. No threshold fixes that;
only a different signal does.

MULTI-PART QUESTIONS
    Support decays sharply across a two-part answer: 35% of claims
    unsupported in the first third, 70% in the middle. Retrieval serves the
    first sub-question, the model answers it well, then elaborates on nothing
    — and never declines (0 of 15 multi-part questions were declined, against
    16% of single-part). So each sub-question is scored separately and the
    MINIMUM is what matters: answering one half well must not mask ignoring
    the other.

RELATION TO PUBLISHED METRICS
    This is RAGAS's `answer_relevancy` in cheap form. RAGAS generates
    candidate questions from the answer and compares them to the original;
    here the answer is compared to the question directly, reusing the
    embedding model already loaded for Module 1. Cite RAGAS for the
    construct, not for this implementation.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from src.trust_layer.verifier import _semantic_similarity

# Below this, the answer is treated as not addressing (that part of) the
# question. Provisional — derive it on the validation split the same way the
# decision thresholds are derived, rather than leaving it chosen.
RELEVANCE_THRESHOLD = 0.35

_MIN_SUBQ_CHARS = 15

# Splits a question into the parts it is actually asking. Conjunctions only
# count when they introduce a new interrogative, so "nuts and bolts" stays
# whole while "what is X, and how do I Y" does not.
_SUBQ_SPLIT = re.compile(
    r"(?<=\?)\s+|"
    r",?\s+and\s+(?=(?:how|what|why|when|where|which|who|is|are|do|does|can|should|will)\b)",
    re.IGNORECASE,
)


@dataclass
class RelevanceResult:
    relevant: bool
    score: float               # the MINIMUM across sub-questions
    per_subquestion: list[tuple[str, float]]
    detail: str


def split_question(question: str) -> list[str]:
    """Split a question into its sub-questions; a single-part question
    returns one element."""
    q = " ".join(question.split())
    parts = [p.strip() for p in _SUBQ_SPLIT.split(q) if p and p.strip()]
    parts = [p for p in parts if len(p) >= _MIN_SUBQ_CHARS]
    return parts or [q]


def check_relevance(question: str, answer: str,
                    threshold: float | None = None) -> RelevanceResult:
    """Does this answer address this question, in all of its parts?"""
    t = RELEVANCE_THRESHOLD if threshold is None else threshold

    if not answer.strip():
        return RelevanceResult(False, 0.0, [], "empty answer")

    subs = split_question(question)
    scored = [(s, _semantic_similarity(s, answer)) for s in subs]
    worst_q, worst = min(scored, key=lambda x: x[1])

    if len(scored) > 1:
        detail = (f"{len(scored)} sub-questions; weakest scores {worst:.3f} "
                  f"({worst_q[:60]!r})")
    else:
        detail = f"question-answer similarity {worst:.3f}"

    return RelevanceResult(relevant=worst >= t, score=worst,
                           per_subquestion=scored, detail=detail)
