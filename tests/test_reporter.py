"""
Tests for Module 7: Transparency Report Generator.

Builds VerificationResult/TrustScore/Decision directly — generate_report()
only assembles what those modules already produced, so no models are needed.

Run with:
    source venv/bin/activate
    pytest tests/test_reporter.py -v
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trust_layer.verifier import VerificationResult
from src.trust_layer.scorer import TrustScore
from src.trust_layer.decision import Decision
from src.trust_layer.reporter import generate_report, format_report


def _result(verdict, claim_score, claim, source="manual.pdf p.1", chunk="evidence text"):
    return VerificationResult(
        claim=claim, verdict=verdict, score=claim_score,
        best_chunk=chunk, best_chunk_source=source,
    )


def _trust(results, overall_score):
    num_claims = len(results)
    num_supported = sum(1 for r in results if r.verdict == "SUPPORTED")
    num_unsupported = sum(1 for r in results if r.verdict == "UNSUPPORTED")
    num_contradiction = sum(1 for r in results if r.verdict == "CONTRADICTION")
    return TrustScore(
        overall_score=overall_score, mean_claim_score=overall_score,
        penalty_factor=1.0, num_claims=num_claims, num_supported=num_supported,
        num_unsupported=num_unsupported, num_contradiction=num_contradiction,
        has_contradiction=num_contradiction > 0,
        per_claim_scores=[r.score for r in results],
    )


def test_answer_report_has_no_flagged_claims_in_explanation():
    results = [
        _result("SUPPORTED", 0.95, "Wear safety glasses at all times."),
        _result("SUPPORTED", 0.90, "Lock out the machine before maintenance."),
    ]
    trust = _trust(results, 0.92)
    decision = Decision(decision="ANSWER", reason="fully supported (score=0.92)", overall_score=0.92)

    report = generate_report("What PPE is required?", "Wear glasses and lock out the machine.",
                              results, trust, decision)

    assert report.decision == "ANSWER"
    assert "supported" in report.explanation.lower()
    assert len(report.citations) == 2
    assert all(c.verdict == "SUPPORTED" for c in report.citations)


def test_warn_report_names_the_flagged_claims():
    results = [
        _result("SUPPORTED", 0.90, "Wear safety glasses at all times."),
        _result("UNSUPPORTED", 0.30, "Replace the filter every 4 days."),
    ]
    trust = _trust(results, 0.65)
    decision = Decision(decision="WARN", reason="partially supported (score=0.65)", overall_score=0.65)

    report = generate_report("q", "a", results, trust, decision)

    assert report.decision == "WARN"
    assert "Replace the filter every 4 days" in report.explanation
    assert "1 of 2" in report.explanation


def test_refuse_report_reflects_no_supporting_evidence():
    results = [
        _result("UNSUPPORTED", 0.0, "Use only bleach to clean the sensor."),
    ]
    trust = _trust(results, 0.0)
    decision = Decision(decision="REFUSE", reason="insufficient support (score=0.00)", overall_score=0.0)

    report = generate_report("q", "a", results, trust, decision)

    assert report.decision == "REFUSE"
    assert "could not be adequately verified" in report.explanation


def test_refuse_report_with_zero_claims_does_not_crash():
    trust = _trust([], 0.0)
    decision = Decision(decision="REFUSE", reason="no claims to verify", overall_score=0.0)

    report = generate_report("q", "", [], trust, decision)

    assert report.decision == "REFUSE"
    assert report.citations == []
    assert "no claims" in report.explanation.lower()


def test_escalate_report_names_the_contradicted_claims():
    results = [
        _result("SUPPORTED", 0.90, "Wear safety glasses."),
        _result("CONTRADICTION", 0.0, "It is safe to bypass the lockout during maintenance."),
    ]
    trust = _trust(results, 0.0)
    decision = Decision(decision="ESCALATE", reason="1 claim(s) contradict retrieved evidence", overall_score=0.0)

    report = generate_report("q", "a", results, trust, decision)

    assert report.decision == "ESCALATE"
    assert "bypass the lockout" in report.explanation
    assert "1 claim(s)" in report.explanation


def test_citation_evidence_is_truncated_for_long_chunks():
    long_chunk = "x" * 500
    results = [_result("SUPPORTED", 0.9, "claim", chunk=long_chunk)]
    trust = _trust(results, 0.9)
    decision = Decision(decision="ANSWER", reason="fully supported", overall_score=0.9)

    report = generate_report("q", "a", results, trust, decision)

    assert len(report.citations[0].evidence_snippet) < 500
    assert report.citations[0].evidence_snippet.endswith("...")


def test_format_report_produces_readable_text_with_all_sections():
    results = [_result("SUPPORTED", 0.9, "Wear safety glasses.")]
    trust = _trust(results, 0.9)
    decision = Decision(decision="ANSWER", reason="fully supported (score=0.90)", overall_score=0.9)

    report = generate_report("What PPE is required?", "Wear glasses.", results, trust, decision)
    text = format_report(report)

    assert "Query: What PPE is required?" in text
    assert "Decision: ANSWER" in text
    assert "Citation trail:" in text
    assert "Wear safety glasses." in text
    assert "manual.pdf p.1" in text
