"""
Tests for Module 3: Multi-Mechanism Verifier.

These tests load real models (sentence-transformers embedder + NLI
cross-encoder), so the first run will download weights and each test is
slower than the decomposer tests.

Run with:
    source venv/bin/activate
    pytest tests/test_verifier.py -v
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trust_layer.verifier import verify_claim, verify


class FakeChunk:
    """Stand-in for a LangChain Document — verifier only needs these two attrs."""

    def __init__(self, text, source="manual.pdf", page=1):
        self.page_content = text
        self.metadata = {"source_file": source, "page": page}


# ---------------------------------------------------------------------------
# verify_claim()
# ---------------------------------------------------------------------------

def test_claim_fully_supported_by_matching_chunk():
    chunk = FakeChunk(
        "The Hi-Lo (back gear) lever on a Bridgeport must never be shifted "
        "while the motor is running."
    )
    claim = "The Hi-Lo lever must never be shifted while the motor is running."

    result = verify_claim(claim, [chunk])

    assert result.verdict == "SUPPORTED"
    assert result.score >= 0.60
    assert result.best_chunk_source == "manual.pdf p.1"


def test_claim_contradicted_by_opposing_chunk():
    chunk = FakeChunk(
        "Employees must wear safety glasses at all times in the machine shop."
    )
    claim = "Employees are not required to wear safety glasses in the machine shop."

    result = verify_claim(claim, [chunk])

    # Whether NLI flags this directly as CONTRADICTION or the negation
    # mechanism drags an unsupported score down, it must not read as SUPPORTED.
    assert result.verdict != "SUPPORTED"


def test_claim_unsupported_when_no_relevant_chunk():
    chunks = [
        FakeChunk("Locate the quill feed handle and disengage Auto Quill Feed D."),
        FakeChunk("The Hi-Lo lever selects between high and low spindle speed ranges."),
    ]
    claim = "Use only water, isopropyl alcohol, or naphtha to clean the robot arm."

    result = verify_claim(claim, chunks)

    assert result.verdict == "UNSUPPORTED"
    assert result.score == 0.0
    assert result.best_chunk_source == "none"


def test_claim_with_number_mismatch_is_not_supported():
    chunk = FakeChunk("Do not operate the lathe above 300 rpm.")
    claim = "Do not operate the lathe above 500 rpm."

    result = verify_claim(claim, [chunk])

    # Topically identical but the critical number doesn't match — the chunk
    # must still be recorded (not dropped as "no chunk passed the gate"),
    # with the entity mismatch visible in the mechanism breakdown.
    assert result.verdict != "SUPPORTED"
    assert result.best_chunk_source == "manual.pdf p.1"
    entity_results = [m for m in result.mechanisms if m.name == "entity_match"]
    assert entity_results, "entity_match mechanism should have fired"
    assert entity_results[0].score < 1.0


def test_claim_with_unbacked_negation_is_flagged():
    chunk = FakeChunk("Employees may remove the guard during scheduled maintenance.")
    claim = "Employees may not remove the guard during scheduled maintenance."

    result = verify_claim(claim, [chunk])

    assert result.verdict != "SUPPORTED"


def test_best_chunk_chosen_across_multiple_chunks():
    off_topic = FakeChunk("The UR5e requires a 100Mbps network connection.", source="ur5e.pdf")
    on_topic = FakeChunk(
        "Under OSHA 1910.147, the employer must establish an energy control program.",
        source="osha_1910_147.pdf",
    )
    claim = "The employer must establish an energy control program under OSHA 1910.147."

    result = verify_claim(claim, [off_topic, on_topic])

    assert result.best_chunk_source == "osha_1910_147.pdf p.1"
    assert result.verdict == "SUPPORTED"


# ---------------------------------------------------------------------------
# verify()
# ---------------------------------------------------------------------------

def test_verify_returns_one_result_per_claim():
    chunk = FakeChunk("Wear safety glasses at all times in the machine shop.")
    claims = [
        "Wear safety glasses at all times in the machine shop.",
        "Use only water, isopropyl alcohol, or naphtha to clean the robot arm.",
    ]

    results = verify(claims, [chunk])

    assert len(results) == 2
    assert results[0].claim == claims[0]
    assert results[1].claim == claims[1]
