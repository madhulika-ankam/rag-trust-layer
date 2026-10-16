# Category 8 — Calibration & Threshold Selection

**Supports:** the answer to Dr. Maier's objection; Contribution 4's thresholds; the
logistic-regression weight fitting
**Prior state:** **zero citations**, while `EVALUATION_PLAN.md` itself admits the numbers
are arbitrary:

> "The composite score (`0.50×NLI + 0.30×entity + 0.20×semantic`), the thresholds
> (0.85 / 0.60 / 0.30), and the negation modifier (0.5) are currently arbitrary."

The September plan called this "the single most important methodological question this
thesis faces." It is a literature problem as much as an experimental one: fitting the
weights answers *how*, but citing the calibration literature answers *why that is the
right kind of answer*.

**Domain ladder:** calibration is a general ML construct; no manufacturing work. All
foundations pre-2024 by necessity.

---

## 8.1 Guo et al. — the canonical calibration reference

| Field | Value |
|---|---|
| Title | On Calibration of Modern Neural Networks |
| Authors | Chuan Guo; Geoff Pleiss; Yu Sun; Kilian Q. Weinberger |
| Venue | ICML 2017 (per arXiv comment) |
| arXiv | 1706.04599 |
| Status | ICML 2017 — **confirm the PMLR proceedings citation** for volume/pages |
| Provenance | arXiv API, fetched 2026-10-13 |
| Access | metadata verified |

The standard citation that modern neural networks are **miscalibrated** — confident scores
do not match empirical accuracy — and the source of **temperature scaling** as the simple
post-hoc fix.

### Why this is the key citation for the Maier objection

It establishes that a model's raw output score is *not* a probability, and that converting
one into a usable confidence requires an explicit, fitted post-hoc step. That is exactly
what the logistic regression does. The argument becomes:

> The verifier's mechanism scores are not calibrated probabilities. Following standard
> practice for post-hoc calibration of neural network outputs, the combination of
> mechanism scores into a single trust value is fitted on held-out validation data rather
> than chosen, and the resulting coefficients are reported.

That reframes the weights from "numbers I picked" to "parameters estimated by a standard
method" — and the framing, not just the fitting, is what satisfies a methodological
objection.

---

## 8.2 Desai & Durrett — calibration for the model family actually used

| Field | Value |
|---|---|
| Title | Calibration of Pre-trained Transformers |
| Authors | Shrey Desai; Greg Durrett |
| Venue | EMNLP 2020 (per arXiv comment: "Accepted to EMNLP 2020") |
| arXiv | 2003.07892 |
| Status | EMNLP 2020 — **confirm the Anthology citation** |
| Provenance | arXiv API, fetched 2026-10-13 |

Narrows Guo et al. to pre-trained transformers — the correct reference class for a
DeBERTaV3 cross-encoder. Cite alongside Guo et al.: the general finding, then the specific
one for this model family. It also examines in-domain versus out-of-domain calibration,
which matters because the NLI model was trained on general-domain data and is applied to
OSHA and OEM technical text.

---

## 8.3 Conformal prediction — the stronger alternative

| Field | Value |
|---|---|
| Title | A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification |
| Authors | Anastasios N. Angelopoulos; Stephen Bates |
| arXiv | 2107.07511 |
| Status | PREPRINT / tutorial — widely cited as the standard introduction |
| Access | metadata verified |

Conformal prediction gives **distribution-free coverage guarantees**: set a target error
rate and obtain a threshold that provably achieves it on exchangeable data.

### Why to cite it even without implementing it

It is the obvious "why didn't you do this instead?" question for a thesis that selects
thresholds empirically. Two defensible positions, both improved by the citation:

1. **Acknowledge and defer.** State that conformal methods would supply formal guarantees
   on the REFUSE threshold, and identify it as future work. Costs one sentence, removes a
   whole line of questioning.
2. **Acknowledge and adopt partially.** Calibrate the REFUSE threshold conformally on the
   validation half to guarantee a bound on unsupported-answer delivery rate. This is
   genuinely tractable on a 302-pair set and would be a strong result — but it is new work,
   not a writing change.

Recommend position 1 unless there is time.

---

## 8.4 Threshold selection on a validation set — the precedent already in hand

The protocol the perturbation experiment already follows comes from **SummaC** (category 5,
TACL 10, pp. 163–177):

> "The balanced accuracy metric requires models to output a binary label (i.e., not a
> scalar score), which for most models requires the selection of a threshold in the score."
> `[quoted in the project's prior work from the paper]`

SummaC selects thresholds on a validation set and reports balanced accuracy on test. That
is precedent for the 50/50 validation/test split already built. **Cite SummaC here as well
as in category 5** — it covers both the metric and the threshold-selection procedure.

⚠ **Brodersen et al. (2010)**, SummaC's own citation for balanced accuracy, remains
**unresolved**. It is a short ICPR paper and should be found — it is the primary citation
for the thesis's headline metric. See `unverified.md` §A.

---

## 8.5 Recent, RAG-specific

| Paper | arXiv | Status | Relevance |
|---|---|---|---|
| Beyond Component Strength: Synergistic Integration and Adaptive Calibration in Multi-Agent RAG Systems | 2511.21729 | preprint | the only RAG paper in the project's set that treats calibration as a first-class concern. 2024+ compliant. **Surfaced but never discussed** in prior work |
| Entropy Alone is Insufficient for Safe Selective Prediction in LLMs | 2603.21172 | preprint | Phillips; Gustafsson; Wu; Thakur; Clifton. Contains **E-AURC and TCE** metric definitions. Also in category 7 |

---

## Summary for Chapter 2 and the Maier response

The full answer to "on what basis are these numbers?" has three parts, and all three now
have citations:

| Part | The claim | Citations |
|---|---|---|
| **The weights** | mechanism scores are not calibrated probabilities, so the combination is *fitted* on held-out data, not chosen | Guo et al. (2017); Desai & Durrett (2020) |
| **The verifier's performance** | measured against known labels using an established meta-evaluation protocol | SummaC (2022); TRUE (2022); BUMP (2023) for the minimal-pair design |
| **The thresholds** | selected on validation, reported on test, with the coverage/risk trade-off made explicit | El-Yaniv & Wiener (2010); Geifman & El-Yaniv (2017); SABER; LIT-RAGBench |

And the honest boundary, which the project already articulated well:

> No published number describes this verifier, because this composition — DeBERTaV3 plus
> entity matching plus negation detection, on manufacturing safety documents — did not
> exist before. What the literature supplies is the *protocol*; the measurements are the
> thesis's own.
