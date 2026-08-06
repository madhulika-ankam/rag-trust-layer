"""
Tests for Trust Layer modules.

Run with:
    source venv/bin/activate
    pytest tests/test_trust_layer.py -v
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trust_layer.decomposer import decompose


# ---------------------------------------------------------------------------
# decompose()
# ---------------------------------------------------------------------------

def test_numbered_list_splits_into_one_claim_per_step():
    answer = (
        '1. Disengage Auto Quill Feed "D", Figure 2.19.\n'
        "2. Locate \"F\" in mid (neutral) position.\n"
        "3. The quill is now under handwheel control"
    )
    claims = decompose(answer)
    assert len(claims) == 3
    assert "Disengage Auto Quill Feed" in claims[0]
    assert "mid (neutral) position" in claims[1]
    assert "handwheel control" in claims[2]


def test_safety_warning_paragraph_splits_into_sentences():
    answer = (
        "Do not shift hi-lo lever while motor is running. "
        "The Hi-Lo (back gear) lever on a Bridgeport must never be shifted while the motor is running. "
        "Turn motor off and apply brake until the spindle stops, then switch to appropriate gearing."
    )
    claims = decompose(answer)
    assert len(claims) == 3
    assert any("Do not shift" in c for c in claims)
    assert any("never be shifted" in c for c in claims)
    assert any("Turn motor off" in c for c in claims)


def test_single_sentence_answer_returns_one_claim():
    answer = (
        "If you only want to modify 1 or 2 variables during each run, "
        "you can favorite specific program variables so you can access them easier."
    )
    claims = decompose(answer)
    assert len(claims) == 1


def test_multi_sentence_paragraph_splits_correctly():
    answer = (
        "The network requirements suggest that only trusted devices should be connected "
        "to the local area network. "
        "There must be no inbound connections from adjacent networks to the robot. "
        "Only URCaps and magic scripts from trusted partners can be used."
    )
    claims = decompose(answer)
    assert len(claims) == 3
    assert any("trusted devices" in c for c in claims)
    assert any("inbound connections" in c for c in claims)
    assert any("URCaps" in c for c in claims)


def test_chemical_list_stays_together_not_split():
    answer = (
        "You should not use bleach as a cleaning solution for this arm. "
        "The recommended agents you can use include water, 70% isopropyl alcohol, "
        "10% ethanol alcohol, and 10% naphtha to remove grease."
    )
    claims = decompose(answer)
    assert len(claims) == 2
    assert any("bleach" in c for c in claims)
    # Chemical list should be one claim, not split into individual chemicals
    chem_claim = next(c for c in claims if "isopropyl" in c)
    assert "naphtha" in chem_claim


def test_short_factual_answer_survives():
    # "Yes" is 1 word — below the fragment threshold — should still be returned
    claims = decompose("Yes")
    assert len(claims) == 1
    assert claims[0] == "Yes"


def test_empty_answer_returns_empty_list():
    assert decompose("") == []
    assert decompose("   ") == []


def test_regulatory_code_not_split_on_dot():
    # "1910.147" contains a dot but is not a sentence boundary
    answer = "Under OSHA 1910.147, the employer must establish an energy control program."
    claims = decompose(answer)
    assert len(claims) == 1
    assert "1910.147" in claims[0]
