# RAG Trust and Transparency Layer — Project Context

## What This Project Is

A Master's thesis project that builds a **Trust and Transparency Layer** for
Retrieval-Augmented Generation (RAG) systems. The system is demonstrated in
manufacturing safety but is designed as domain-agnostic middleware that can be
added to any RAG system in any safety-critical industry.

---

## The Core Problem

Standard RAG systems generate answers without any mechanism to verify whether
those answers are actually supported by retrieved evidence. This is dangerous in
safety-critical domains like manufacturing, where a hallucinated answer can lead
to incorrect or unsafe decisions.

There are four types of hallucination this project addresses:

- **Intrinsic** — answer contradicts retrieved evidence
- **Extrinsic** — answer contains claims not found in retrieved evidence
- **Conflation** — answer mixes facts from different documents incorrectly
- **Omission** — answer leaves out critical safety-relevant information

---

## What This Project Builds

A pluggable **Trust Layer** that sits on top of any existing RAG pipeline. It
takes three inputs from the RAG system — the original query, the retrieved
chunks, and the generated answer — and returns a structured trust report.

The Trust Layer does NOT:
- Modify the RAG retrieval mechanism
- Change how the LLM generates answers
- Retrain any model

It DOES:
- Intercept generated answers before they reach the user
- Verify each claim against retrieved evidence
- Score overall confidence
- Make a decision about what to return
- Explain why in human-readable form

---

## System Architecture

### Standard RAG Pipeline (Baseline — not the contribution)

```
User Query → Embed → Vector Search → Retrieve Top K Chunks → LLM → Answer
```

### Trust Layer (The Contribution)

```
[Query + Retrieved Chunks + Generated Answer]
                ↓
        MODULE 1: Claim Decomposer
        Break answer into atomic verifiable claims
                ↓
        MODULE 2: Retrieval Coverage Check
        Do retrieved chunks contain enough information?
        (If not → REFUSE immediately)
                ↓
        MODULE 3: Multi-Mechanism Verifier
        For each claim vs retrieved chunks:
          - NLI Model (deberta-v3) → logical entailment
          - Entity & Number Matching → numerical/code precision
          - Negation Detection → conditional exceptions
          - Semantic Similarity → topical coverage
                ↓
        MODULE 4: Query Coverage Check
        Did the answer actually address what was asked?
                ↓
        MODULE 5: Confidence Scorer
        Combine all signals into one trust score
                ↓
        MODULE 6: Decision Module
          ANSWER    → score ≥ 0.85, fully supported
          WARN      → score 0.60–0.84, partially supported
          REFUSE    → score < 0.60, insufficient support
          ESCALATE  → any contradiction found, safety critical
                ↓
        MODULE 7: Transparency Report Generator
          Layer 1: Trust Score (machine readable)
          Layer 2: Citation Trail (per claim sourcing)
          Layer 3: Natural Language Explanation (human readable)
                ↓
        Final Output Returned to User
```

---

## Verification Mechanisms

### Why Multiple Mechanisms

NLI alone fails on regulatory text because:
- It misses numerical mismatches (500°C vs 300°C both read as similar)
- It misses specific regulatory codes (OSHA 1910.147 vs 1910.212)
- It often misses conditional exceptions ("unless", "except when")
- It can be fooled by topical similarity without logical support

Each mechanism targets a specific failure mode:

| Mechanism | Failure Mode It Catches |
|---|---|
| NLI (deberta-v3) | Logical entailment failures |
| Entity & Number Matching | Numerical and code precision errors |
| Negation Detection | Conditional exceptions in regulatory text |
| Semantic Similarity | Topical drift and coverage gaps |

### Cascade Architecture

Mechanisms do not all run on every claim. Cheaper checks run first:

1. Semantic similarity runs first (fast gate — if too low, skip rest)
2. NLI runs second (if contradiction found → ESCALATE immediately)
3. Entity matching runs only if claim contains numbers or codes
4. Negation detection runs only if negation markers exist in evidence

---

## Pluggability

The Trust Layer defines a clean interface:

- **Input**: query (str), retrieved\_chunks (list), generated\_answer (str)
- **Output**: TrustReport (structured object with score, decision, citations,
  explanation)

Any RAG system that can provide these three inputs can use this Trust Layer
without modification to its own pipeline.

---

## Dataset

Primary dataset is sourced from Singh, Hamilton, White, Wise, Yousif, Carvalho,
Shan, Abrisham Baf, Mayyas, Cavuoto, and Megahed (2025), "A Multimodal
Manufacturing Safety Chatbot: Knowledge Base Design, Benchmark Development, and
Evaluation of Multiple RAG Approaches" (arXiv:2511.11847). Full dataset and
documents obtained directly from corresponding author Dr. Fadel Megahed
(Miami University).

### Knowledge Base (what RAG retrieves from)

16 documents across four categories, covering three machines (Bridgeport Manual
Mill, Haas TL-1 CNC Lathe, Universal Robots UR5e):

- **OEM Manuals**
  - Bridgeport Milling Machine (M-508, 2018) — pending from Megahed
  - Haas Lathe Operator's Manual (96-8910, Rev. J) — obtained
  - UR5e Universal Robots User Manual — obtained
- **OSHA Regulations (29 CFR 1910)**
  - 1910.147 — Lockout/Tagout
  - 1910.178 — Powered Industrial Trucks
  - 1910.211–1910.219 — Guarding to Mechanical Power Transmission
- **OSHA Technical Documents**
  - OSHA 3120 — Control of Hazardous Energy Lockout/Tagout
  - OSHA 3170 — Safeguarding Equipment & Protecting from Amputations
  - OSHA Technical Manual, Section IV Chapter 4 — Industrial Robot Safety
- **NIOSH Safety Alerts**
  - NIOSH 2011-156 — Lockout/Tagout to Prevent Injury During Maintenance
  - NIOSH 85-103 — Preventing the Injury of Workers by Robots

### Test Queries (what questions are asked)

161 expert-validated question/gold-answer pairs (deduplicated), covering all
three machines, obtained from Megahed's team. Questions were originally derived
from the OEM manuals (not the OSHA/NIOSH documents); OSHA/NIOSH documents serve
as supplementary grounding in the knowledge base that the RAG pipeline can draw
on when generating answers, even though no test questions were written
specifically from them.

Each question still needs to be labeled with an `expected_decision`
(ANSWER / WARN / REFUSE / ESCALATE) to serve as ground truth for evaluating the
Trust Layer's Decision Module — this labeling has not yet been done.

### Known Dataset Issues

- 11 rows have special character encoding errors (corrupted smart quotes/dashes
  from PDF extraction) — minor, fixable with a cleaning script
- Bridgeport Mill manual not yet received — follow-up sent to Megahed
- Megahed has been notified of the encoding issues

---

## Evaluation

The system is evaluated by comparing against a standard RAG baseline
(no trust layer) using:

| Metric | What It Measures |
|---|---|
| Hallucination Rate | Percentage of answers with unsupported claims |
| Groundedness Score | Degree of evidence support in returned answers |
| Decision Accuracy | Correctness of ANSWER/WARN/REFUSE/ESCALATE decisions |
| Coverage | Proportion of queries that receive an answer |

---

## Tech Stack

| Component | Tool |
|---|---|
| RAG Pipeline | LangChain |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers/all-mpnet-base-v2 |
| NLI Model | Not yet finalized — candidates: cross-encoder/nli-deberta-v3-base (laptop) or nli-deberta-v3-large (GPU) |
| NER and Negation | spaCy |
| LLM | Llama 3 or Mistral (local, open source) |
| Evaluation | RAGAS metrics |

---

## Project Folder Structure

```
rag-trust-layer/
│
├── data/
│   ├── raw/          ← knowledge base PDFs stored here (manuals, OSHA, NIOSH)
│   └── processed/    ← chunked text stored here
│
├── src/
│   ├── rag/
│   │   ├── loader.py      ← loads PDF documents
│   │   ├── chunker.py     ← splits documents into chunks
│   │   └── retriever.py   ← vector store and similarity search
│   │
│   ├── trust_layer/
│   │   ├── decomposer.py  ← claim decomposition
│   │   ├── verifier.py    ← NLI + entity + negation + semantic
│   │   ├── scorer.py      ← confidence scoring
│   │   ├── decision.py    ← ANSWER/WARN/REFUSE/ESCALATE logic
│   │   └── reporter.py    ← transparency report generation
│   │
│   └── main.py            ← runs the full pipeline
│
├── notebooks/
│   └── experiments.ipynb  ← evaluation experiments
│
├── tests/
│   └── test_trust_layer.py
│
├── requirements.txt
├── CONTEXT.md             ← this file
└── .gitignore
```

---

## Current Implementation Status

- [x] Project folder structure created
- [x] requirements.txt created
- [x] Virtual environment set up
- [x] Primary dataset obtained (161 Q&A pairs + 15 knowledge base documents)
- [ ] Bridgeport Mill manual (pending from Megahed) — NEEDS RECHECK: data/raw
      already has KneeMill-Complete-Manual.pdf, which may already be this
      (Bridgeport mills are commonly called "knee mills") — confirm before
      assuming it's still missing
- [x] Dataset cleaned (special character fix) and labeled with expected_decision
- [ ] NLI model finalized (base vs large)
- [x] Basic RAG pipeline working (loader, chunker, retriever) — verified live
      against a freshly rebuilt, clean Chroma index (17/17 current data/raw
      PDFs, no stale/orphaned entries)
- [x] LLM answer generation (generator.py) — llama3 via local Ollama,
      constrained to context-only answers
- [x] Full pipeline wired end-to-end (`run_pipeline()` in main.py):
      retrieve -> generate -> decompose -> verify -> score -> decide -> report
- [x] Trust layer modules implemented (core: Modules 1, 3, 5, 6, 7)
  - [x] Module 1: Claim Decomposer (decomposer.py)
  - [ ] Module 2: Retrieval Coverage Check
  - [x] Module 3: Multi-Mechanism Verifier (verifier.py)
  - [ ] Module 4: Query Coverage Check (deferred)
  - [x] Module 5: Confidence Scorer (scorer.py) — weighted mean, penalized
        by fraction of UNSUPPORTED/CONTRADICTION claims
  - [x] Module 6: Decision Module (decision.py) — ESCALATE checked first
        (overrides score thresholds), then ANSWER/WARN/REFUSE by score
  - [x] Module 7: Transparency Report Generator (reporter.py) — trust score,
        per-claim citation trail, natural-language explanation
- [ ] Evaluation framework built

---

## Next Steps (as of 2026-09-23)

The full pipeline is wired end-to-end and has been run against the real
knowledge base (not just fixtures): retrieve -> generate (llama3 via
Ollama) -> decompose -> verify -> score -> decide -> report. 45/45 tests
passing. See `docs/2026-08-07-errors-and-fixes.md` for the detailed writeup
of every bug found and fixed via end-to-end testing.

### What changed on 2026-10-11 — the groundedness review

30 of the 161 generated answers were read by the author against their own
retrieved evidence, blind to the system's decisions. This is the only
human-produced ground truth in the project. Worksheet:
`data/processed/answer_review_done.csv`.

```
AXIS 1  GROUNDED    26/30 = 87%   CI [70, 95]
AXIS 2  RELEVANT    22/30 = 73%   CI [56, 86]
AXIS 3  COMPLETE    18/30 = 60%   CI [42, 75]
```

**The model is not hallucinating.** 0 ungrounded, 0 contradicted, 4 partly
(qids 42, 48, 112, 126). qid 48 is the same case flagged in August as the one
unambiguous hallucination — found again independently, blind.

**The system refuses good answers.** Cross-tabulating the author's judgement
against what the system decided:

```
  your view        system said    n
  fully good       REFUSE         8
  fully good       WARN           4
  fully good       ANSWER         1
  off-target       REFUSE         7
  incomplete       REFUSE         6
  partly grounded  REFUSE         3
  partly grounded  WARN           1
```

Of 13 answers judged fully good — grounded, on-target and complete — the
system delivered 1 as ANSWER and refused 8.

Detection itself is not broken: 3 of the 4 **partly grounded** answers were
refused. The verifier is **miscalibrated, not blind.**

> ⚠ **CORRECTED 2026-10-14.** This group was written up as "fabricated".
> The author's own label was **"partly"**, and reading the four shows the
> word was wrong for three of them: q42 is an omission (drops the manual's
> "tolerance of 30 degrees"), q126 is incompleteness, q112 carries no note.
> Only **q48** is content the manuals do not support. Use "partly
> grounded" from here on; see `docs/thesis/facts.md` §11.

**The binding constraint is retrieval, not verification.** Counting what the
author's notes blame:

```
  14/30  retrieval
   9/30  answer does not address the question
   8/30  incompleteness
  10/30  gold answer quality
```

The sharpest case is qid 33: a Bridgeport question answered from the Haas
lathe manual, with the model openly stating the Bridgeport information was
absent. No amount of claim verification repairs that.

qid 115 is the counter-case and the author separated it correctly:
"the evidence is good and has all the points... but not the answer
generated." Retrieval succeeded; generation truncated.

#### What this means for the thesis

The research question was whether claim-level verification reduces the
delivery of unsupported answers. The measured answer in this corpus is that
**there are almost no unsupported answers to reduce**, and that the failures
which do occur are relevance and completeness — the two checks that were
designed and then deferred:

```
MODULE 2  Retrieval Coverage Check   designed, not built
MODULE 4  Query Coverage Check       designed, deferred
```

Both are implementable with `_semantic_similarity`, which already exists in
`verifier.py` and is currently only used claim-to-chunk:

```
Module 4   _semantic_similarity(question, answer)
Module 2   _semantic_similarity(question, chunk) over the k retrieved
```

These map onto established metrics rather than new ones — RAGAS defines
`faithfulness` (built), `answer_relevancy`, `context_precision` and
`context_recall` (all three missing). The gap can be stated in the field's
own vocabulary.

This is a finding, not a failure. "Verification-gated delivery was evaluated
in safety-critical manufacturing RAG; groundedness failures proved rare while
retrieval relevance and answer completeness dominated" is a more interesting
result than a favourable accuracy table, and it is defensible because it was
measured.

#### Caveats to carry into the write-up

```
n = 30, single annotator, wide intervals
author had access to gold answers while labelling
30 of 161 is a sample; the other 131 are unlabelled
the 4 "partly" rows are the only evidence of unsupported content,
and on re-reading (2026-10-14) only ONE of the four — q48 — is
```

---

### What changed on 2026-09-23

Two things reshaped the plan. Both came out of the thesis conversation now
archived at `docs/thesis-chat.md` (reference only — do not auto-load).

**1. Dr. Maier challenged the basis of the numbers.** The composite score,
the thresholds, and the negation modifier are currently arbitrary. The
resolution is not to justify the score — the score is an internal artifact
with no external referent. It is to validate the *outputs*: the verifier
against known labels (balanced accuracy + ROC-AUC, per SummaC/TRUE), and
the decision layer via risk-coverage analysis (per SABER and the selective
prediction literature). Thresholds get **derived** on a held-out validation
split against a stated risk tolerance, not chosen.

**2. A paper very close to this architecture exists.** arXiv:2605.21949,
"Claim-Selective Certification for High-Risk Medical RAG" — claim
decomposition, per-claim evidence scoring, four-way action selection
(state / state-with-conditions / contest / withhold ≈ ANSWER / WARN /
ESCALATE / REFUSE) in a safety-critical domain. The claim "no one has
formalised four-way decisions for RAG" is no longer available. What
survives: **post-hoc, answer-level middleware over an unmodified RAG
pipeline** (they intervene *during* response construction), a different
verification mechanism (NLI + entity + negation vs. their cue-based
relation scoring), and the manufacturing/regulatory domain.

### Natural-hallucination evaluation batch (2026-08-08)

Ran 10 questions sampled evenly across the 161-question gold set (every
16th row) through the full pipeline, no adversarial prompting. Result:
**0 ANSWER, 1 WARN, 8 REFUSE, 1 ESCALATE** — dataset expected ANSWER for 9
of these and ESCALATE for 1. Full stage-by-stage breakdown published at:
https://claude.ai/code/artifact/893447a6-fe4d-4a29-846b-fa20a5f7b47f
(**not saved in this repo** — see task B1).

This near-total REFUSE rate blocks everything downstream: with coverage at
zero, every decision-level metric is measuring a system that refuses
everything. Three possible causes, which produce an **identical** output
and must be told apart by hand before anything is changed:

- **Break #1 — verifier misjudges.** The claim IS in the chunk; NLI returns
  neutral anyway. Seen in Q64, where the LLM quoted the source almost
  verbatim and still scored UNSUPPORTED (that chunk has PDF-extraction
  damage — words run together). Likely aggravated by feeding 512-char
  chunks to a model trained on sentence pairs. → fix the input or the model.
- **Break #2 — the aggregation eats a good answer.** All claims judged
  correctly, but `mean × (1 − bad_fraction)` in `scorer.py` crushes the
  result. With one bad claim out of n, the score ceiling is `1 − 1/n`:
  0.50 at 2 claims, 0.67 at 3, 0.75 at 4. Answers decompose into 2–4
  claims, so **a single unsupported claim makes ANSWER (≥0.85)
  mathematically unreachable.** → change the aggregation.
- **Break #3 — nothing is broken.** Llama 3 genuinely hallucinated and the
  layer caught it. Unambiguous in Q48 ("not explicitly defined... we can
  infer", then four specifics stated anyway). → fix nothing; report it.

**Do not lower the thresholds to make the REFUSEs go away.** That cures the
symptom identically in all three cases, and in the Break #3 case it makes
the system deliver unsupported safety instructions — the exact thing the
thesis claims it prevents.

---

### A. Do now — no code, ~30 minutes total

1. **Email Dr. Maier.** Draft is in `docs/thesis-chat.md` (~line 28715).
   Currently building against a guess about what he meant. Two outcomes,
   both good: he confirms, or he names the real objection.
2. **Split the dataset.** `data/processed/qa_pairs_labeled.csv`, 161 rows
   → add a seeded `split` column, ~50 validation / ~111 test. Weights and
   thresholds are selected on validation ONLY; the test set is touched once
   at reporting time. Highest-leverage item in this file; without it every
   number reported is overfit and dismissible on those grounds.
3. **Confirm the Bridgeport manual.** `KneeMill-Complete-Manual.pdf` is in
   `data/raw` and in the rebuilt index. Bridgeport mills are commonly called
   knee mills — confirm this is the manual listed as "pending from Megahed"
   and close the open item.

### B. Diagnose before changing anything

1. **Re-run the 10-case batch with output saved to disk.** The existing
   breakdown only exists in the artifact above. Write full per-claim detail
   (claim, best chunk, all three NLI probabilities, each mechanism's score,
   verdict, trust arithmetic) to JSON so it can be re-read without
   re-running Ollama.
2. **Do the reading pass.** For each flagged claim, one question: *is this
   claim actually supported by the chunk it was checked against?* Then:
   claim IS supported but verdict UNSUPPORTED → Break #1; all claims judged
   right but answer still died → Break #2; claim genuinely not in the chunk
   → Break #3. **Count the proportions** — it will not be one clean cause.
   This is reading comprehension, not safety engineering; no domain
   expertise required. The same judgement is what Level 2 validation needs.

### C. Fixes — one at a time, measure between each

1. **Sentence-level NLI (do this first).** `chunker.py` uses
   `chunk_size=512`, so `verify_claim` hands DeBERTa a multi-sentence
   passage as premise. NLI models are trained on sentence pairs and degrade
   at passage level — this is the central finding of SummaC. Split the
   chunk into sentences, run the claim against each, take the max
   entailment. ~15 lines inside `verify_claim`, same model, no GPU. Put it
   behind a flag so old and new can run side by side on the same 10 cases.
   Citable as "following SummaC, verification at sentence granularity with
   max-aggregation."
2. **Fix the declined-answer bug (Q80).** When the LLM honestly says "there
   is no information about X in the context," the decomposer treats the
   decline as a factual claim and the verifier scores it CONTRADICTION →
   false ESCALATE. An honest "I don't know" must be recognised as a
   distinct case and not run through claim verification.
3. **Scorer aggregation** — only if the reading pass says Break #2
   dominates. Options: soft penalty instead of `(1 − bad_fraction)`, or a
   min/mean blend. Changing this invalidates any threshold selected
   beforehand, so it must precede the sweep.
4. **The NLI model is a swappable component — not just base vs. large.**
   Only revisit after C1 and a measurement. If sentence splitting fixes the
   under-scoring, staying on `base` is justified and the GPU setup is
   avoided; if not, the before/after number justifies moving. **Do not change
   the model and the input in the same step** — attribution is lost.

   The choice is wider than `deberta-v3-base` vs `deberta-v3-large`. It is a
   single constant (`NLI_MODEL_NAME`, `verifier.py:27`), so the verifier can
   host a different entailment model entirely. Candidates worth testing —
   **verify each is current and appropriate before committing**:

   ```
   cross-encoder/nli-deberta-v3-large   same family, bigger
   roberta-large-mnli                   long-standing MNLI baseline
   bart-large-mnli                      ditto
   MiniCheck (Tang et al., 2024)        purpose-built for
                                        document-grounded fact
                                        verification; already cited
                                        in EVALUATION_PLAN.md
   SummaC as a component                rather than only as a protocol
   ```

   MiniCheck is the most interesting of these: it is designed for exactly
   this task and for efficiency, and it is already in the citation table.

   **This is also a thesis argument, not only an implementation detail.**
   `EVALUATION_PLAN.md` already states that the contribution is the *layer*
   and the verification mechanism is a pluggable component inside it —
   "the architecture was designed to be mechanism-agnostic." Demonstrating
   that by running the same pipeline over two or three different entailment
   models makes that claim empirical rather than asserted, and it protects
   the thesis if Config C beats Config D: the finding becomes "the decision
   layer drives the improvement; verifier choice is a cost and auditability
   tradeoff," which is a result rather than a failure.

### D. Evaluation apparatus

0. **`expected_decision` is keyword-generated, not expert-labelled —
   validate it before any decision-accuracy number is reported.**
   `src/label_dataset.py` (2026-08-06) assigns the label by regex over the
   gold answer: "do not" / "never" / "must not" / a safety threshold ->
   ESCALATE, hedged -> WARN, otherwise ANSWER. No rule produces REFUSE,
   which is why the distribution is 121 ANSWER / 37 ESCALATE / 3 WARN /
   0 REFUSE across 161 questions.

   Consequence: every decision-accuracy, coverage and over-abstention
   figure currently rests on labels no human has checked. The confusion
   matrix in `evaluate_system.py` is only as good as these.

   ```
   □ Dr. Morkos reviews 15-20 labels
     -> EVALUATION_PLAN.md Layer 0.1 already calls for this
     -> lets you write "spot-checked by a domain expert"
        instead of "generated by keyword heuristics"

   □ Check the 0-REFUSE problem specifically
     Some of the 161 questions are probably NOT answerable
     from the knowledge base ("look up electricians in the
     area" is the example in EVALUATION_PLAN). The regex
     cannot produce REFUSE, so those are mislabelled ANSWER
     and the system is being penalised for correctly
     refusing them.

   □ Report inter-annotator agreement (Cohen's kappa) on the
     reviewed subset, per the Layer 0.1 plan

   □ Until this is done, state in Chapter 4 that decision
     labels are heuristic. Do not present decision accuracy
     as validated.
   ```

   NOTE: the groundedness labels being produced in
   `data/processed/answer_review.csv` are a DIFFERENT ground truth —
   human-produced, about whether a generated answer is supported by its
   retrieved evidence. Those do not depend on `expected_decision` and are
   unaffected by this issue.


1. **Tag the dataset** — `has_numerical_answer`, `has_conditional_language`,
   `difficulty`, `machine`. Gates the subset experiments (numerical,
   conditional), which are the strongest differentiating results.
2. **Freeze generation outputs.** Run all 161 and save query, retrieved
   chunks, and raw LLM answer to JSON *before* the trust layer touches
   them. Config A comes free from this, and it is the frozen input B, C
   and D all consume. Safe to do at any time — generation is identical
   under all three Breaks.
3. **Perturbation set (~100 pairs).** Take supported claims and reword or
   corrupt them in known ways; labels are known because the errors were
   made deliberately. Replaces hand-labeling 70+ claims. Include paraphrase
   pairs specifically — that tests the Break #1 weakness directly, and the
   before/after becomes a thesis result rather than an undocumented tweak.
4. **Verifier validation** — `balanced_accuracy_score` (primary, per
   SummaC) and `roc_auc_score` (secondary, per TRUE) against the
   perturbation labels. Two lines of scikit-learn.
5. **Unsupported-answer delivery rate.** *Of the answers actually delivered,
   what fraction contained a claim not in the evidence?* This is the
   headline metric and the y-axis of the main result. Coverage alone is the
   number that improves when the threshold is rigged; this is the number
   that gets worse.
6. **Threshold sweep → risk-coverage table.** Report coverage AND
   unsupported-delivery at each threshold. Then state the risk tolerance
   first and let it select the threshold: "maximise coverage subject to
   unsupported delivery below X% on the validation split." The judgement
   then lives in the tolerance (a defensible domain argument), not in the
   threshold. Expect an ugly derived number — round numbers read as guesses.
7. **Ablation** — NLI only → +entity → +negation → full. Doubles as an
   integration test: identical scores mean a mechanism isn't wired in. Do
   this INSTEAD of grid-searching the weights.
8. **Sensitivity analysis** for the verifier internals that can't be derived
   (`SIMILARITY_GATE`, the 0.30/0.70 blend). The goal is not to justify the
   value but to show the result doesn't depend on it: "varying the gate from
   0.15 to 0.35 changes balanced accuracy by under two points." If it swings
   sharply, that is itself important to know.
9. Module 2 (Retrieval Coverage Check) — not yet built. Justifiable via
   arXiv:2603.14170 (grounding abstention in retrieval confidence rather
   than generative uncertainty).
10. RAGAS harness for Config B, then Config C (LLM judge + decision
    thresholds). Shortcut worth considering: pass RAGAS faithfulness through
    the existing decision thresholds to get C while reusing B's plumbing.

### E. Small changes and issues found while reading (2026-09-23)

None of these change the research. They are cleanups, doc/code mismatches,
and two security items that are not cleanups at all.

#### E0. Security and licensing — RESOLVED / downgraded (2026-09-25)

```
✓ GitHub personal access token in .git/config
  → deleted on GitHub 2026-09-25 (it had also
    already expired). The string still sits in
    .git/config but is now dead.
  → OUTSTANDING: no SSH key exists on this machine,
    so pushing will not work until either
    `ssh-keygen -t ed25519` + the public key added
    to GitHub, or `gh auth login`. Not urgent —
    nothing needs pushing right now.

⚠ Copyrighted OEM manuals and Megahed's unpublished
  dataset are tracked in git:
    Haas Lathe Operator's Manual
    UR5e User Manual
    KneeMill Complete Manual
    multi_pdf_eval_deduplicated.xls
  → DOWNGRADED: the repo is private (verified —
    an unauthenticated GitHub API lookup returns
    404), so nothing is being redistributed. This
    is ordinary research practice.
  → BECOMES A CHECKPOINT before the repo is ever
    made public, shared with an examiner, or
    attached to a submission. Note provenance in
    the README now so this does not have to be
    rediscovered later.
  → OSHA/NIOSH documents are US government works
    and are fine to keep regardless.
```

#### E1. Code

```
□ verifier.py:73 — ENTAILMENT_THRESH is dead.
  Defined, never used anywhere. Its comment
  describes behaviour the code does not have.
  → delete it, or wire it in

□ Two different 0.60 thresholds, different jobs:
    SUPPORTED_SCORE  (verifier.py:74)  per CLAIM
    WARN_THRESHOLD   (decision.py:21)  per ANSWER
  Coincidence, not design. Rename before the
  threshold sweep or the wrong one gets moved.

□ retriever.py — Chroma distance metric is never
  configured, so the index uses Chroma's default
  ("space":"l2"), while verifier.py:78 computes
  cosine explicitly.
  → HARMLESS TODAY: all-mpnet-base-v2 has a
    Normalize layer, stored vectors are unit-length
    (verified: norm = 1.0000), and for unit vectors
    L2 and cosine rank identically
  → set the metric explicitly anyway, so it works
    by decision rather than by accident
  → REMEMBER FOR MODULE 2: the scales differ.
    cosine 0.25  ≡  L2 1.22
    Do not copy SIMILARITY_GATE across.

□ retriever.py:5 imports the deprecated
  langchain_community.vectorstores.Chroma
  → migrate to langchain_chroma

□ .gitignore — add *.zip and conversations.json
  so a Claude account export never lands in the repo

□ NLI model is one constant (NLI_MODEL_NAME,
  verifier.py:27), so swapping it is a trivial
  code change — but WHICH model to use is an
  experimental decision, not a cleanup.
  → see C4 for candidates and the argument

□ verifier.py:131 — dead branch. `if not
  claim_values:` can never be true; line 123
  already returned in that case. Leftover
  defensive code.

□ verifier.py:31-33 — the NLI label positions
  (_NLI_CONTRADICTION=0, _NLI_ENTAILMENT=1,
  _NLI_NEUTRAL=2) are hardcoded. Correct for
  this checkpoint (verified against its
  config.json), but DIFFERENT MODELS USE
  DIFFERENT ORDERS — roberta-large-mnli is
  {0: contradiction, 1: neutral, 2: entailment}.
  Swapping the model without updating these
  reads neutral where it expects entailment.
  Nothing crashes; every score is silently wrong.
  → read id2label from the model config at load
    time instead of hardcoding
```

#### E2. Documentation vs. implementation

```
□ The documented scoring formula is wrong.
  CONTEXT.md, EVALUATION_PLAN.md and the thesis
  chat all describe:
      0.50×NLI + 0.30×entity + 0.20×semantic
  verifier.py:206 actually computes:
      0.30×similarity + 0.70×entailment
  then applies entity and negation as MULTIPLICATIVE
  penalties (lines 215-218).
  → a two-term blend with two penalty multipliers,
    not a four-way weighted sum
  → fix before this reaches Chapter 3 or 4; it also
    appears in EVALUATION_PLAN's Validation section

□ verifier.py:140 — the entity-penalty comment
  describes behaviour the code does not have:
      comment: "each missing critical value
                halves the score"
      code:    score = ratio  (matched / total)
  They agree only when exactly half the values
  match. They differ critically at zero:
      halving → 0.5 ^ misses, never reaches 0
      ratio   → 0.0 when nothing matches
  With one critical value and one miss — the
  common case — halving gives ×0.5 while the
  code gives ×0.0, annihilating the claim score
  regardless of entailment.
  → DECIDE which behaviour is wanted, then make
    the comment and code agree. This is the same
    hard-multiplication pattern as the scorer
    problem in Break #2, one level down.
```

#### E3. EVALUATION_PLAN.md internal inconsistencies

```
□ Layer 0.5 was rewritten as the perturbation set,
  but two places still describe the old plan:
    - execution order step 5: "Hand-label ~70 claims
      for support (Layer 0.5)"
    - Triage / NECESSARY block: "Claim-level support
      labels — ~60-80 claims"
  → reconcile: perturbation set is primary,
    ~40 natural labels (0.6) is the optional
    external-validity check
```

#### E4. Chapter 1 draft (`docs/thesis/chapter-1-introduction.md`)

```
□ §1.2 — broken citation tag left in the prose:
    (cite index="53-1">"you risk safety"</cite>
  → normal quotation + [4]

□ §1.4 Objective 4 — the replacement text exists in
  EVALUATION_PLAN.md ("Revised Objective 4") and was
  never applied. Still says "against a standard RAG
  baseline."

□ §1.6 Contribution 6 — same problem, same fix
  (three comparison configurations, not one baseline)

□ §1.6 Contributions 2 and 4 — see
  docs/thesis/chapter-1-contributions-revision.md.
  Contribution 4's claim that "existing verification
  approaches report groundedness as an informational
  score" is now false as a general statement.

□ §1.5 — "the retrieval coverage check may flag
  insufficiency" describes Module 2, which is not
  built. Build it or move to future tense.

□ Terminology — "hallucination rate at output"
  (§1.5, §1.7) vs "unsupported-answer delivery rate"
  (EVALUATION_PLAN). Same construct, two names.
  Unify on the latter throughout.
```

#### E5. Resolved — no longer outstanding

```
✓ EVALUATION_PLAN.md recovered (was believed lost
  to the claude.ai sandbox; the user had a copy)

✓ arXiv:2605.21949 read in full (2026-09-23).
  Confirms: they decompose the QUERY into templated
  claim skeletons before a response exists
  ("Given a query q, the decomposition layer emits
  verifiable claim skeletons", §4.2) and position
  themselves as operating "earlier in the pipeline,
  before the final response is formed" (§2).
  The post-hoc differentiation HOLDS.
  Single-author v1 preprint, company affiliation,
  no venue. Their weak labels agree with human audit
  on 73/100 (κ = 0.5027, §5.3), and metadata-only
  shortcut controls beat their full selector on
  action accuracy (§6.1).
  → the ⚠ flags in chapter-1-contributions-revision.md
    can now be cleared
```

### F. Reading and positioning

1. **arXiv:2605.21949 — read fully, this week.** Closest prior work. Check
   peer-reviewed vs. preprint, and confirm they intervene during generation
   (that is the differentiation). Write the differentiation paragraph
   explicitly; do not let a committee member find it first.
2. **SummaC (arXiv:2111.09525)** — evaluation section only. Why balanced
   accuracy, how thresholds were selected. Skip the architecture. Also the
   source for the sentence-granularity fix in C1.
3. **SABER (arXiv:2605.18792)** — the threshold sweep table and how
   coverage/risk-on-answered are defined and presented. Skip the training.
4. **Kernan Freire et al. (arXiv:2401.05200)** — results and discussion.
   Operator quotes, night-shift scenario. This is the Chapter 1 motivation.
5. **Drop the novelty claim** about four-way decisions wherever it appears;
   reposition on the post-hoc middleware property.
6. **Reconstruct `EVALUATION_PLAN.md`.** It was written into the claude.ai
   sandbox and never landed in this repo — it exists only as tool-call text
   in `docs/thesis-chat.md` (lines ~26892–28043), which is fully
   recoverable. Until then the evaluation plan lives in a 30k-line chat log.

### Dependencies

```
B (diagnosis)  → blocks C2/C3/C4 — three causes, three different repairs
C (fixes)      → block D6 — a scorer change voids any threshold selected before it
A2 (split)     → blocks ALL defensible reporting
D1 (tagging)   → blocks the subset experiments
D3 (perturb)   → blocks verifier validation; independent of C, safe anytime
D2 (freeze)    → independent of everything; safe anytime
```

One thing to hold on to: if the reading pass says Break #3 dominates, that
is **not** a failed thesis. "The trust layer correctly identifies these
answers as unsupported; system utility is bounded by generation quality,
not verification" is a real finding about deploying local RAG in
safety-critical manufacturing. What fails a thesis is a good number that
cannot be explained.

### What changed on 2026-10-14 — the four fixes, and what they bought

The diagnosis from 13 October held up: **Module 1 was the bottleneck, not
Module 3.** Entailment collapses as the CLAIM (the NLI hypothesis)
lengthens — mean 0.69 under 12 words, 0.16 at 26+, with similarity moving
the OPPOSITE way, which rules out the "long claims are off topic" confound.

Four changes, each measured against the 30 answers the author read and
labelled herself. Aggregate coverage was reported but never used to accept
anything — that rule exists because every change on 13-14 October passed on
aggregates and failed on ground truth.

**Step 1 — atomic decomposition** (`decomposer.py`)

  - sentence-split INSIDE list items. The list regex gave the final item
    everything to the end of the answer, so q126 was one 123-word "claim"
    made of six sentences.
  - detach non-restrictive relative clauses and appositives, carrying the
    subject over. Restrictive ones are left alone: removing the clause that
    says WHICH thing is meant broadens the claim and makes it easier to
    support, which is the wrong direction for a safety filter.
  - distribute a shared subject, auxiliaries, negation and any leading
    condition across coordinated verbs. A condition is never detached on
    its own — "When MM is selected, units are millimetres" does not entail
    "units are millimetres".
  - strip citations BEFORE parsing. Left in, "[Source: KneeMill-Complete-
    Manual.pdf p.30]" parsed as a noun phrase and became the SUBJECT of a
    claim.
  - R7: drop claims about what the documents DO NOT say. "There is no
    specific mention of a Bridgeport mill in the provided manual" came back
    CONTRADICTION at p=0.98 against a manual about Bridgeport mills — the
    model penalised for admitting it does not know.
  - an answer whose claims were ALL dropped as non-claims now returns [],
    where the old fallback handed the verifier back the raw answer.

  Four of my own splitting bugs were caught by reading the output rather
  than the totals, and are worth recording because each one raised the
  contradiction count while looking like progress: glued non-adjacent spans
  ("The documents only provide information on to loosen the drawbar"),
  duplicated carried function words ("are are the basis"), a missing space
  at the cut ("The R8 colletis tightened"), and a stray comma left where a
  clause was removed. Splits are now rejected unless every piece re-parses
  to a verbal root with no repeated word.

**Step 2 — max over granularities: tested and REJECTED.** On real labelled
claims it raises good claims by 0.001 and partly-grounded ones by 0.111,
collapsing separation from 0.378 to 0.102. Third time a maximum has
inflated false positives in this project.

**Step 3 — the ESCALATE rule.** Only the chunk the retriever ranked MOST
SIMILAR may raise a contradiction, replacing the max over all five.
Measured over the 30:

```
rule                   false ESCALATE on     CONTRADICTION
                       13 fully-good         claims / 429
winning chunk only            0                    1     unreachable
top similarity                0                   11     <- selected
second-highest                2                   11
max, threshold 0.9            2                   20
max over all chunks           3                   40
```

Every rule delivers the same answers. The ESCALATE rule changes nothing
except how often a sound answer is accused of contradicting the manual.

**Step 4 — the scorer.** `AGGREGATOR = "min"` (SummaC-ZS), replacing
`mean x (1 - bad_fraction)`. The old rule returns EXACTLY 0.000 for a
single-claim answer whose claim is flagged, and `proportion` is equally
binary; 21 of 161 answers have one claim and 31 have none, so for a third
of the benchmark the score carried no information. `WARN_THRESHOLD` moved
0.60 -> 0.30 because "min" measures a different quantity — swept 0.05 to
0.95, and 0.25/0.30/0.35 all give the same result, so 0.30 is the centre of
the stable region, not an edge.

**Result against the 30 labelled answers** (THEN = when she labelled):

```
                      THEN    NOW        criterion set before the work
FULLY GOOD delivered  5/13    6/13       must rise above 5     PASS
false ESCALATE on     0/13    0/13       must fall below 4     PASS
  fully good
partly-grounded        3/4     3/4       must stay >= 3        PASS
  withheld
off-target delivered   0/7     1/7       must stay <= 1        PASS
```

Claim level, all 161 answers: mean entailment 0.427 -> 0.525, median 0.017
-> 0.886, SUPPORTED 39% -> 49%, CONTRADICTION 53 -> 11, median claim length
18 -> 15 words. 74 tests passing.

**Two corrections made on 14 October, recorded because both would have
reached the supervisors:**

  1. **"FABRICATION" was the wrong word** for the four answers the author
     marked "partly". Only q48 contains content the manuals do not support;
     q42 is an omission and q126 is incompleteness. The system's behaviour
     is unchanged — the criterion still passes 3/4 — but what that criterion
     *guarantees* is weaker than the name implied. See `facts.md` §11.

  2. **The length claim was too broad.** "NLI degrades with hypothesis
     length" is contradicted by this project's own perturbation data: at
     sentence granularity, mean entailment on supported pairs is FLAT
     across 0-15 to 30+ words (0.868 -> 0.911). The effect appears only on
     real decomposer output, so it belongs to decomposition, not to the
     model. A follow-up hypothesis — that proposition count rather than
     length is the driver — was tested and did NOT hold: at 12-20 words,
     1 / 2 / 3+ clauses give 0.548 / 0.554 / 0.551, and length vs clause
     count correlate at rho +0.763, so the two cannot be separated in this
     corpus. Both the control condition and the failed hypothesis are
     written up in `facts.md` §10.

**Honest limits, for Chapter 6:**

  - The headline gain is ONE answer out of 13. On n=13 that is not a
    reliable effect. What IS reliable is the claim-level movement and the
    disappearance of the false contradictions.
  - The target of "most claims under 12 words" was NOT met — median 15,
    35% under 12. The remaining long claims are single propositions with
    restrictive modifiers that cannot be split without weakening them.
    Entailment still falls with length inside the new distribution (0.68
    under 12 words, 0.22 at 26+), so there is more to gain here.
  - `WARN_THRESHOLD` was selected on 30 answers. It needs revisiting once
    Dr. Morkos has validated more labels. `src/calibrate.py` derives it
    from a stated risk tolerance instead.
  - "min" is the rule most sensitive to one bad claim, so it is biased
    against long answers. q100 (5 claims) and q114 (6) sit on that line.
  - None of SummaC, TRUE or Glover et al. reports NLI accuracy as a
    function of HYPOTHESIS length — they all vary the premise. That gap is
    what `decomposer.py` controls, and it is worth stating as a
    contribution.

---

## Key Research Contribution

This project contributes a **post-generation accountability system** — not a
fix to hallucination inside the LLM, but a filter that prevents hallucinated
answers from reaching users. The system operates at output level, which is where
hallucination matters most in safety-critical deployments.

The hallucination still occurs inside the LLM. This system intercepts it before
delivery.

---

## Generalisation Argument

The same framework works across industries by adjusting weights:

| Industry | Most Critical Mechanism | Weight Adjustment |
|---|---|---|
| Manufacturing Safety | Entity/Number Matching | w_entity increased |
| Medical | Entity/Number Matching | w_entity increased |
| Legal | Negation Detection | w_negation increased |
| Financial | Entity/Number Matching | w_entity increased |

Same modules, same pipeline, different tuning per domain.

---

## Future Considerations (Discussed, Not Yet Built)

### Query Coverage Check

During design discussions, a gap was identified: the current architecture
verifies whether claims in an answer are *supported* by evidence, but does not
check whether the answer actually *addresses* the full query. A high-confidence
answer could still ignore parts of the question (e.g., a query asking about
temperature limits AND PPE requirements, where the answer only covers PPE).

A proposed **Module: Query Coverage Check** would decompose the query into
sub-questions and check whether the answer addresses each one, producing a
separate coverage score to combine with the verification score. This was
deferred for scope reasons — revisit if time allows after the core Trust Layer
(Modules 1–6) is working end-to-end.

---

## Important Notes for Implementation

- The RAG pipeline is infrastructure, not the contribution
- The Trust Layer is the research contribution
- RAGAS is used only for evaluation metrics, not as the pipeline
- All models should run locally where possible (no API dependency)
- The virtual environment must be activated before running anything:
  `source venv/bin/activate`