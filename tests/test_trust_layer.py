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


def test_plus_bullets_are_recognized_as_list_items():
    # LLM-generated markdown commonly uses "+" for a nested bullet level;
    # the original regex only recognized "-", "*", "•" and missed these.
    answer = "* Required PPE:\n\t+ Safety glasses\n\t+ Steel-toed boots\n\t+ Hearing protection"
    claims = decompose(answer)
    assert len(claims) == 3


def test_nested_bullet_children_inherit_parent_context():
    # A child bullet like "Not used for other purposes" is a fragment on its
    # own — NLI can't verify it as a standalone claim. It must be merged with
    # its parent line so it reads as a complete, checkable sentence.
    answer = (
        "* Lockout devices and tagout devices shall be:\n"
        "\t+ Singularly identified\n"
        "\t+ Not used for other purposes"
    )
    claims = decompose(answer)
    assert len(claims) == 2
    assert all("Lockout devices and tagout devices shall be" in c for c in claims)
    assert any("singularly identified" in c for c in claims)
    assert any("not used for other purposes" in c for c in claims)
    # the header itself, ending in ":", should not be emitted as its own claim
    assert not any(c.strip().endswith(":") for c in claims)


def test_flat_list_unaffected_by_nesting_logic():
    # Sanity check: a plain, non-nested numbered list should behave exactly
    # as before the nested-merge change.
    answer = (
        "1. Wear safety glasses at all times.\n"
        "2. Lock out the machine before maintenance.\n"
        "3. Verify the zero energy state before proceeding."
    )
    claims = decompose(answer)
    assert len(claims) == 3
    assert claims[0] == "Wear safety glasses at all times."
    assert claims[1] == "Lock out the machine before maintenance."
    assert claims[2] == "Verify the zero energy state before proceeding."
