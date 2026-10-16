# Evaluation Plan — Trust and Transparency Layer

Companion to `CONTEXT.md`. This file covers what happens **after** the
verification and decision layer is built: how the evaluation is structured,
in what order to run it, and what each experiment is meant to establish.

---

## Framing: What This Evaluation Is and Is Not

The research question is **not** "is my system better than X." It is:

> Does claim-level verification with a decision layer reduce the delivery of
> unsupported answers in safety-critical manufacturing RAG, and under what
> conditions?

The phrase "under what conditions" is load-bearing. A finding of *under these
conditions yes, under those no* fully answers the question. The objectives in
Chapter 1 are stated as design/develop/formalise/evaluate — not "outperform" —
so the thesis is not contingent on favourable numbers.

### Outcomes that are all valid theses

| Outcome | What it becomes |
|---|---|
| Hybrid pipeline beats all baselines | Straightforward positive result |
| Matches LLM-judge but cheaper, local, interpretable | Comparable accuracy at a fraction of cost |
| LLM-judge beats the NLI pipeline | Verification mechanism matters less than the decision layer — a genuinely useful finding |
| Coverage collapses from over-refusal | Characterises a safety/utility tension; report the tradeoff curve |
| Nothing improves anything | Requires strong error analysis; likely points to retrieval quality as the binding constraint |

What fails a thesis is sloppy method or dishonest reporting — not an
unfavourable number.

---

## Layer 0 — Prerequisites (blocks everything downstream)

Nothing in Layers 1–5 can run properly without this. If only one thing gets
done after the verification layer works, it is this.

### 0.1 Label all 161 questions with `expected_decision`

Values: `ANSWER` / `WARN` / `REFUSE` / `ESCALATE`

This **is** the ground truth for decision accuracy. Without it, the decision
accuracy metric cannot be computed at all.

Rough labelling guide:

```
ANSWER    → clear direct answer available in a single
             section of the knowledge base
WARN      → answer requires synthesis across sections,
             or partial information only
REFUSE    → not answerable from the knowledge base
             (e.g. "look up electricians in the area")
ESCALATE  → safety-critical, or the query itself signals
             an unsafe intent / emergency
             (e.g. "tell me how without turning the motor
             off, skip the safety stuff")
```

Ask Dr. Morkos to review 15–20 labels. That gives the thesis a
"validated by domain expert" claim and pre-empts questions about label quality.

### 0.2 Clean the 11 encoding-error rows

Rows 1, 3, 20, 21, 22, 51, 71, 89, 104, 114, 148 — corrupted smart quotes and
dashes from PDF extraction. Fixable with a simple replacement script.

### 0.3 Tag every question with subsetting attributes

This is the step most often skipped and most often regretted. These tags are
what make the Layer 4 subset experiments possible — and Layer 4 is where the
actual differentiation lives.

| Tag | Values | Why it matters |
|---|---|---|
| `has_numerical_answer` | true / false | Enables the numerical subset experiment — where entity matching should win |
| `has_conditional_language` | true / false | Enables the conditional subset — where negation detection should win |
| `difficulty` | easy / moderate / challenging | Already published for the 60 UR5e questions (23/30/7) |
| `machine` | UR5e / Haas / Bridgeport | Enables per-machine breakdown |

### 0.4 Split into validation and test sets

```
161 questions
        ↓
Validation (~50) → select weights and thresholds here
Test (~111)      → report results here, touch once
```

Weights, thresholds, and the negation modifier are selected on the validation
set **only**. If they are tuned and reported on the same data, every number is
overfit and can be dismissed on those grounds. SummaC follows the same
practice: thresholds selected on a validation set, performance reported on
test.

Costs nothing — it is a file split — and it is the highest-leverage item in
this entire document.

### 0.5 Build a perturbation set (~100 pairs) — primary verifier validation

**This replaces bulk claim labeling as the primary route.** Take gold answers
from the benchmark and introduce single, known errors. The labels are free and
unambiguous — the corruption is deliberate.

```
Original (supported):
"The arm stops within 200ms"
        ↓
Numerical perturbation:
"The arm stops within 500ms"        → unsupported

Negation perturbation:
"Lockout is always required"
(evidence: "required unless equipment
 cannot be locked out")              → unsupported

Entity swap:
"Recovery mode" → "Emergency mode"   → unsupported
```

**Precedent:** BUMP (Ma et al., 2023) contributes 889 human-written minimal
pairs, each introducing a single error from an ontology of seven types into a
reference summary. SummEdits and HaluEval likewise consist of summaries
corrupted by introducing synthetic factual errors.

**Why this beats generic claim labeling for this thesis:**

```
Generic claim labels  → tests general verifier accuracy,
                        where an LLM judge likely wins

Targeted perturbations → tests EXACTLY the failure modes
                         entity matching and negation
                         detection were built for,
                         where the hybrid should win
```

Report balanced accuracy and ROC-AUC on the perturbation set, **broken out by
perturbation type**. That breakdown is the differentiating result: e.g. "the
hybrid verifier catches 94% of numerical corruptions versus 61% for NLI alone."

Roughly one afternoon of work.

### 0.6 Optional — ~40 naturally occurring claim labels

Supplements 0.5 by confirming the perturbation set is not unrealistically easy.
Small enough to actually finish. Skip if the timeline compresses; the
perturbation set carries the validation on its own.

---

## Layer 1 — Freeze the Baseline

Config A is **not a separate run**. It is the intermediate state of Config D.

```
query → retrieve → generate → [SAVE HERE] → trust layer → decision
                                   ↑
                        this saved output IS Config A
```

Write one JSON per question containing:

```json
{
  "question_id": "...",
  "question": "...",
  "gold_answer": "...",
  "retrieved_chunks": [ { "content": "...", "metadata": {...} } ],
  "generated_answer": "...",
  "generation_latency_ms": 0,
  "generation_cost_usd": 0.0,
  "trust_layer_output": { ... }
}
```

**Never regenerate these.** Every verification configuration must consume the
same frozen answers, or the comparisons are not valid. This single artifact
gives Config A and Config D, and is the shared input for B and C.

---

## Layer 2 — The Four Configurations

| Config | Verification | Decision layer | Represents |
|---|---|---|---|
| **A** | none | none | unverified RAG — the baseline problem |
| **B** | RAGAS faithfulness | none (score reported, answer always delivered) | current evaluation-framework practice |
| **C** | LLM-as-judge | yes | isolates the decision layer's contribution |
| **D** | hybrid NLI + entity + negation | yes | the full proposed system |

### What each comparison establishes

```
A vs B  → does verification detect anything useful?
B vs C  → does ACTING on the score matter?
C vs D  → does the verification MECHANISM matter?
A vs D  → total system contribution (headline result)
```

The middle two comparisons are what make this a thesis rather than a demo.

### Practical notes

- RAGAS faithfulness formula: `claims supported by context / total claims in
  response`. It decomposes the response into claims and checks each against
  the context using an LLM judge (gpt-4o-mini by default) — so it overlaps with
  Modules 1, 3, and 5. This overlap must be addressed head-on in Chapter 2.
- B is not free either — it also makes LLM calls. But it is a library call
  rather than custom code, so set it up before C.
- **Shortcut for C:** take RAGAS's faithfulness score and pass it through the
  same decision thresholds used in D. That yields "LLM-judge verification +
  decision module" while reusing B's infrastructure. Defensible and cheaper.
  Alternative: write an independent judge prompt for a cleaner separation.
- Budget a few dollars for API calls across B and C (161 questions × ~3 claims).

---

## Layer 3 — Core Metrics

**Fourteen metrics in five groups.** Not every metric applies to every
configuration; the applicability matrix is at the end of this section, and the
gaps in it are meaningful rather than missing work.

### A note on terminology before anything else

*Faithfulness*, *groundedness* and *hallucination rate* are largely the same
construct under different vocabularies — the degree to which generated content
is supported by retrieved evidence. Faithfulness (RAGAS's term) and
groundedness are continuous; hallucination rate is usually the discrete
complement. Do not write as though they are three separate constructs.

The headline metric of this thesis is not a new invention either:

```
Hallucination rate
= unsupported answers / ALL answers generated

Unsupported-answer DELIVERY rate
= unsupported answers / answers DELIVERED
```

Same numerator concept. **The denominator is the contribution.**

---

### Group 1 — System level (comparable to Singh et al.)

These are the metrics the manufacturing audience reads without translation, and
this thesis runs on the same benchmark as Singh et al. (arXiv:2511.11847),
making the comparison unusually direct.

| Metric | Definition |
|---|---|
| **1. Correctness** | Proportion of answers factually correct against the gold answer |
| **2. Cost per query** | USD; local inference should approach zero |
| **3. Latency per query** | Seconds, end to end |

| | Singh et al. | This work |
|---|---|---|
| Correctness | 86.66% | — |
| Cost / query | $0.005 | — (local) |
| Latency | 10.04s | — |

Singh et al. name **high accuracy, low latency and low cost** as the three
requirements for next-generation safety training systems. Reporting against
those three maps this work directly onto requirements their own paper states.
The cost and data-locality arguments (see "Design Justification" below) are
manufacturing-relevant regardless of how correctness compares.

---

### Group 2 — The headline pair

| Metric | Definition |
|---|---|
| **4. Unsupported-answer delivery rate** | Of answers *delivered to the user*, the fraction containing at least one claim unsupported by the retrieved evidence |
| **5. Groundedness of delivered answers** | The continuous form of the same construct — degree of evidential support in what actually reached the user |

Metric 4 is the headline result of the thesis, and the **A vs D comparison is
read off a single row**:

```
                        A      B      C      D
Unsupported delivery   31%    31%    12%     9%
                        ↑                     ↑
                   the "before"          the "after"
```

Config A delivers every answer, so **A's cell is by definition the
generation-side hallucination rate** — there is no separate metric for it.
B sitting at the same value as A is itself a result: scoring an answer changes
nothing unless the score governs delivery.

The framing matters. This is measured *at the point of delivery*, not at
generation. The system does not reduce hallucination inside the LLM — it
reduces how much of it reaches the user.

---

### Group 3 — The safety/utility tradeoff

| Metric | Definition | Guards against |
|---|---|---|
| **6. Coverage** | Fraction of queries receiving an answer | The "refuse everything" degenerate solution |
| **7. Over-abstention rate** | Of questions that *were* answerable, the fraction refused | The cost side of safety |
| **8. Risk–coverage curve** | Metric 6 plotted against metric 4, one point per threshold | Presenting a single operating point as if it were the only one |
| **9. AURC** | Area under that curve; a single summary number. Lower is better | — |

**Declare explicitly whether WARN counts as "answered" for coverage.** It
changes the number, and a reader cannot check the work without knowing.

Precedent: SABER (arXiv:2605.18792) sweeps τ ∈ [0.05, 0.95] reporting Score,
Coverage, Risk-on-answered and abstention F1. Over-abstention rate is reported
as a metric in LIT-RAGBench (arXiv:2603.06198). The risk-coverage framework
itself is El-Yaniv & Wiener (2010) and Geifman & El-Yaniv (2017).

Report as an operating point rather than a curve alone:

> "At 80% coverage, unsupported-answer delivery drops from 0.31 to 0.09."

---

### Group 4 — Verifier validation (the direct answer to Dr. Maier)

Measured against the perturbation set (Layer 0.5), where labels are known
because the errors were introduced deliberately.

| Metric | Definition | Why |
|---|---|---|
| **10. Balanced accuracy** | Average of the per-class accuracy; corrects for class imbalance | Primary metric in SummaC (Laban et al., 2022). Plain accuracy is gameable: if 80% of claims are supported, always answering "supported" scores 80% |
| **11. ROC-AUC** | Probability that a randomly chosen supported claim scores higher than a randomly chosen unsupported one. 1.0 perfect, 0.5 chance | Example-level metric argued for in TRUE (Honovich et al., 2022). Threshold-independent |
| **12. Per-perturbation-type breakdown** | Metrics 10–11 computed separately for numerical / negation / entity-swap corruptions | Precedent: BUMP (Ma et al., 2023). **This is the differentiating result** |

Metrics 10 and 11 answer different questions and must not be conflated:

```
Balanced accuracy → did I pick a good threshold?
ROC-AUC           → is my score any good at all?
```

Metric 12 is where entity matching and negation detection earn their place —
e.g. "the hybrid verifier catches 94% of numerical corruptions versus 61% for
NLI alone." A pooled number hides exactly the effect this thesis claims.

---

### Group 5 — Decision layer

| Metric | Definition |
|---|---|
| **13. Decision accuracy** | 4×4 confusion matrix over ANSWER / WARN / REFUSE / ESCALATE against the Layer 0.1 `expected_decision` labels |
| **14. Per-class precision and recall** | Computed per decision class |

**Report recall on ESCALATE prominently and argue the asymmetry:**

> For ESCALATE, recall matters more than precision. A false alarm costs the
> operator thirty seconds. A missed escalation is the failure mode this system
> exists to prevent.

That is asymmetric cost weighting, and it is the correct framing for a safety
component in an engineering setting.

---

### Applicability matrix

```
                        A     B     C     D
Correctness             ✓     ✓     ✓     ✓
Cost / latency          ✓     ✓     ✓     ✓
Unsupported delivery    ✓     ✓     ✓     ✓
Groundedness delivered  ✓     ✓     ✓     ✓
Coverage              100%  100%    ✓     ✓
Over-abstention         0%    0%    ✓     ✓
Risk-coverage / AURC    —     —     ✓     ✓
Balanced acc / ROC-AUC  —     —     ✓     ✓
Per-perturbation type   —     —     ✓     ✓
Decision accuracy       —     —     ✓     ✓
Per-class P/R           —     —     ✓     ✓
```

**A and B are at 100% coverage and 0% over-abstention by definition** — neither
has a decision layer, so neither can withhold anything. State this explicitly
when presenting the table, or the blanks will be read as gaps in the work.

Group 4 applies to C and D because both are verifiers and both can be validated
the same way. Hybrid versus LLM judge on the same perturbation set, broken out
by perturbation type, is among the strongest results available here.

---

### The ground-truth rule — do not grade your own homework

The single most important methodological constraint in this section.

```
WRONG
Your verifier decides which answers to deliver
        ↓
Your verifier then scores how grounded
those delivered answers were
        ↓
Guaranteed to look good. Means nothing.
```

Ground truth must be **independent of the layer being evaluated**:

```
→ the 161 expert-validated gold answers
→ the expected_decision labels (Layer 0.1)
→ the perturbation set labels (Layer 0.5)
→ author reading under the written protocol
```

All four configurations are scored against that same external standard. Never
against each other — and never against the trust layer's own verdicts. The
RAGAS version of this trap is covered under "Positioning Against Existing
Tools"; the self-grading version is worse.

### What is NOT on this list

```
Ablation study       — an EXPERIMENT (Layer 4.1)
Subset experiments   — EXPERIMENTS (Layer 4.2, 4.3)
```

Both re-report the metrics above on narrower slices. They are not additional
metrics and listing them as such double-counts. A vs D is the headline
*comparison*; the ablation is what happens *inside* D and answers a different
question — not "did it help" but "which part helped."

### Not a results-section metric

**Trust calibration.** Chapter 1 §1.5 correctly scopes this as unmeasured:
establishing that operator trust calibrates in response to these signals would
require a deployment study with practising operators, which this work does not
conduct. The defensible claim is *reduces unsupported answers reaching users,
and provides the signals that would allow trust to calibrate*. Never "increases
trust" — that invites a question about how trust was measured.

---

## Layer 4 — The Differentiating Experiments

Layer 3 produces the table. **Layer 4 produces the contribution.**

### 4.1 Ablation study

```
NLI only
NLI + entity matching
NLI + entity + negation
Full pipeline
```

Dual purpose: this is simultaneously the strongest expected result *and* the
best integration test. If NLI-only scores identically to the full pipeline, the
entity and negation modules are not actually wired in — that is a bug, not a
finding. Run this early.

### 4.2 Numerical subset

Filter to `has_numerical_answer = true`, compare D vs C.

Hypothesis: entity matching catches numerical mismatches (e.g. 500ms stated vs
200ms in evidence) that an LLM judge treats as equivalent because the sentence
structure matches.

### 4.3 Conditional subset

Filter to `has_conditional_language = true`, compare D vs C.

Hypothesis: negation detection catches exception language ("unless", "except
when", "provided that") that entailment-based verification overlooks.

### 4.4 Threshold sensitivity sweep

Sweep decision thresholds: 0.70 / 0.75 / 0.80 / 0.85 / 0.90

Plot **coverage against unsupported-answer delivery rate**.

This curve is a result whichever way it bends. It also converts the chosen
thresholds from arbitrary numbers into *empirically selected* ones — meaning
selected by experimentation and observation rather than theoretical derivation,
which is standard and defensible practice for system parameters.

---

## Layer 5 — Error Analysis

Do not skip. This chapter is often what separates a good thesis from a passing
one, and it produces material regardless of how Layer 3 turned out.

Take 25–30 failures from Config D and categorise each:

```
□ retrieval failed — relevant chunk never surfaced
□ NLI mislabelled — entailment verdict was wrong
□ entity matcher false positive — matched page numbers,
  figure numbers, or irrelevant digits
□ claim decomposition error — split mid-clause, or
  merged two distinct claims
□ threshold miscalibration — score was reasonable but
  fell on the wrong side of a boundary
□ label arguably wrong — the ground truth is debatable
```

Then count the categories. If the system underperforms, this analysis explains
*why* — and that explanation is itself a contribution.

---

## Recommended Execution Order

Note that this is **not** the order the experiments appear in the thesis. Small
versions of the ablation and error analysis are pulled forward because they
double as debugging.

```
1. Layer 0 — label, clean, tag, SPLIT the dataset
2. Freeze pipeline outputs (A comes free)
3. Run Config D
4. Spot-check 10–15 cases by hand → fix bugs
5. Hand-label ~70 claims for support (Layer 0.5)
   → can be done from the Config D output
6. Verifier validation: balanced accuracy, ROC-AUC
7. Ablation study → confirm all mechanisms are live
8. Run Config B (RAGAS)
9. Run Config C (LLM judge + decision thresholds)
10. Subset experiments (numerical, conditional)
11. Threshold sweep → risk-coverage curve
    (select final thresholds on VALIDATION set)
12. Full error analysis (25–30 cases, categorised)
```

Steps 4 and 7 exist to catch broken wiring *before* spending API money on B and
C. Fifteen minutes of manual inspection can save a full re-run.

Step 5 is placed after D because the claims to label come from D's output —
there is nothing to label before the pipeline has run.

### Dependencies

```
Layer 0.1 labelling → blocks decision accuracy (Layer 3)
Layer 0.3 tagging   → blocks subset experiments (Layer 4)
Layer 0.4 split     → blocks ALL defensible reporting
Layer 0.5 claims    → blocks verifier validation (Level 2)
Layer 1 freeze      → blocks valid comparison (Layer 2)
```

---

## Writing Order

Write in this order, not thesis order:

| When | Chapter | Depends on results? |
|---|---|---|
| Now | Ch. 3 — System Design | No |
| As you build | Ch. 4 — Implementation | No |
| While experiments run | Ch. 2 — Related Work | No |
| After Layers 3–5 | Ch. 5 — Results | Yes |
| Last | Ch. 6 — Discussion & Limitations | Yes |
| Revise existing draft | Ch. 1 — Introduction | Partially |

Chapters 3 and 4 do not depend on the numbers at all. Having them drafted means
a disappointing Layer 3 result costs nothing in schedule — it only changes what
Chapter 6 says.

---

## Positioning Against Existing Tools

### RAGAS is an instrument, not a rival

RAGAS operates as **offline evaluation infrastructure**: a developer runs it
against a test set and obtains aggregate quality scores to inform development.
It cannot withhold an answer from a user. The trust layer operates at
**inference time** on every query, and its output is a delivery decision rather
than a performance metric.

Using RAGAS metrics to evaluate the trust layer while positioning against RAGAS
would be incoherent. So: use its metrics, and position on function.

**Critical caution — avoid circularity:**

```
WRONG: use RAGAS faithfulness to judge whether
       the NLI verdict was correct
       → one verifier grading another;
         neither is ground truth

RIGHT: ground truth = the 161 expert-validated gold
       answers + the expected_decision labels
       → both the trust layer AND RAGAS are scored
         against that same ground truth
```

### Garak

Different problem — adversarial robustness and red-teaming, run offline against
a model rather than at inference against a response. Mention briefly in Chapter
2 to show awareness; it is not a comparison arm.

### The claim to make, and the one to avoid

```
Cannot defend:
"NLI outperforms LLM-as-judge"
→ likely false on general entailment;
  a large LLM judge will often win there

Can defend:
"A hybrid NLI + rule-based pipeline detects
 numerical and conditional-exception failures
 that LLM-judge verification misses, at lower
 cost, with interpretable per-mechanism scores,
 and feeds a delivery decision that
 evaluation-only frameworks do not provide"
```

The advantage is not the NLI model in isolation. It is the combination, targeted
at the specific failure modes that matter in safety-critical technical
documentation.

---

## Chapter 2 Positioning Paragraph (draft)

> RAGAS operationalises faithfulness as the proportion of claims in a generated
> response that can be inferred from the retrieved context, computed by
> decomposing the response into claims and assessing each against the context
> using an LLM judge. This work adopts the same underlying construct but differs
> in three respects. First, verification is performed using a natural language
> inference model supplemented by rule-based mechanisms rather than an LLM judge,
> motivated by the documented insensitivity of language models to numerical
> discrepancies and conditional exception language in technical documentation.
> Second, verification is performed at inference time on each query rather than
> offline in batch. Third, and most substantively, the resulting score governs
> response delivery rather than being reported as a descriptive metric.

---

## Validation — "On What Basis Are These Numbers?"

Raised by Dr. Maier after seeing preliminary results. This is the single most
important methodological question this thesis faces, and it contains two
distinct sub-questions:

1. **Why those weights and thresholds?** The composite score
   (`0.50×NLI + 0.30×entity + 0.20×semantic`), the thresholds
   (0.85 / 0.60 / 0.30), and the negation modifier (0.5) are currently
   arbitrary. A score of 0.548 has no external meaning.
2. **How do you know the verifier's judgments are correct?** The NLI says
   NEUTRAL — says who? What makes that the right label?

### The reframe that resolves most of it

The composite score is an **intermediate artifact with no external referent**.
Validating "is 0.548 correct?" is meaningless. What *does* have an external
referent:

```
Per-claim:  is this claim actually supported
            by the evidence? (human judgment)

Per-answer: was ANSWER/WARN/REFUSE/ESCALATE
            the right decision? (expected_decision labels)
```

Validate those outputs. The score is merely the mechanism producing them.

### Three levels of validation, all with published precedent

**Level 1 — Component validation (free; pure citation)**

DeBERTa-v3's NLI performance on MNLI and ANLI is published, as is the embedding
model's performance on STS benchmarks. Report these in Chapter 4. The
entailment model was not invented here; its accuracy is established
independently of this work.

Answers: *is the NLI component a reasonable instrument?* → here are its
published numbers.

**Level 2 — Verifier validation against human labels**

The established meta-evaluation protocol for factual-consistency metrics:

- **SummaC** (Laban et al., 2022) uses **balanced accuracy** as primary metric
  — chosen because accuracy is conceptually simple and interpretable, and
  adjusting class imbalance out of the metric makes scores uniform across
  datasets — with **ROC-AUC** as secondary. Thresholds are selected on a
  validation set.
- **TRUE** (Honovich et al., 2022) argues that *system-level* correlation with
  human judgment is the wrong meta-evaluation target, and instead uses
  **example-level ROC-AUC** over binary support labels.

Procedure:

```
1. Sample claims from pipeline output
2. Hand-label each: supported / not supported
3. Compute inter-annotator agreement (Cohen's κ)
   on a subset
4. Score the verifier against those labels:
   → balanced accuracy (primary)
   → ROC-AUC (secondary)
   → per-class precision and recall
```

**Level 3 — Decision validation via risk-coverage**

This is the established framework for exactly what the decision module does.
Allowing a classifier to abstain and measuring the coverage–risk tradeoff is a
classical formulation (El-Yaniv & Wiener, 2010; Geifman & El-Yaniv, 2017).

```
Coverage       = fraction of questions answered
Selective risk = error rate among answered questions
```

Sweep the threshold and plot coverage against unsupported-answer rate, then
report **operating points**:

> "At 80% coverage, unsupported-answer delivery drops from 0.31 to 0.09."

That single sentence carries more weight than any composite score. Area under
the risk-coverage curve (AURC) gives a single summary number with real meaning.

The selective-prediction framing also converts the thresholds from guesses into
derived quantities: choose the threshold that **maximises coverage subject to
selective risk staying below a stated tolerance** on the validation set. For a
manufacturing safety thesis, deriving thresholds from a safety requirement is a
substantially stronger story than picking round numbers.

---

### Triage — what is actually required

#### NECESSARY — Maier's question cannot be answered without these

```
□ Validation / test split
  161 questions → ~50 validation, ~111 test
  Select weights and thresholds on validation ONLY
  Touch the test set once, at reporting time
  → Zero extra work; just split the file
  → Without this, every number is overfit and
    can be dismissed on those grounds

□ expected_decision labels on all 161
  (already Layer 0.1 — this is the
   decision-accuracy ground truth)

□ Risk-coverage curve
  Already planned as the threshold sweep (4.4);
  plot it as coverage vs unsupported-answer rate
  → THIS is the direct answer to "on what basis"

□ Claim-level support labels — ~60-80 claims
  NOT 150. Enough for balanced accuracy with
  wide but honest confidence intervals.
  A few hours of work.
```

#### WORTH DOING — meaningfully strengthens the thesis

```
□ Cohen's κ on a 30-40 claim subset
  Second annotator; another grad student is fine
  κ above ~0.6 is respectable

□ Component benchmark numbers in Chapter 4
  Published DeBERTa MNLI/ANLI figures
  → pure citation, no experimental work

□ Ablation study (already Layer 4.1)
  Do this INSTEAD of grid-searching weights —
  if each mechanism addition improves results,
  the exact weights matter less
```

#### SKIP unless time allows — PhD-level polish, fine as future work

```
□ Expected Calibration Error + reliability diagrams
□ Bootstrap resampling for significance testing
□ Learned weights via logistic regression on
  validation labels (3 features, ~50 examples —
  genuinely not much work if time permits)
□ Full 150+ claim labeling
```

### The minimum that answers Dr. Maier

```
1. Split the data
2. Label ~70 claims using a written protocol
3. Report balanced accuracy + ROC-AUC
4. Report the risk-coverage curve
5. Label expected_decision on all 161
```

Roughly one day of focused work, most of which was already in this plan. Steps
1 and 4 are nearly free and do the heaviest lifting.

---

### On who does the labeling

**The author can label.** The judgment required is *"is this claim supported by
this text?"* — a reading-comprehension task. It is **not** *"is this safe
manufacturing practice?"*, which would require a safety engineer. Only the
former is needed.

```
Claim:    "The arm stops within 500ms"
Evidence: "...stopping time 200ms..."
        ↓
Supported? No.
        ↓
No manufacturing expertise required
```

What makes single-annotator labeling defensible:

1. **Write the labeling protocol before starting.** Define
   supported / not supported / unclear, and write down the edge-case rules.
   This becomes a thesis appendix.
2. **Second annotator on a subset** (~30-40 claims) with Cohen's κ reported.
3. **Dr. Morkos reviews 15-20** — not to relabel everything, but to confirm the
   protocol is sound.
4. **Declare it in limitations:** "Labels produced by the author following a
   documented protocol; agreement validated on a subset."

Single-annotator datasets appear routinely in published work. What is *not*
defensible is undocumented labeling with no agreement check.

Note also that the gold answers are already expert-validated by the Megahed
team, so `expected_decision` labelling often reasons from expert-written
answers rather than from scratch — a meaningful backstop.

---

### The sentence all of this exists to support

Everything above is in service of being able to say this truthfully:

> My thresholds are selected on held-out validation data to meet a stated risk
> target, and my verifier's agreement with human judgment is measured directly
> rather than assumed.

Anything beyond that sentence is optional polish.

### Full defense answer

> The composite score is an internal mechanism, not a claim about the world, so
> I validate the outputs it produces rather than the score itself. Verification
> is validated against human-labeled claim support using balanced accuracy and
> ROC-AUC, following the meta-evaluation protocol of SummaC and TRUE. Decision
> quality is validated through risk-coverage analysis from the selective
> prediction literature, reporting selective risk at fixed coverage levels.
> Weights and thresholds are selected on a held-out validation split and never
> on the test set.

---

## Prior Work — Positioning and Framing Shift

### The closest architectural precedent

**Claim-Selective Certification for High-Risk Medical RAG** (arXiv:2605.21949)
describes decomposing a question into verifiable claim units, scoring each
claim against evidence, and choosing whether to state it directly, state it
with conditions, contest it, or withhold it.

```
Their four actions:        This thesis:
────────────────────       ───────────────────
state directly         ≈   ANSWER
state with conditions  ≈   WARN
contest                ≈   ESCALATE
withhold               ≈   REFUSE
```

Their implementation: template-based claim decomposition, cue-based relation
scoring for support/conflict/limitation signals, and an intent-aware
risk-calibrated selector. They motivate it similarly — high-risk medical QA has
an asymmetric answer contract, where unsupported dosing or contraindication
claims can be harmful while blanket abstention suppresses usable evidence.

**Consequence: the claim "no prior work formalises four-way decisions for RAG"
must be dropped.** Do not let a committee member find this paper first.

### The three remaining differences

**1. Pipeline position — the substantial one.** Their own paper states that
claim-selective RAG uses the signal *earlier in the pipeline, before the final
response is formed*, mapping each claim to an explicit action rather than only
scoring a completed answer.

```
Them: intervene DURING response construction
      per-claim actions assembled into an answer
      → requires access to the generation process

This: intervene AFTER generation
      answer-level decision on a completed answer
      → requires only three strings:
        query, chunks, answer
      → any deployed RAG can adopt it unmodified
```

**2. Verification mechanism.** Cue-based relation scoring versus NLI + entity
matching + negation detection.

**3. Domain.** Medical versus manufacturing, with a distinctive regulatory/OEM
document mix. Weaker as a differentiator but real.

### The framing shift

```
DROP as the headline:
"A four-way decision module for RAG"
        ↓
Claim-selective certification does this

LEAD WITH:
"Post-hoc middleware that adds verification-gated
 delivery to an unmodified RAG pipeline"
        ↓
Theirs integrates into generation.
This requires nothing from the host system.
```

The pluggability property should move into the title and abstract. The decision
module becomes *how* the middleware works, not the headline claim.

**Action:** read arXiv:2605.21949 in full and write the differentiation
paragraph before the defense. Check whether it is peer-reviewed or preprint.

---

## Methodological Precedent — Answering "On What Basis?"

The field has converged on protocols for exactly this. Two distinct things must
not be conflated:

```
Justifying the METHOD
"Balanced accuracy is the right metric here"
        ↓
Papers supply this. Many of them.

Justifying THE NUMBERS
"My verifier scores 0.81"
        ↓
No paper can supply this. It must be measured.
```

A published thermometer design does not report the patient's temperature — but
it means the thermometer need not be reinvented.

### Verifier validation precedent

| Source | Contribution |
|---|---|
| **SummaC** (Laban et al., 2022) | Balanced accuracy primary, ROC-AUC secondary; thresholds selected on validation set; bootstrap resampling for significance |
| **TRUE** (Honovich et al., 2022) | Example-level ROC-AUC over binary support labels; argues against system-level correlation as the target |
| **MiniCheck** (Tang et al., 2024) | Lightweight claim verification benchmarking |
| **BUMP** (Ma et al., 2023) | 889 minimal pairs, single error from an ontology of seven types |
| **SummEdits, HaluEval** | Corrupted-summary construction for consistency evaluation |

### Decision layer validation precedent

| Source | Contribution |
|---|---|
| **SABER** (arXiv:2605.18792) | Threshold sweep τ ∈ [0.05, 0.95] in 0.05 steps, reporting Score, Coverage, Risk on answered, abstention F1 — essentially this thesis's experiment design |
| **El-Yaniv & Wiener (2010); Geifman & El-Yaniv (2017)** | The risk-coverage framework itself |
| **Citation-Enforced RAG** (arXiv:2603.14170) | Abstention grounded in retrieval confidence rather than generative uncertainty |
| **LIT-RAGBench** (arXiv:2603.06198) | Over-abstention rate as a reported metric |

Also useful for positioning — **Prompt-Based Abstention Fails Under Misleading
Context** (arXiv:2608.22228) notes that abstention is well studied in selective
prediction, but for RAG most work either folds it into broader system
evaluation or targets frontier models.

### What can and cannot be borrowed

```
Borrow: which metrics to compute
        how to select thresholds
        how to construct perturbations
        how to report results
        what counts as rigorous

Cannot borrow: the actual values
        SummaC's balanced accuracy is SummaC's,
        measured on SummaC's benchmark — it says
        nothing about this pipeline on these
        161 questions
```

The verifier here is a composition nobody has built: DeBERTa + entity matching
+ negation detection with these weights, on manufacturing safety documents. No
published number describes that object, because it did not exist before. That
is the cost of having a contribution — if a paper already reported these
numbers, there would be no thesis.

### The line for Dr. Maier

> I follow the meta-evaluation protocol established by SummaC and TRUE for
> verifier validation, and the selective-prediction protocol from SABER and the
> risk-coverage literature for the decision layer. The protocols are
> established; the measurements are mine, because the system is mine.

### Before optimising against a hypothetical — ask him

His objection is currently being guessed at. A short email resolves it:

> When we spoke, you asked what basis my scores rest on. I want to make sure I
> address the right thing. My plan is to validate the verifier against a
> perturbation set with known labels using balanced accuracy and ROC-AUC,
> following the protocol in SummaC and TRUE, and to validate the decision layer
> using risk-coverage analysis from the selective prediction literature.
> Thresholds would be selected on a held-out validation split. Does that address
> your concern, or were you pointing at something else?

Possible underlying objections, and whether the current plan covers them:

```
"Your composite score is arbitrary"
  → covered: validation-set selection

"You have no ground truth"
  → covered: perturbations + decision labels

"Your sample is too small"
  → partly: confidence intervals; otherwise a
    stated limitation

"Why believe a number you invented?"
  → covered: external protocols

"This isn't how my field does it"
  → NOT covered. If Maier comes from a
    measurement-heavy engineering background
    rather than NLP, his standard for "validated"
    may differ, and citing SummaC will not
    satisfy him. Worth establishing which.
```

---

## Immediate Next Steps

```
1. Email Maier — confirm what he actually meant
   Cheapest item here; unblocks everything else

2. Split the data (~50 validation / ~111 test)
   Ten minutes; highest leverage item in this document

3. Read arXiv:2605.21949 in full
   Write the differentiation paragraph

4. Build the perturbation set (~100 pairs)
   One afternoon; numerical, negation, entity swap

5. Continue Layer 0 labelling and tagging
```

Items 1 and 2 cost almost nothing and should happen regardless of Maier's
answer.

---

## Design Justification — Defending the Verification Mechanism

This section answers the hardest questions this thesis will face. Both are
likely to come up in a defense, and both have real answers that do not depend
on winning on raw accuracy.

### First, check the premise

"LLM-as-judge is better" is not established. It is better at *general
entailment reasoning* — one axis. And the Config C vs D result is an experiment
not yet run; answering as though the comparison is already lost is premature.

More importantly, "better" for a safety component deployed on a shop floor is
not the same as "better" on an entailment benchmark.

### The five axes where the layer's significance is independent of accuracy

**1. Auditability**

```
LLM judge output:
"Unsupported." — plus a score
        ↓
Why? Unrecoverable. The reasoning sits
inside a model that cannot be inspected.

Hybrid pipeline output:
NLI:      NEUTRAL (0.51)
Entity:   MISMATCH — claim "500ms",
          evidence "200ms"
Negation: "unless" detected in evidence
Semantic: 0.61
→ combined 0.44 → REFUSE
        ↓
Every component of the decision is visible
and attributable to a specific mechanism
```

In a setting where an incident might trigger an inquiry into why the system
said what it said, "the LLM judged it unsupported" is a materially weaker
answer than a decomposable score.

**2. Correlated failure**

Possibly the strongest argument:

```
Generator: an LLM
Judge:     an LLM
        ↓
If they share training data, architecture,
or failure modes, they may share blind spots
        ↓
The judge may confidently approve exactly
the fabrications the generator is prone to
```

DeBERTa is a different architecture trained on a different objective. Entity
matching is not a neural model at all. Architectural diversity in a
verification chain is an engineering principle, not a rationalisation.

**3. Determinism and reproducibility**

```
Hybrid pipeline: fixed weights, fixed thresholds
→ same input, same output, indefinitely
→ reproducible by anyone, permanently

LLM judge: API model versions deprecate
→ gpt-4o-mini today ≠ gpt-4o-mini in 18 months
→ published results become unreproducible
```

For a component claiming to be a *safety* mechanism, a verifier whose behaviour
can change without notice is a genuine liability.

**4. Data locality**

Manufacturing firms frequently cannot transmit operational data to external
APIs — proprietary process parameters, equipment configurations, sometimes
contractual restrictions. A verification layer requiring an API call per claim
is undeployable in those environments. The hybrid pipeline runs entirely local.

**5. Targeted hardening**

Entity matching and negation detection exist because entailment models —
LLM judges included — are documented to be weak on precisely the two things
that cause harm in procedural documentation: wrong numbers and missed
exceptions. This is not a general accuracy claim. It is a claim about specific
failure modes, and it is testable in the Layer 4 subset experiments.

### Answer: "Why NLI and not LLM-as-judge?"

> We deliberately avoided LLM-as-judge verification for three reasons. First,
> auditability: a verification decision in a safety-critical setting should be
> decomposable into inspectable components rather than delegated to an opaque
> model. Second, correlated failure: using a language model to verify a language
> model risks shared blind spots, whereas an NLI model supplemented by
> rule-based checks provides architectural diversity in the verification chain.
> Third, deployability: local inference imposes no per-query cost and requires
> no transmission of operational data to external services, which is a hard
> constraint in many manufacturing environments. We include an LLM-judge
> configuration in our evaluation precisely so this design choice can be
> assessed empirically rather than assumed.

That final sentence matters most: the choice was tested, not assumed.

### Answer: "Why not just use RAGAS faithfulness instead of your layer?"

> RAGAS faithfulness is an offline evaluation metric. It produces an aggregate
> score to inform system development; it does not operate at inference time and
> it cannot withhold a response from a user. Substituting it for the proposed
> verification layer would supply a number but not a decision, no per-claim
> source attribution, and no explanation — and every answer, including
> unsupported ones, would still be delivered. We use RAGAS in this work, but as
> a comparison configuration and as a source of standard metrics, not as a
> replacement for the layer.

One-line version if pressed: **RAGAS tells the developer how the system
performed. This layer tells the operator whether to act on this answer.**

### Why this makes the thesis robust to its own results

The contribution is the **layer** — decompose, verify, score, decide, explain.
The verification mechanism is a **pluggable component inside it**.

```
If Config C beats Config D:
The layer still stands — swap the mechanism
        ↓
Finding: "the decision layer drives most of the
improvement; verifier choice is a cost and
auditability tradeoff rather than an accuracy one"
        ↓
A useful, publishable result
```

The architecture was designed to be mechanism-agnostic. That makes "which
verifier performs best" an empirical question answered *within* the framework
rather than a threat to it.

The thesis question was never "is DeBERTa better than GPT." It is "does
verification-gated delivery reduce unsupported answers reaching users, and what
are the tradeoffs among verification mechanisms." Both halves are answered
regardless of how C vs D falls.

---

## Revised Objective 4

Replace the current Objective 4 in Chapter 1 with:

> **Objective 4.** Evaluate the resulting system against three comparison
> configurations — an unverified RAG baseline, a score-reporting configuration
> representative of current evaluation-framework practice, and an LLM-judge
> verification variant — on an expert-validated manufacturing safety benchmark,
> measuring unsupported-answer delivery rate, groundedness, decision accuracy,
> and coverage.

This turns the evaluation from "I built a thing and it works" into "I isolated
what actually causes the improvement."
