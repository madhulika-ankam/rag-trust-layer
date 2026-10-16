# Facts sheet — every number Chapters 3, 4 and 5 need

Compiled 14 October 2026, read out of the code and the data rather than
from notes. **Write from this file, not from the code.** Digging through
source for a threshold mid-paragraph is what turns a three-day chapter into
a six-day chapter.

Every row names where it came from. If a number here disagrees with one in
`CONTEXT.md` or `EVALUATION_PLAN.md`, this file is the later one — but check
the source before trusting either.

---

## 1. Corpus

| item | value | source |
|---|---|---|
| Raw documents | 17 PDFs | `data/raw/` |
| OEM manuals | 3 | see below |
| Regulatory / guidance documents | 14 | 29 CFR 1910 parts, OSHA 3120/3170, OSHA Technical Manual §IV ch.4, NIOSH 85-103, 2011-156 |
| Chunking | `RecursiveCharacterTextSplitter`, size **512**, overlap **64** | `src/rag/chunker.py:4` |
| Full index | **3,964 chunks** | `data/chroma` |
| OEM-only index | **2,285 chunks** | `data/chroma_oem_only` |
| Embeddings | `sentence-transformers/all-mpnet-base-v2` | `src/rag/retriever.py:7` |
| Retrieval | cosine similarity, **k = 5** | `src/rag/retriever.py:37` |

The three OEM manuals:

| machine | file |
|---|---|
| Bridgeport Series I knee mill | `KneeMill-Complete-Manual.pdf` |
| HAAS lathe (NGC control) | `english---lathe-ngc---operator_s-manual---2018.pdf` |
| Universal Robots UR5e | `710-965-00_UR5e_User_Manual_en_Global.pdf` |

**Two indexes, and why.** The OEM-only index exists because the regulatory
documents dominated retrieval for machine-specific questions. Chapter 3 must
state which index each reported run used. The frozen generations in
`data/processed/generations.jsonl` used the **full** index.

> ⚠ **UNRESOLVED:** `unverified.md` §E records a 153-vs-161 question-count
> discrepancy. Both `qa_pairs_clean.csv` and `qa_pairs_labeled.csv` contain
> **161** rows, so 153 must come from an earlier version or from the source
> dataset. Resolve or state it as a limitation — do not quote 153 anywhere.

---

## 2. Question set and labels

| item | value | source |
|---|---|---|
| Questions | **161** question / gold-answer pairs | `data/processed/qa_pairs_clean.csv` |
| `expected_decision` = ANSWER | **121** | `generations.jsonl` |
| `expected_decision` = ESCALATE | **37** | " |
| `expected_decision` = WARN | **3** | " |
| How labels were produced | rule-based heuristic over the gold answers; the trigger phrase is recorded per row | `qa_pairs_labeled.csv`, column `label_reason` |
| Independent validation | **none yet** — 20 sent to Dr. Morkos 14 Oct | `data/processed/label_review_morkos.csv` |

**Chapter 4 must say, until Dr. Morkos replies:** decision labels are
heuristic, and decision accuracy against them is reported as indicative,
not validated. This is `CONTEXT.md` §D0 and it is not optional.

Note the label distribution is badly skewed — 121 / 37 / 3, and **zero**
REFUSE. Any decision-accuracy figure has to be read against that baseline.

---

## 3. Generation

| item | value | source |
|---|---|---|
| Model | **Llama 3** via local Ollama | `src/rag/generator.py:35` |
| Endpoint | `http://localhost:11434/api/generate` | `:34` |
| Temperature | **0.0** | `:87` |
| Prompt mode (default) | `guarded` | `:74` |

The three prompt variants, verbatim at `src/rag/generator.py:37-73`:

- **`minimal`** — context, question, "Answer:". No behavioural instruction.
  The closest thing to the unverified baseline Config A represents.
- **`grounded`** — adds "Answer the question using ONLY the information in
  the context below. Do not use any outside knowledge."
- **`guarded`** — adds, on top of `grounded`, "If the context does not
  contain enough information to answer the question, say so explicitly
  instead of guessing."

> ⚠ **THE CONFOUND, and it must be stated in Chapters 3, 5 and 6.** Every
> frozen generation used `guarded`. The abstention instruction is doing work
> that the trust layer is then measured on top of. A fair statement of the
> result is "a verification layer added to an *already-guarded* pipeline",
> not "a verification layer added to RAG".

### Cost and latency

| item | value | source |
|---|---|---|
| Retrieval, mean | **0.03 s** | `src/evaluate_system.py` |
| Generation, mean | **1.85 s** | " |
| End to end, mean | **1.88 s** | " |
| Cost per query | **$0.00** (local inference) | " |
| Comparator | Singh et al. (arXiv:2511.11847): 86.66% accuracy, $0.005/query, 10.04 s | " |

---

## 4. Trust layer configuration

Every constant, with how it was set. **"Chosen by hand" is written where
that is the truth** — a stated weakness with a measured alternative beside
it is defensible; an unexplained constant is not.

| constant | value | how it was set | source |
|---|---|---|---|
| `EMBED_MODEL_NAME` | `all-mpnet-base-v2` | same embedder as retrieval, by design | `verifier.py:25` |
| `NLI_MODEL_NAME` | `cross-encoder/nli-deberta-v3-base` | chosen; `-large` tested and did not improve | `:26` |
| `NLI_GRANULARITY` | **`sentence`** | **measured** — see §6 | `:143` |
| `MIN_NLI_SENT_CHARS` | 15 | set by a failing test: "Power must be disconnected." is 27 chars | `:146` |
| `SIMILARITY_GATE` | 0.25 | chosen by hand | `:92` |
| `CONTRADICTION_THRESH` | 0.50 | chosen by hand | `:93` |
| `SUPPORTED_SCORE` | 0.60 | chosen by hand | `:95` |
| similarity / entailment weights | **0.30 / 0.70** | chosen by hand, then **validated against a fitted alternative** — see §5 | `:346` |
| ESCALATE rule | only the **top-similarity** chunk may raise a contradiction | **measured** — see §7 | `:367+` |
| `AGGREGATOR` | **`min`** (SummaC-ZS) | **measured** — see §8 | `scorer.py` |
| `ANSWER_THRESHOLD` | 0.85 | carried over, not re-swept | `decision.py:20` |
| `WARN_THRESHOLD` | **0.30** | **swept 0.05–0.95**; 0.25/0.30/0.35 tie, so this is the centre of the plateau | `decision.py` |

### Claim decomposition (Module 1)

Normalisation rules R1–R7 in `src/trust_layer/decomposer.py`:

| rule | what it does |
|---|---|
| R1 | strips meta-framing ("According to the context, it is stated on page 30:") |
| R2 | strips conversational connectors ("Therefore, yes,") |
| R4 | **drops** claims about where information sits in a document |
| R5 | strips inline citations, round and square brackets, one level of nesting |
| R6 | strips markdown emphasis and leading punctuation |
| R7 | **drops** claims about what the documents do NOT say |

Atomic splitting, added 14 October: sentence-split inside list items;
detach non-restrictive relative clauses and appositives carrying the
subject over; distribute shared subject, auxiliaries, negation and leading
conditions across coordinated verbs. **Restrictive** relative clauses and
**conditions** are never detached — doing so broadens the claim, which for
a safety filter is the wrong direction.

### Modules not built

| module | status | reason for Chapter 3 |
|---|---|---|
| 2 — Retrieval coverage | not built | out of scope, no time |
| 4 — Query coverage | **built and abandoned** | detected 1 of 8 off-target answers; `src/trust_layer/relevance.py` retained as negative result |

---

## 5. Perturbation benchmark — verifier validation

| item | value |
|---|---|
| Pairs | **302** |
| Split | **152 validation / 150 test**, fixed seed, by `pair_id` |
| Labels | 169 supported / 133 unsupported |
| Rows failing the similarity gate | 4 |
| Corruption types | numerical, negation_inverted, code_swap, term_swap, condition_dropped, unsupported_addition |
| Protocol follows | BUMP (Ma et al., ACL 2023) and FactCC |
| Source | `data/processed/perturbations.csv`, built by `src/build_perturbations.py` |

### Results, held-out test split (n = 150), sentence granularity

Command: `venv/bin/python -m src.evaluate_verifier --features data/processed/features_sentence.csv`

| combination rule | threshold | BA validation | BA test | AUC test |
|---|---|---|---|---|
| entailment only | 0.664 | 0.8865 | 0.9309 | 0.9707 |
| 0.5 sim + 0.5 entail | 0.533 | 0.8865 | 0.9309 | 0.9757 |
| **0.3 sim + 0.7 entail (production)** | 0.692 | 0.8842 | **0.9188** | **0.9754** |
| 0.7 sim + 0.3 entail | 0.499 | 0.8830 | 0.9475 | 0.9755 |
| fitted logistic regression | 0.761 | 0.8865 | 0.9309 | 0.9757 |

**This is the answer to Dr. Maier.** The hand-set 0.30/0.70 weighting
performs within **0.0003 AUC** of coefficients fitted by logistic regression
on held-out data. It is not a justified constant, but it is a constant with
a measured alternative showing it costs nothing.

Fitted coefficients (log-odds of `supported`): entailment 2.27, entity 2.66,
similarity 0.43, contradiction −1.17, negation −0.14, intercept −3.11.

### Ablation, cumulative in pipeline order (test split)

| configuration | BA test | AUC test |
|---|---|---|
| NLI only | 0.9309 | 0.9628 |
| + semantic similarity | 0.9309 | 0.9594 |
| + entity matching | 0.9309 | **0.9754** |
| + negation checking (full) | 0.9188 | 0.9754 |

Entity matching carries the gain. Similarity slightly *reduces* AUC on this
set; negation costs a little balanced accuracy. Say so — an ablation where
every component helps is usually an ablation that was not run honestly.

### Detection by perturbation type (test split, production rule)

| type | detected | note |
|---|---|---|
| numerical | 25/25 | |
| code_swap | 17/17 | |
| negation_inverted | 6/6 | n < 20 |
| condition_dropped | 6/7 | n < 20 |
| term_swap | 5/6 | n < 20 |
| unsupported_addition | 6/6 | n < 20 |
| SUPPORTED controls kept | 72/83 | |

Report as counts, not percentages. At n = 6 a percentage implies precision
the data cannot support.

---

## 6. NLI granularity — settled 14 October

Command: `venv/bin/python src/experiments/granularity.py`

| | perturbation test split | 30 labelled answers | | | |
|---|---|---|---|---|---|
| | AUC / BA | good delivered | false ESCALATE | partly-grounded withheld | SUPPORTED claims |
| **sentence** | **0.975 / 0.919** | **6/13** | **0/13** | **3/4** | **211/429** |
| chunk | 0.930 / 0.873 | 4/13 | 1/13 | 2/4 | 167/429 |

Sentence wins on both sets, on every criterion.

### It wins at every claim length, not just on average

Command: `venv/bin/python src/experiments/granularity_by_length.py`

The aggregate above could hide a trade — sentence better for short claims,
chunk better for long ones. It does not. The same 302 labelled pairs, scored
both ways, with AUC computed **within** each length band:

| claim words | n | AUC chunk | AUC sentence | difference |
|---|---|---|---|---|
| 0–15 | 57 | 0.817 | **0.871** | +0.054 |
| 15–20 | 58 | 0.856 | **0.926** | +0.070 |
| 20–30 | 91 | 0.958 | **0.982** | +0.024 |
| 30+ | 96 | **0.969** | 0.968 | −0.001 (tie) |
| all | 302 | 0.920 | **0.952** | +0.032 |

Sentence never loses. The −0.001 at 30+ words is noise.

**Worth a paragraph in Chapter 3:** before the decomposer was fixed, the two
sets *disagreed* and chunk looked better on real claims. That was an
artefact — claims were long enough that the length effect swamped the
comparison. Granularity choice and decomposition granularity interact, so
measuring one while the other is broken gives the wrong answer.

> ⚠ The *mechanism* behind the old chunk advantage is **not established**.
> A plausible story is that sentence granularity gives a long claim many
> chances to find a partial match — 5 chunks × ~5 sentences — and that this
> leniency helped unsupported claims as much as supported ones. That is
> speculation and has not been tested. Do not present it as a finding.

The deciding case is **q42**, an answer the author marked *partly grounded*:
the generated answer drops the manual's "tolerance of 30 degrees" from a
safety condition. Chunk granularity returns ANSWER on it at full confidence;
sentence granularity withholds it.

---

## 7. ESCALATE rule — settled 14 October

Command: `venv/bin/python src/experiments/escalate_rules.py`

| rule | false ESCALATE on 13 fully-good | CONTRADICTION claims / 429 |
|---|---|---|
| winning chunk only | 0 | 1 — effectively unreachable |
| **top similarity (production)** | **0** | **11** |
| second-highest contradiction | 2 | 11 |
| max over chunks, threshold 0.9 | 2 | 20 |
| max over all chunks | 3 | 40 |

**Every rule delivers the same answers.** It changes nothing except how
often a sound answer is accused of contradicting the manual.

Known limitation for Chapter 6: if two documents genuinely disagree and the
more similar one supports the claim, the disagreement is not surfaced.

---

## 8. Answer-level aggregation — settled 14 October

Command: `venv/bin/python src/experiments/aggregator_comparison.py`

Under the constraint set *before* the work (≥3 of the 4 partly-grounded
answers withheld, ≤1 of 7 off-target delivered). Note what that criterion
actually guarantees after the §11 renaming: it says the system withholds
answers that are **incomplete or partly supported**, which is a weaker and
different promise from "it catches fabrication". State it the weaker way.

| aggregator | best threshold | fully-good delivered |
|---|---|---|
| `current` — mean × (1 − bad fraction) | 0.60 | 5/13 |
| `proportion` — RAGAS faithfulness | 0.80 | 5/13 |
| `mean` | — | never above 5 within the constraint |
| **`min` — SummaC-ZS (production)** | **0.30** | **6/13** |

The reason to switch is not the one answer of difference. It is that
`current` and `proportion` are both **binary at n = 1**: an answer with one
flagged claim scores exactly 0.000. **21 of 161 answers have exactly one
claim and 31 have none**, so for about a third of the benchmark the old
score carried no information.

Known cost: `min` is the rule most sensitive to a single bad claim, so it is
biased against long answers. q100 (5 claims) and q114 (6) sit on that line.

---

## 9. Claim-level results

| | before decomposer fix | after |
|---|---|---|
| Claims from 161 answers | 392 | **429** |
| Median claim length (words) | 18 | **15** |
| Mean claim length | 19.6 | 16.1 |
| Claims under 12 words | 25% | **35%** |
| Mean entailment | 0.427 | **0.525** |
| Median entailment | 0.017 | **0.886** |
| SUPPORTED | 39% | **49%** |
| CONTRADICTION verdicts | 53 | **11** |

Files: `data/processed/verified_before_decomposer_fix.jsonl` and
`data/processed/verified.jsonl`.

Also: 24 answers were whole-answer declines, and 31 produced zero claims
after R4/R7 dropping.

---

## 10. The length effect — the central finding

Command: `venv/bin/python src/experiments/length_effect.py [verified file]`

### Before the fix (n = 392 claims)

| claim words | n | mean entailment | median | % SUPPORTED | mean similarity |
|---|---|---|---|---|---|
| 0–8 | 35 | 0.686 | 0.982 | 63% | 0.391 |
| 8–12 | 62 | 0.699 | 0.989 | 65% | 0.513 |
| 12–16 | 70 | 0.515 | 0.833 | 50% | 0.537 |
| 16–20 | 58 | 0.375 | 0.006 | 36% | 0.535 |
| 20–26 | 72 | 0.373 | 0.007 | 31% | 0.595 |
| 26+ | 95 | 0.162 | 0.002 | 13% | 0.631 |

Spearman: length vs entailment **ρ = −0.353, p = 5.71e-13**;
length vs similarity **ρ = +0.370, p = 3.91e-14**.

### After the fix (n = 429 claims)

| claim words | n | mean entailment | median | % SUPPORTED | mean similarity |
|---|---|---|---|---|---|
| 0–8 | 54 | 0.667 | 0.984 | 63% | 0.399 |
| 8–12 | 95 | 0.680 | 0.987 | 64% | 0.533 |
| 12–16 | 81 | 0.616 | 0.970 | 59% | 0.555 |
| 16–20 | 65 | 0.472 | 0.297 | 45% | 0.549 |
| 20–26 | 72 | 0.418 | 0.008 | 36% | 0.588 |
| 26+ | 62 | 0.224 | 0.004 | 21% | 0.635 |

Spearman: entailment **ρ = −0.281, p = 2.97e-09**;
similarity **ρ = +0.326, p = 4.70e-12**.

**The argument, in three steps:**

1. Entailment falls steeply with claim length — 0.675 mean under 12 words,
   0.329 at 20 or more.
2. Similarity moves the **opposite** way (0.484 → 0.609). Long claims are
   *more* on topic and *less* entailed, so this is not a relevance confound.
3. Causally confirmed: rewriting claims without changing meaning moved
   entailment 0.000 → 0.996 (q23, 23 words → 6) and 0.002 → 0.992 (q93).

### The control condition — where the effect does NOT appear

Command: `venv/bin/python src/experiments/granularity_by_length.py`

**This is the most important table in the file, and it narrows the claim.**

Mean entailment on perturbation pairs labelled *supported* — claims that
genuinely are entailed, so they should score high at any length:

| claim words | n | chunk | sentence |
|---|---|---|---|
| 0–15 | 32 | 0.395 | **0.868** |
| 15–20 | 33 | 0.386 | **0.721** |
| 20–30 | 49 | 0.476 | **0.894** |
| 30+ | 55 | 0.519 | **0.911** |

At sentence granularity the collapse **does not happen**. Entailment is flat
across the whole range and if anything rises — 0.868 at under 15 words,
0.911 at 30 or more. Same NLI model, same granularity, opposite result to
the real claims above.

The difference is in what the claims *are*. Perturbation claims are single
propositions lifted from a manual; they are simply long. Real long claims
are long because they **bundle several facts together**, and no single
sentence of evidence supports all of them at once.

### A hypothesis that was tested and did NOT hold

Command: `venv/bin/python src/experiments/length_or_propositions.py`

The obvious follow-up: if composition rather than length is the cause, then
holding length fixed and varying the number of propositions should move
entailment. It does not.

| 12–20 word claims | n | mean entailment | % SUPPORTED |
|---|---|---|---|
| 1 clause | 25 | 0.548 | 48% |
| 2 clauses | 55 | 0.554 | 55% |
| 3+ clauses | 66 | 0.551 | 53% |

Flat. Clause count adds nothing at this length. At 20+ words it does appear
to matter (2 clauses 0.441, 3+ clauses 0.295) but the first cell is n = 14.

The two predictors cannot be separated in this corpus: length vs clause
count correlate at **ρ = +0.763 (p = 4e-83)**, and only 11 claims are long
*and* single-clause, so the clean test has no sample behind it.

**Report this as a negative result.** "Is it length or complexity?" is a
question an examiner will ask, and "we tested; our data cannot separate
them, and here is why" is a far better answer than an untested assertion.

### What may be claimed, and what may not

❌ **DO NOT WRITE:** *"NLI accuracy degrades with hypothesis length."* The
control condition above contradicts it. At sentence granularity this model
handles 30-word single-proposition hypotheses perfectly well. Writing the
broad version hands an examiner a refutation drawn from the thesis's own
appendix.

✅ **The defensible claim:**

> On real decomposer output, verification quality degrades sharply with
> claim length (ρ = −0.281, p = 3e-09), while semantic similarity over the
> same claims moves in the opposite direction (ρ = +0.326), ruling out
> topical relevance as the cause. The same model, at the same granularity,
> shows **no such degradation on single-proposition claims of equal
> length**. The effect is therefore a property of how generated answers are
> decomposed, not of the model's tolerance for long hypotheses.

That is narrower than the first version and **better evidenced**, because
it comes with its own control condition. It survives the obvious challenge
("how do you know it isn't just long text?") instead of being sunk by it.

**The literature position:** SummaC (TACL 2022), TRUE (NAACL 2022) and
Glover et al. (GEM 2022) all vary **premise** length. None reports accuracy
against **hypothesis** length — the variable a decomposer controls. Frame
this as an unexamined variable that this thesis measures, not as a defect
in the models. Verify the gap claim once more before Chapter 2 asserts it.

The effect **persists after the fix**, which is why claim length stays in
Chapter 6 as future work.

---

## 11. The 30 human-labelled answers — the ground truth

Protocol: the author labelled 30 answers blind to the system's decision.
Worksheet `data/processed/answer_review.csv`, labels
`answer_review_done.csv`, system decisions withheld in `answer_review_key.csv`.

| her judgement | n | delivered before | delivered now | false ESCALATE now |
|---|---|---|---|---|
| fully good | 13 | 5 | **6** | **0** |
| incomplete but grounded | 6 | 0 | 0 | 1 |
| off-target | 7 | 0 | 1 | 0 |
| **partly grounded** | 4 | 1 | 1 | 1 |

Command: `venv/bin/python src/experiments/ground_truth_table.py`

> ⚠ **NAMING, corrected 14 October.** The fourth group was called
> "FABRICATION" in earlier drafts of this file and in `CONTEXT.md`. That was
> an analysis-script label, not the author's. Her own word was **"partly"**,
> and reading the four shows most of them are not fabrication at all:
>
> | qid | her note | what it actually is |
> |---|---|---|
> | q42 | missed "tolerance of 30degrees", present in the evidence | **omission** |
> | q48 | "says something that is not backed by the evidence" | **unsupported content** |
> | q112 | *(no note recorded)* | unknown |
> | q126 | "the generated answer is supported but it doesn't answer the entire question" | **incompleteness** |
>
> Use **"partly grounded"** everywhere. Only q48 is clearly content the
> manuals do not support.

**The finding that reframes the thesis:** across 30 answers read by hand,
**not one** claim contradicted the manuals, and exactly **one answer (q48)**
contains content the manuals do not support. Everything else the layer
withholds is omission, incompleteness or off-target retrieval — none of
which is hallucination under the definition this thesis adopts.

A retrieval pipeline carrying a grounding instruction produced, on this
corpus, approximately **one ungrounded answer in thirty**. The layer's
measurable effect is therefore reliable detection at a cost in
availability, not hallucination removal — there was almost nothing to
remove.

This is the thesis's central empirical result. It is a negative result
about the problem, not about the method, and it is more useful to a
practitioner than a percentage improvement would have been.

> ⚠ n = 13 in the key cell. The improvement from 5 to 6 is **one answer**.
> Do not present it as a reliable effect. The claim-level movement in §9 is
> the defensible one.

---

## 12. Aggregate system figures — report, never used to accept a change

Command: `venv/bin/python -m src.evaluate_system`

| aggregator | coverage | risk | over-abstention |
|---|---|---|---|
| current | 32.9% | 22.6% | 66.9% |
| proportion (RAGAS) | 49.1% | 27.8% | 53.7% |
| **min (production)** | **18.0%** | **13.8%** | **80.2%** |

`min` has the lowest risk and the lowest coverage — the conservative
position, which is the intended one for a safety component.

**These figures rest on the regex-generated `expected_decision` labels,
which disagree with the author's own reading on at least q23 and q139.**
Every change on 13–14 October that passed on these aggregates failed on the
30 labelled answers. Chapter 5 reports both and says which one decided.

---

## 13. Test suite

**74 tests passing** (`venv/bin/python -m pytest tests/ -q`), across
`test_trust_layer.py` (28, decomposer), `test_verifier.py`,
`test_scorer.py`, `test_decision.py`, `test_relevance.py`.

---

## Open items that affect what can be claimed

| item | blocks | status |
|---|---|---|
| Dr. Morkos's 20 labels | "decision accuracy validated" in Ch 4 and 5 | sent 14 Oct |
| Dr. Maier's framing answer | Chapter 5's shape | sent 14 Oct |
| 153 vs 161 question count | a methodology sentence in §3.2 | unresolved |
| BUMP, FactCC, Sentence-BERT, DeBERTaV3, El-Yaniv & Wiener locators | citing the perturbation protocol in Ch 3 | see `unverified.md` §A |
| Configs B (RAGAS) and C (LLM judge) | comparative evaluation in Ch 5 | not run; 20–24 Oct window or declared future work |
