# Errors Found and Fixed — RAG Trust Layer

This documents every bug found while building and testing the Trust Layer,
in the order they were found, with the symptom, root cause, how it was
diagnosed, the fix, and how the fix was verified. Most of these were only
findable by actually running the pipeline against real data — none showed
up from reading the code alone.

---

## 1. Verifier silently dropped chunks that scored exactly 0.0

**Found:** 2026-08-06, while writing test coverage for `verifier.py`.

**Symptom:** A test claim with an obvious numeric mismatch — "Do not operate
the lathe above **500** rpm" vs. evidence saying "Do not operate the lathe
above **300** rpm" — should have been flagged UNSUPPORTED with a clear
explanation. Instead, `verify_claim()` returned the misleading message "all
chunks below similarity gate" with `best_chunk_source: "none"`, even though
the chunk was 99% topically similar and clearly evaluated.

**Root cause:** In `verify_claim()` (`src/trust_layer/verifier.py`), the
"best score so far" tracker was initialized to `0.0`, and the loop only
recorded a chunk as the best match when `combined > best_score` (strict
greater-than). When the entity-matching mechanism caught the number
mismatch, it multiplied the chunk's combined score down to exactly `0.0`.
Since `0.0 > 0.0` is `False` in Python, that legitimately-evaluated chunk
was never recorded — the function fell through to the "no chunk passed the
gate" branch, which is meant for a completely different situation (nothing
topically relevant at all).

**Why it mattered:** This wasn't just a cosmetic message issue. It meant
every claim that scored exactly 0.0 after a mechanism penalty — which is
exactly the scenario the entity-matching mechanism exists to catch — lost
its citation, its per-mechanism score breakdown, and got mislabeled as "no
relevant evidence found" instead of "evidence found, but a critical detail
doesn't match." For a transparency-report system, that's the difference
between two very different explanations shown to a user.

**Fix:** Changed the initial value from `0.0` to `-1.0`
(`src/trust_layer/verifier.py:181`), so any chunk that actually got
evaluated — even one that legitimately scores 0.0 — is still recorded as
the best match.

**Verification:** Re-ran the failing test; the result correctly returned
`verdict: CONTRADICTION` (NLI itself also caught the mismatch, 99.7%
contradiction probability), with the citation and full mechanism breakdown
intact. Added `test_claim_with_number_mismatch_is_not_supported` to
`tests/test_verifier.py` to guard against regression.

---

## 2. Decomposer didn't recognize `+` as a bullet marker

**Found:** 2026-08-07, during the first real end-to-end pipeline run
(llama3-generated answer, not a hand-written fixture).

**Symptom:** llama3 answered a question using nested Markdown bullets:

```
* Lockout devices and tagout devices shall be:
    + Singularly identified
    + The only device(s) used for controlling energy
    + Not used for other purposes
    + Durable, capable of withstanding the environment ... (p.4)
```

`decompose()` produced only 2 garbled claims instead of 5 clean ones, e.g.:
`"* Lockout devices and tagout devices shall be: + Singularly identified +"`
— bullet markers left in the text, content split at arbitrary points.

**Root cause:** `_LIST_ITEM_RE` in `src/trust_layer/decomposer.py` only
recognized `-`, `•`, and `*` as bullet characters. LLM-generated Markdown
commonly uses a different symbol per nesting level (a common writing
convention so consecutive same-symbol bullets don't visually blend), and
`+` for a second-level bullet is a standard choice. With `+` unrecognized,
only the single top-level `*` line counted as a "list item" match — but
`_split_list_items()` requires at least 2 matches to treat text as a list,
so it fell through to spaCy sentence-splitting, which doesn't understand
bullet/indentation structure and mangled the output.

**Fix:** Added `+` to the bullet character class:
`[-•*+]\s+` (`src/trust_layer/decomposer.py:28`).

**Verification:** Re-ran `decompose()` on the same input — now correctly
found 5 list items instead of 2 garbled fragments. Added
`test_plus_bullets_are_recognized_as_list_items` to
`tests/test_trust_layer.py`.

---

## 3. Nested sub-bullets became unverifiable sentence fragments

**Found:** 2026-08-07, immediately after fixing #2 — fixing the bullet
regex revealed a deeper problem underneath it.

**Symptom:** With `+` now recognized, the same nested list correctly split
into 5 items, but each child bullet came out as an isolated fragment:
`"Not used for other purposes"` instead of a complete statement. Verifying
this fragment against the exact matching regulation text — which literally
contains the phrase "...shall not be used for other purposes..." — still
scored it as **UNSUPPORTED** (score 0.11). Manually inspecting the
verifier's mechanism breakdown showed why: NLI scored the fragment as 98.4%
"neutral" and only 1.6% "entailment," because "Not used for other purposes"
has no subject — it isn't a complete proposition an NLI model can confidently
match against anything, regardless of how well the words overlap with the
evidence.

**Root cause:** `decompose()` treated every bullet in a list — parent lines
and indented children alike — as independent, standalone claims. But a
child bullet under a line like `"X shall be:"` is only a complete thought
*combined with* the parent ("X shall be [child]"). Splitting them apart
without carrying the parent's text forward produces claims that are
technically "atomic" but grammatically incomplete, which breaks NLI
verification even when the underlying fact is 100% correct and well-cited.

**Decision point:** Two fixes were possible — teach the decomposer to merge
parent/child bullet text, or constrain the LLM's prompt to avoid nested
bullets in the first place. Chose to fix the decomposer, since it handles
any LLM output structure robustly rather than depending on prompt
compliance that could silently break with a future model or prompt change.

**Fix:** Rewrote `_split_list_items()` to capture each bullet's indentation
level, then added `_merge_nested_items()` and `_merge_parent_child()`
(`src/trust_layer/decomposer.py`). Logic: track an ancestor stack keyed by
indent depth; when a list item ends in `:` (a strong signal it's an intro
line, e.g. "Lockout devices shall be:"), treat it as a header for its
children — don't emit it as its own claim, but prepend its (colon-stripped)
text to every indented child beneath it. Flat, non-nested lists are
unaffected since they have no indentation depth changes and no colon-ending
parent lines.

**Verification:**
- `"Not used for other purposes"` → merged into `"Lockout devices and
  tagout devices shall be not used for other purposes"` — now scores as a
  complete, verifiable claim.
- As a side benefit, `"Singularly identified"` (2 words) previously got
  silently dropped by the decomposer's own fragment-length filter
  (`_MIN_CLAIM_WORDS = 4`); merged with its parent it becomes 8 words and is
  correctly kept.
- Added `test_nested_bullet_children_inherit_parent_context` and
  `test_flat_list_unaffected_by_nesting_logic` to `tests/test_trust_layer.py`
  to cover both the new behavior and confirm no regression on plain lists.
- Full suite (45 tests) still passes.

---

## 4. Persisted Chroma index was missing 13 of 17 knowledge base documents

**Found:** 2026-08-07, while running the full pipeline against a real gold
question ("How do I put the quill in hand feed mode on the bridgeport
mill?").

**Symptom:** The pipeline correctly retrieved chunks, generated an answer,
and produced a report — but the LLM said "the provided context does not
contain any information about putting a quill in hand feed mode on a
Bridgeport mill," and the Trust Layer correctly REFUSED. That looked
correct at first (a good sign the system doesn't hallucinate when retrieval
comes up empty), but the question directly matches your own gold-answer
dataset (Q1), which cites the manual by figure number — meaning the content
plainly exists in your source PDFs and should have been retrievable.

**Root cause:** Queried the persisted index directly
(`vectorstore.get()` and inspected `metadatas`) and found it only contained
chunks from 4 source documents — all OSHA CFR regulations — none of the
equipment manuals (Bridgeport/knee mill, Haas lathe, UR5e robot), OSHA
technical documents, or NIOSH alerts. The index had been built at some
earlier point from an incomplete/older snapshot of `data/raw` (likely
before the manuals were added) and never rebuilt since. This wasn't a
retrieval-quality problem — the content simply didn't exist in the index at
all.

**Fix:** Ran `build_index()` (`src/main.py`) fresh against the current,
complete `data/raw` folder — all 17 PDFs, including the large 20MB UR5e
manual and 17MB lathe manual. Produced 1,089 pages → 3,964 chunks.

**Verification:** Re-queried the index; the Bridgeport question now
retrieved real content from `KneeMill-Complete-Manual.pdf`, the LLM
generated a grounded answer citing the actual manual, and the Trust Layer
correctly flagged one claim as SUPPORTED (0.88, tied to a specific page)
and one as UNSUPPORTED (0.18, evidence didn't match that particular detail)
— exactly the kind of nuanced, per-claim judgment the system is designed to
produce.

---

## 5. Index rebuild appended to the old index instead of replacing it

**Found:** 2026-08-07, immediately after fixing #4 — verifying the "fixed"
index revealed a second problem.

**Symptom:** After the rebuild in #4, the index reported **21** source
documents instead of the expected 17. Listing them showed 4 duplicates of
the original stale OSHA documents still present — including 2
(`1910.119`, `1910.132`) that don't even exist in `data/raw` anymore at
all; they were orphaned leftovers with no current source file backing them.

**Root cause:** `build_vectorstore()` (`src/rag/retriever.py`) calls
`Chroma.from_documents(..., persist_directory=CHROMA_DIR)`. Chroma appends
new documents to an existing persisted collection at that path rather than
replacing it — it was never actually a "rebuild," every prior run had been
purely additive.

**Decision point:** Considered wiping and rebuilding the whole index
outright vs. deleting only the stale entries by metadata. Chose targeted
deletion for the immediate fix (no need to re-embed 3,964 chunks over
again), but fixed `build_vectorstore()` itself to always wipe and rebuild
from scratch — the user confirmed the source documents won't change often,
so simplicity and guaranteed correctness matter more than the efficiency
of an incremental sync, which would have been meaningfully more code for a
rarely-run operation.

**Fix:**
1. Immediate cleanup: identified the 4 stale `source_file` values, deleted
   their 342 chunks directly via `vectorstore.delete(ids=...)`, leaving a
   clean 17-document index.
2. Root-cause fix: `build_vectorstore()` now calls `shutil.rmtree(CHROMA_DIR)`
   before creating the new index, so every future rebuild starts clean
   (`src/rag/retriever.py`).

**Verification:** Re-listed the index's source documents — exactly the 17
current files in `data/raw`, no duplicates, no orphans. Full test suite
(45 tests) still passes.

---

## Summary

| # | Component | Symptom | Root cause | Fix |
|---|---|---|---|---|
| 1 | `verifier.py` | Misleading "no chunk passed gate" message, lost citations | `best_score` init `0.0` + strict `>` comparison dropped legitimately-scored-0.0 chunks | Init to `-1.0` |
| 2 | `decomposer.py` | Nested LLM bullets produced garbled claims | `+` bullet character not recognized | Added `+` to bullet regex |
| 3 | `decomposer.py` | Correctly-cited claims scored UNSUPPORTED | Child bullets split into fragments without parent's grammatical subject | Merge parent text into indented children |
| 4 | `data/chroma` (index) | Real gold questions about equipment manuals got REFUSE | Index only had 4/17 documents — manuals were never indexed | Rebuilt index from full `data/raw` |
| 5 | `retriever.py` + index | Rebuilt index had duplicate/orphaned stale entries | `Chroma.from_documents()` appends, doesn't replace | Deleted stale entries; `build_vectorstore()` now wipes before rebuilding |

All five were found through actually running the pipeline end-to-end
against real data, not from reading the code or from isolated unit tests —
each one only became visible once a real LLM-generated answer or a real
gold question exposed a scenario the fixture-based tests hadn't covered.