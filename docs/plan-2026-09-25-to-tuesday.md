# Plan — Friday 25 Sep to Tuesday meeting

Built from the supervisor to-do list, reordered by what is actually blocking
what, and by what has to be true on Tuesday.

---

## The honest framing

The supervisor list is not a four-day list. "Extensive literature review" plus
experiments plus finalising the design plus drafting seven thesis sections is
several weeks of work. Attempting all of it produces four shallow things
instead of two solid ones.

**What has to be true on Tuesday:** Dr. Maier said the scores are meaningless
and not mathematically backed. Every conceptual answer given so far has failed
to land, because the answer to "how do I trust these numbers" is not an
explanation — it is numbers. **The deliverable for Tuesday is a table.**

Everything below is ordered around producing that table and the design
decisions it unlocks.

### The key scheduling insight

**The perturbation set does not depend on fixing the REFUSE problem.**

```
Perturbation set → validates the VERIFIER
                   claim level, ~100 pairs
                   INDEPENDENT of the scorer

161-question run → validates the SYSTEM
                   answer level
                   BLOCKED by the REFUSE diagnosis
```

So the Maier deliverable can be produced this weekend regardless of whether
the scorer question is settled. Do it first.

---

## Friday (today) — set up the experiment

```
□ E0 security items — 15 min, do these first
  → revoke the GitHub token in .git/config,
    switch the remote to SSH
  → gitignore the OEM manuals and the Megahed
    dataset; note provenance in the README

□ Build the perturbation set  (~100 pairs)
  Source: gold answers from the 161-question set.
  Three corruption types, ~33 each, one error per pair:

    numerical    "200ms" → "500ms"
                 "300°C" → "500°C"
    negation     "required unless X" → "always required"
    entity swap  "Recovery mode" → "Emergency mode"
                 "OSHA 1910.147" → "OSHA 1910.212"

  Each row: claim, evidence chunk, label, perturbation_type
  Keep the UNCORRUPTED original as a positive example
  → ~100 corrupted + ~100 clean = ~200 labelled pairs

  Precedent: BUMP (Ma et al., 2023) — minimal pairs,
  single error from an ontology of types.

□ Split it: ~50% validation, ~50% test
  Thresholds and weights are selected on validation ONLY.
```

**Why this first:** it is the only item that directly answers Maier, and it is
one afternoon.

---

## Saturday — run it, and diagnose

```
MORNING — produce the numbers

□ Run the verifier over every perturbation pair
  Record: entailment_p, similarity, entity_ratio,
  negation_flag, combined score, verdict

□ Compute, on the TEST half:
    balanced_accuracy_score(true, predicted)
    roc_auc_score(true, scores)
  → two lines of scikit-learn

□ Break both out BY PERTURBATION TYPE
  → this is the differentiating result

□ Run the ablation over the same set:
    NLI only → +entity → +negation → full
  → the table below is the target

                  NLI   +entity  +negation  full
  Numerical       __%     __%      __%      __%
  Negation        __%     __%      __%      __%
  Entity swap     __%     __%      __%      __%
  Overall         __%     __%      __%      __%

  Doubles as an integration test: if the +entity
  column equals the NLI column, entity matching
  is not wired in.

AFTERNOON — the diagnosis

□ Re-run the 10-question batch, saving FULL per-claim
  detail to JSON this time (it currently exists only
  in an artifact)

□ Reading pass. For each flagged claim, one question:
  is this claim actually supported by the chunk it
  was checked against?

    supported but marked UNSUPPORTED  → Break #1
    all claims right, answer still died → Break #2
    genuinely not in the chunk         → Break #3
    supported, but by TWO chunks       → Break #1b

  COUNT THE PROPORTIONS. It will not be one cause.
```

---

## Sunday — finalise the design

"Finalise the middleware" means settling four open decisions. All four are now
evidence-based rather than matters of taste.

```
□ 1. THE WEIGHTS — fit them instead of choosing them
  This is the direct answer to "not mathematically
  backed up."

    P(supported) = σ(w₀ + w₁·entailment
                      + w₂·similarity
                      + w₃·entity_ratio
                      + w₄·negation_flag)

  Logistic regression, fitted by maximum likelihood
  on the validation half. ~20 lines of sklearn.
  Report the coefficients.

  The weights stop being chosen. They become fitted
  parameters from a standard method, and the
  coefficients tell you which mechanism carries
  the signal.

  EVALUATION_PLAN.md currently lists this under
  "skip unless time allows." After the meeting on
  the 24th it is necessary.

□ 2. THE SCORER — only if the reading pass says
  Break #2 dominates
    current: mean × (1 − bad_fraction)
    ceiling with one bad claim of n: 1 − 1/n
    → 0.50 at 2 claims, 0.67 at 3, 0.75 at 4
    → ANSWER (≥0.85) unreachable at realistic
      claim counts
  Options: soft penalty, or a min/mean blend.

□ 3. SENTENCE-LEVEL NLI — only if Break #1 dominates
  Split each chunk into sentences, score the claim
  against each, take the max, cite the chunk the
  winning sentence came from.
  ~15 lines inside verify_claim. Same model, no GPU.
  Citable: "following SummaC, verification at
  sentence granularity with max-aggregation."

□ 4. THE ENTITY PENALTY — decide and document
    comment says: each miss halves  (0.5^misses,
                  never reaches zero)
    code does:    score = matched/total
                  (hits 0.0, annihilates the claim)
  One missing value in a single-value claim is the
  common case: ×0.5 versus ×0.0. Pick one, make the
  comment and the code agree.
```

**Rule for all four: change one thing at a time and re-measure.** Changing the
model and the input together, or the weights and the scorer together, destroys
attribution.

---

## Monday — writing and the literature gap

```
□ Chapter 1 fixes — CONTEXT.md section E4, ~1 hour
  → broken citation tag in §1.2
  → Objective 4: apply the replacement already
    written in EVALUATION_PLAN.md
  → Contribution 6: three configurations, not one
    baseline
  → Contributions 2 and 4: apply
    chapter-1-contributions-revision.md
  → §1.5: Module 2 is not built — future tense
  → unify on "unsupported-answer delivery rate"

□ Chapter 3 (Design) — draft, results-independent
  Everything needed is now settled or about to be:
  the module structure, the cascade ordering and
  WHY (cheap-and-precomputable before
  expensive-and-pairwise), the scoring formulation,
  the threshold derivation argument.

□ Chapter 4 (Implementation) — outline only
  Fill in after the design decisions land.
  NOTE: the documented formula is wrong in three
  places (CONTEXT.md, EVALUATION_PLAN.md, the
  thesis chat). Fix before writing, not after.

□ Literature — VERIFY, do not expand
  The reading list is already assembled in
  EVALUATION_PLAN.md. What is missing is
  verification, not more papers.

  Confirm against ACL Anthology / arXiv:
    DeBERTa        He et al., ICLR 2021
    DeBERTaV3      He et al., ICLR 2023
    SNLI           Bowman et al., EMNLP 2015
    MultiNLI       Williams et al., NAACL 2018
    Sentence-BERT  Reimers & Gurevych, EMNLP 2019 ✓
    SummaC         Laban et al., 2022
    TRUE           Honovich et al., 2022
    BUMP           Ma et al., 2023
    FactCC         Kryscinski et al., 2020

  Plus the Chapter 1 reference list's own flagged
  items [5], [6], [7], [9].
```

### The one real literature gap

The supervisor asked for "paper ideas for the proposed metrics." The honest
finding, after searching:

```
Manufacturing RAG papers
→ accuracy, cost, latency only
→ NO verification metrics anywhere

NLP factual-consistency papers
→ balanced accuracy, ROC-AUC, risk-coverage
→ no manufacturing context
```

**No manufacturing paper reports verification metrics, because nobody has done
verification-gated delivery in manufacturing.** That absence is the gap this
thesis occupies — say it as a finding, not as a hole in the review.

The bridge is Singh et al. (arXiv:2511.11847), the source of the 161-question
benchmark. They name high accuracy, low latency and low cost as the three
requirements for next-generation safety training systems, and report 86.66%
accuracy, $0.005/query, 10.04s latency. Running on their benchmark makes that
comparison direct.

---

## What to defer, and say so on Tuesday

```
✗ Results chapter        no results yet — that is
                         what this weekend produces
✗ Conclusion             follows Results
✗ Config B (RAGAS)       costs API money; pointless
                         before the design is settled
✗ Config C (LLM judge)   same
✗ Module 2               not built; not needed for
                         the Tuesday deliverable
✗ Full 161-question run  blocked on the design
                         decisions from Sunday
✗ Bibliography as a
  formatted artefact     the citations exist; formatting
                         them is an end-stage task
```

Deferring these deliberately, with reasons, reads far better than arriving
with seven half-finished sections.

---

## What to walk in with on Tuesday

```
1. The verifier validation table
   balanced accuracy, ROC-AUC, per perturbation type

2. The ablation table
   each mechanism against the failure mode it
   was built for

3. The fitted logistic-regression coefficients
   "the weights are not chosen; they are fitted by
    maximum likelihood on held-out validation data"

4. The diagnosis
   proportions of Break #1 / #2 / #3 across 10 cases,
   and what each implies

5. One sentence acknowledging his objection
   "You were right that the weighting was arbitrary.
    I have replaced the hand-chosen weights with
    coefficients fitted on held-out data, and here
    is the verifier's measured performance against
    known labels."
```

That last line matters. Committee members who push hard respond well to
evidence that their objection produced a change.

---

## Priority if the weekend compresses

```
1. Perturbation set + balanced accuracy + ROC-AUC
2. Per-type breakdown + ablation
3. Logistic regression fit
4. The 10-case reading pass
5. Chapter 1 fixes
6. Chapter 3 draft
```

Items 1–3 are the Tuesday meeting. Everything else can slip.
