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


def test_condition_in_evidence_omitted_from_claim_is_penalised():
    # The evidence carries a conditional exception ("unless") that the claim
    # silently drops. The claim contains no negation marker of its own, so
    # this case is only reachable if _negation_check tests BOTH sides — it
    # was previously unreachable and scored a full 1.0, which is the failure
    # mode this mechanism exists to catch.
    chunk = FakeChunk(
        "Lockout is required unless the equipment cannot be locked out."
    )
    claim = "Lockout is always required."

    result = verify_claim(claim, [chunk])

    negation = [m for m in result.mechanisms if m.name == "negation"]
    assert negation, "negation mechanism should be recorded"
    assert negation[0].fired, "negation should fire when evidence has a condition"
    assert negation[0].score < 1.0, "omitted condition should carry a penalty"


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


def test_sentence_granularity_finds_support_diluted_in_a_long_chunk():
    # The supporting sentence sits among four unrelated ones, which is what a
    # 512-character chunk looks like in practice. DeBERTa is fine-tuned on
    # single sentence pairs, so the whole-chunk premise dilutes it.
    chunk = FakeChunk(
        "The control box houses the main power supply unit. "
        "Main power must be disconnected before any maintenance is performed. "
        "The teach pendant connects via a shielded cable. "
        "Observe ESD regulations when handling circuit boards. "
        "Ambient operating temperature is specified in section 4."
    )
    claim = "Disconnect the main power supply before maintenance."

    from src.trust_layer.verifier import _nli_scores, _NLI_ENTAILMENT

    chunk_level = _nli_scores(claim, chunk.page_content, granularity="chunk")
    sent_level = _nli_scores(claim, chunk.page_content, granularity="sentence")

    # Sentence granularity isolates the one relevant premise, so entailment
    # should be at least as high as the diluted whole-chunk reading.
    assert sent_level[_NLI_ENTAILMENT] >= chunk_level[_NLI_ENTAILMENT]


def test_split_for_nli_falls_back_when_there_are_no_sentence_boundaries():
    from src.trust_layer.verifier import _split_for_nli

    runon = "mainpowermustbedisconnectedbeforeservicingtheequipmentproperly"
    assert _split_for_nli(runon) == [runon], "must never return an empty premise list"

    normal = "Power must be disconnected. Observe ESD regulations at all times."
    assert len(_split_for_nli(normal)) == 2


def test_contradiction_in_a_non_winning_chunk_still_escalates():
    # The bug this guards: a contradicting chunk is scored 0.0 and therefore
    # always loses the max to any on-topic chunk, so the contradiction was
    # silently discarded. With k=5 in production that made ESCALATE
    # unreachable — 0 of 101 claims above threshold at answer level, against
    # 43 of 302 where only one chunk was supplied.
    on_topic = FakeChunk(
        "The robot arm stopping performance is measured during commissioning "
        "and recorded in the installation log for future reference.",
        source="ur5e.pdf",
    )
    contradicting = FakeChunk(
        "The arm must never be operated without the safety guard fitted.",
        source="osha.pdf",
    )
    claim = "The arm may be operated without the safety guard fitted."

    # The contradicting chunk is deliberately NOT first, so it cannot win by
    # being the only candidate.
    result = verify_claim(claim, [on_topic, contradicting])

    assert result.verdict != "SUPPORTED"
    assert result.best_chunk_source.startswith("osha.pdf"), \
        "a CONTRADICTION must cite the contradicting chunk, not the top-scoring one"


def test_max_contradiction_is_taken_across_all_chunks():
    from src.trust_layer.verifier import _nli_scores, _NLI_CONTRADICTION

    premise_agrees = "Lockout is required before any maintenance is performed."
    premise_denies = "Maintenance may be performed without applying lockout."
    claim = "Lockout is required before maintenance."

    agree = _nli_scores(claim, premise_agrees)[_NLI_CONTRADICTION]
    deny = _nli_scores(claim, premise_denies)[_NLI_CONTRADICTION]
    # Sanity check on the fixture itself: the denying premise must be the more
    # contradictory of the two, or the test above proves nothing.
    assert deny > agree
