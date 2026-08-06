"""
Module 7: Transparency Report Generator

Takes the outputs of Modules 3, 5, and 6 (per-claim verification results,
overall trust score, and final decision) and produces a TrustReport with
three layers:

  Layer 1 — Trust Score:            machine-readable score/decision/counts
  Layer 2 — Citation Trail:         per-claim verdict, score, and source
  Layer 3 — Natural Language:       a human-readable explanation of why
"""
from dataclasses import dataclass, field

from src.trust_layer.decision import Decision
from src.trust_layer.scorer import TrustScore
from src.trust_layer.verifier import VerificationResult

_SNIPPET_MAX_LEN = 160


@dataclass
class Citation:
    claim: str
    verdict: str
    score: float
    source: str
    evidence_snippet: str


@dataclass
class TrustReport:
    query: str
    answer: str
    decision: str  # ANSWER | WARN | REFUSE | ESCALATE
    reason: str
    overall_score: float
    num_claims: int
    num_supported: int
    num_unsupported: int
    num_contradiction: int
    explanation: str
    citations: list[Citation] = field(default_factory=list)


def _snippet(text: str, max_len: int = _SNIPPET_MAX_LEN) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."


def _build_citations(results: list[VerificationResult]) -> list[Citation]:
    return [
        Citation(
            claim=r.claim,
            verdict=r.verdict,
            score=r.score,
            source=r.best_chunk_source,
            evidence_snippet=_snippet(r.best_chunk),
        )
        for r in results
    ]


def _explain(decision: Decision, trust: TrustScore,
             results: list[VerificationResult]) -> str:
    if decision.decision == "ANSWER":
        return (
            f"All {trust.num_claims} claim(s) in this answer are supported "
            f"by the retrieved documentation (trust score "
            f"{trust.overall_score:.2f})."
        )

    if decision.decision == "WARN":
        flagged = [r for r in results if r.verdict != "SUPPORTED"]
        flagged_text = "; ".join(
            f'"{r.claim}" ({r.verdict.lower()})' for r in flagged
        )
        return (
            f"This answer is only partially supported (trust score "
            f"{trust.overall_score:.2f}). {len(flagged)} of "
            f"{trust.num_claims} claim(s) could not be fully verified: "
            f"{flagged_text}. Review these before relying on the answer."
        )

    if decision.decision == "REFUSE":
        if trust.num_claims == 0:
            return "This answer could not be verified — no claims were found to check."
        return (
            f"This answer could not be adequately verified against the "
            f"retrieved documentation (trust score {trust.overall_score:.2f}). "
            f"{trust.num_unsupported + trust.num_contradiction} of "
            f"{trust.num_claims} claim(s) lacked sufficient supporting evidence."
        )

    if decision.decision == "ESCALATE":
        contradicted = [r for r in results if r.verdict == "CONTRADICTION"]
        contra_text = "; ".join(f'"{r.claim}"' for r in contradicted)
        return (
            f"This answer contains {len(contradicted)} claim(s) that "
            f"directly contradict the retrieved documentation: "
            f"{contra_text}. Escalated for human review before delivery."
        )

    return decision.reason


def generate_report(query: str, answer: str, results: list[VerificationResult],
                     trust: TrustScore, decision: Decision) -> TrustReport:
    """Build the full three-layer TrustReport for one query/answer pair."""
    return TrustReport(
        query=query,
        answer=answer,
        decision=decision.decision,
        reason=decision.reason,
        overall_score=trust.overall_score,
        num_claims=trust.num_claims,
        num_supported=trust.num_supported,
        num_unsupported=trust.num_unsupported,
        num_contradiction=trust.num_contradiction,
        explanation=_explain(decision, trust, results),
        citations=_build_citations(results),
    )


def format_report(report: TrustReport) -> str:
    """Render a TrustReport as readable plain text, e.g. for CLI/demo output."""
    lines = [
        f"Query: {report.query}",
        f"Answer: {report.answer}",
        "",
        f"Decision: {report.decision}  (trust score: {report.overall_score:.2f})",
        f"Reason: {report.reason}",
        "",
        report.explanation,
        "",
        "Citation trail:",
    ]
    for i, c in enumerate(report.citations, 1):
        lines.append(
            f"  {i}. [{c.verdict}] (score={c.score:.2f}) {c.claim}"
        )
        lines.append(f"     source: {c.source}")
        lines.append(f"     evidence: {c.evidence_snippet}")
    return "\n".join(lines)
