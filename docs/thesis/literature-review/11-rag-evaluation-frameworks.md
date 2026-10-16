# Category 11 — RAG Evaluation Frameworks

**Supports:** Contribution 4's surviving comparison, revised Objective 4's three
configurations (unverified baseline / score-reporting / LLM-judge)
**Prior state:** **RAGAS is named repeatedly across the project and cited nowhere.** It is
now the *only* surviving comparison for Contribution 4 after the Claim-Selective finding,
which makes the missing citation a real problem.

**Domain ladder:** general-domain frameworks, plus one biomedical meta-evaluation and one
domain-specific RAG evaluator. Three of the six are 2024+.

---

## 11.1 RAGAS — the comparison Contribution 4 depends on

| Field | Value |
|---|---|
| Title | **Ragas: Automated Evaluation of Retrieval Augmented Generation** |
| Authors | Shahul Es; Jithin James; Luis Espinosa-Anke; Steven Schockaert |
| arXiv | 2309.15217 (2023-09-26, latest revision 2025-04-28) |
| Status | **PREPRINT on the arXiv record — no DOI, no journal reference** |
| Provenance | arXiv API, fetched 2026-10-13 |
| Access | metadata verified |

⚠ **The venue is unconfirmed.** The project's prior work guessed "EACL 2024 demo track".
That is **not confirmed** by the arXiv record and must not be cited until verified. See
`unverified.md` §B.

Note the title capitalisation on the record is "**Ragas**", not "RAGAS".

### Why the citation matters more than it looks

Contribution 4's claim was narrowed to: evaluation frameworks compute groundedness as a
descriptive offline metric and deliver every response regardless of score. **RAGAS is the
example that makes that claim true.** With no citation, the one surviving differentiation
for Contribution 4 rests on an uncited assertion about a named system.

The positioning paragraph is already drafted at `EVALUATION_PLAN.md:634-648` and is sound —
it just needs this reference attached.

⚠ **And keep the caution the project recorded:** do not claim NLI verification outperforms
an LLM judge on entailment accuracy. Prior work was explicit that a large LLM judge will
likely beat DeBERTaV3 on many claims. The defensible claims are *cost*, *latency*,
*locality*, *inference-time operation* and *delivery control* — not raw accuracy.

---

## 11.2 ARES — the second framework

| Field | Value |
|---|---|
| Title | ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems |
| Authors | Jon Saad-Falcon; Omar Khattab; Christopher Potts; Matei Zaharia |
| Venue | **NAACL 2024** (per arXiv comment) |
| arXiv | 2311.09476 |
| Status | NAACL 2024 — **confirm the Anthology citation** for page numbers. 2024+ compliant |
| Provenance | arXiv API, fetched 2026-10-13 |

Named in the project's related-work tables as "ARES (Saad-Falcon et al., 2023)" with no
locator. **Now resolved — and note it is a 2024 NAACL paper, not 2023.**

Cite alongside RAGAS so the "evaluation frameworks" claim rests on two systems rather than
one. ARES uses fine-tuned LLM judges with prediction-powered inference, which makes it a
stronger version of the same category.

---

## 11.3 LLM-as-judge validity — required for Objective 4

The revised Objective 4 adds "an LLM-judge verification variant" as a comparison
configuration. That needs methodological grounding, or the configuration itself is
arbitrary.

| Paper | Verified citation | Status |
|---|---|---|
| **Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena** | Lianmin Zheng; Wei-Lin Chiang; Ying Sheng; Siyuan Zhuang; Zhanghao Wu; Yonghao Zhuang; + more — arXiv `2306.05685`, **NeurIPS 2023 Datasets and Benchmarks Track** | the standard citation for LLM-as-judge agreement with human preference |
| **Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences** | Shreya Shankar; J. D. Zamfirescu-Pereira; Björn Hartmann; Aditya G. Parameswaran; Ian Arawjo — arXiv `2404.12272` (2024-04-18) | preprint; 2024+ compliant. The caution: LLM judges need validating against human preference, they are not a ground truth |

Zheng et al. establishes that LLM judges can agree with humans; Shankar et al. establishes
that this agreement must be *demonstrated*, not assumed. Together they justify treating the
LLM-judge configuration as a comparison rather than as a reference standard — which is the
correct framing given the 161-question set has **expert-validated gold answers** and
therefore does not need an LLM judge to define truth.

---

## 11.4 Domain-specific and meta-evaluation

| Paper | Citation | Status | Relevance |
|---|---|---|---|
| **RAGalyst: Automated Human-Aligned Agentic Evaluation for Domain-Specific RAG** | arXiv `2511.04502` | preprint; 2024+ | **directly relevant to the Maier objection** and surfaced-but-never-discussed in prior work. Its premise — that existing frameworks rely on heuristic metrics or LLM judges lacking validated human alignment — is the thesis's own critique. Read it |
| **PlainQAFact: Retrieval-augmented Factual Consistency Evaluation Metric for Biomedical Plain Language Summarization** | arXiv `2503.08890`, **DOI `10.1016/j.jbi.2026.105019`** — *Journal of Biomedical Informatics* | **PUBLISHED**, peer-reviewed | the richest captured example of **verifier-versus-verifier meta-evaluation** (AUC-ROC tables against SummaC, QAFactEval, AlignScore, DAE). A template for how to present the verifier validation table |
| **SelfCheckGPT** | Potsawee Manakul; Adian Liusie; Mark J. F. Gales — EMNLP 2023 (per RT4CHART's bibliography) | published | zero-resource, sampling-based consistency. The contrast: no external evidence. Cite once to show the alternative was considered |

**PlainQAFact is the most actionable of these.** It is peer-reviewed, in a safety-adjacent
domain, and shows exactly how to lay out a comparison of one verifier against established
baselines — which is the table Dr. Maier asked for.

---

## Summary for Chapter 2

Two paragraphs are already drafted in the project (`EVALUATION_PLAN.md:634-648` for RAGAS,
and the broader one at thesis-chat line 25807). Both are good. They need:

1. **The RAGAS citation attached** — and its venue verified first.
2. **ARES added** as a second instance, correctly dated 2024.
3. **Zheng et al. and Shankar et al.** cited where the LLM-judge configuration is
   introduced, so that configuration is grounded rather than assumed.
4. **RAGalyst read**, because it makes the thesis's own critique of existing evaluation and
   may either support the framing or pre-empt it.

The positioning that survives: these are **offline evaluation infrastructure** that informs
development; the trust layer operates at inference time on every query and its output is a
delivery decision rather than a performance metric.
