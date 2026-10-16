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


def test_normalisation_strips_meta_framing():
    from src.trust_layer.decomposer import normalise_claim
    # A direct quotation from the manual that verified as UNSUPPORTED purely
    # because of the framing wrapped around it.
    c = ("According to the context, it is explicitly stated on page 30 of the "
         "User Manual: Very strong magnetic fields can damage the robot.")
    assert normalise_claim(c) == "Very strong magnetic fields can damage the robot."


def test_normalisation_drops_document_location_claims():
    from src.trust_layer.decomposer import normalise_claim
    assert normalise_claim("This is mentioned in step 8 of the Remote Display Tab section.") is None
    assert normalise_claim("This is mentioned in the section on Tool Turret Operations.") is None


def test_normalisation_strips_inline_citations():
    from src.trust_layer.decomposer import normalise_claim
    c = "Approved industrial safety glasses (Source: KneeMill-Complete-Manual.pdf p.2)"
    assert "Source" not in normalise_claim(c)
    assert "p.2" not in normalise_claim(c)


def test_normalisation_strips_conversational_connectors():
    from src.trust_layer.decomposer import normalise_claim
    assert normalise_claim("Therefore, yes, the Bridgeport takes R8 collets.") == \
        "The Bridgeport takes R8 collets."


def test_normalisation_leaves_a_clean_claim_alone():
    from src.trust_layer.decomposer import normalise_claim
    c = "There must be no inbound connections from adjacent networks to the robot."
    assert normalise_claim(c) == c


# ---------------------------------------------------------------------------
# Atomic splitting — claim length is what drives entailment
#
# Measured over all 392 verified claims: mean entailment 0.69 for claims under
# 12 words, 0.16 for claims of 26 or more, with similarity moving the OPPOSITE
# way (long claims are more on topic, not less). These cases pin the splits
# that shorten a claim, and — just as important — the ones that must not fire,
# because a split that changes what is being claimed is worse than a long
# claim.
# ---------------------------------------------------------------------------

def test_prose_trailing_a_list_item_is_split_into_sentences():
    # The list regex gives the final item everything to the end of the
    # answer, so closing prose was swallowed into it. q126 came out as a
    # single 123-word "claim" built from six sentences.
    answer = (
        "1. Check the oil level.\n"
        "2. Close the access panel. The machine is now ready for operation. "
        "Always wear safety glasses while it runs."
    )
    claims = decompose(answer)
    assert len(claims) == 4
    assert all(len(c.split()) < 12 for c in claims)


def test_non_restrictive_relative_clause_becomes_its_own_claim():
    answer = ("The spindle guard, which must be removed before servicing, "
              "covers the drive belt assembly at all times.")
    claims = decompose(answer)
    assert len(claims) == 2
    # The subject has to be carried over, or the detached clause is a fragment
    assert "The spindle guard covers the drive belt assembly at all times." in claims
    assert "The spindle guard must be removed before servicing." in claims


def test_restrictive_relative_clause_is_left_attached():
    # No commas: the clause says WHICH agents are meant. Detaching it would
    # broaden "the agents you can use include water" into a claim about all
    # agents — easier to support and no longer what the answer said.
    answer = ("The recommended cleaning agents you can use include water "
              "and isopropyl alcohol for the robot arm.")
    assert len(decompose(answer)) == 1


def test_appositive_becomes_an_explicit_statement():
    answer = ("The R8 collet, a standard Bridgeport fitting, is tightened "
              "with the drawbar from above the spindle.")
    claims = decompose(answer)
    assert "The R8 collet is a standard Bridgeport fitting." in claims
    assert any("tightened with the drawbar" in c and "fitting" not in c
               for c in claims)


def test_comma_separated_noun_list_is_not_read_as_an_appositive():
    # spaCy parses the second item of "water, 70% isopropyl alcohol, ..." as
    # an appositive of the first. Emitting "Water is 70% isopropyl alcohol."
    # would fabricate a claim the answer never made.
    answer = ("Use water, 70% isopropyl alcohol, 10% ethanol alcohol, "
              "and 10% naphtha to clean the robot arm.")
    claims = decompose(answer)
    assert not any(c.lower().startswith("water is") for c in claims)


def test_condition_is_distributed_across_coordinated_verbs():
    # Dropping the condition would manufacture an unconditional instruction.
    # It is copied into every conjunct instead.
    answer = ("When the Hi-Lo lever is engaged, disconnect the main power "
              "supply and remove the access cover from the head.")
    claims = decompose(answer)
    assert len(claims) == 2
    assert all(c.lower().startswith("when the hi-lo lever is engaged")
               for c in claims)


def test_conditional_clause_is_never_detached_on_its_own():
    # "If X, you can do Y" does not entail "You can do Y".
    answer = ("If you only want to modify 1 or 2 variables during each run, "
              "you can favorite specific program variables.")
    claims = decompose(answer)
    assert len(claims) == 1


def test_negation_is_carried_but_not_duplicated():
    answer = ("Do not shift the back gear lever and do not operate the "
              "spindle brake while the motor is running.")
    claims = decompose(answer)
    assert len(claims) == 2
    assert all(c.lower().count("do not") == 1 for c in claims)


def test_words_are_not_fused_across_a_removal():
    # Rebuilding text from token indices silently drops the space where the
    # cut was made: "The R8 colletis tightened".
    answer = ("The R8 collet, a standard Bridgeport fitting, is tightened "
              "with the drawbar from above the spindle.")
    for claim in decompose(answer):
        assert "colletis" not in claim
        assert ", ," not in claim
        assert not claim.startswith(",")


def test_claims_about_missing_information_are_dropped():
    from src.trust_layer.decomposer import normalise_claim
    # Handed to NLI next to a manual that discusses Bridgeport mills, this
    # came back CONTRADICTION at p=0.98 — the model penalised for admitting
    # it does not know.
    assert normalise_claim(
        "There is no specific mention of a Bridgeport mill in the provided manual.") is None
    assert normalise_claim(
        "The context does not provide information on the drawbar torque.") is None
    assert normalise_claim(
        "Since this icon is not mentioned in the manual, I cannot provide a meaning.") is None


def test_an_answer_made_only_of_meta_commentary_has_no_claims():
    # The old fallback returned the raw answer whenever every claim was
    # filtered, which handed the verifier exactly the text that was dropped.
    assert decompose("There is no information about this in the manual.") == []


def test_a_short_answer_is_still_returned_as_a_claim():
    # The fallback must survive for answers that are merely short — nothing
    # was dropped here, the text is just below the fragment threshold.
    assert decompose("Yes") == ["Yes"]
    assert decompose("4 days") == ["4 days"]
