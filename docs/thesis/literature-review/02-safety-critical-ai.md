# Category 2 — Safety-Critical & High-Stakes AI Deployment

**Supports:** §1.3 (the asymmetry argument), §1.2 (why 86.66% accuracy is not enough),
Chapter 2 area 3
**Prior state:** **completely empty.** Reading-list Group 5 in the thesis chat still read
`14. Trustworthy AI in Safety-Critical Systems (find recent 2022-2024 survey papers)` and
`15. AI Safety and Reliability in Industrial Applications (find relevant papers)`. Never
populated.

---

## ⚠ Read this before using the category

**All three entries are unreviewed preprints.** Zero published papers. By the
published-first standard applied everywhere else in this review, this is the weakest
category in the set — compare category 1, which is now 11 peer-reviewed out of 12.

**Access levels are honest, not incidental.** §2.1 has been read in full. §2.2 and §2.3
have not — only their abstracts. Neither is worth a full read at their current weight in
the argument; §2.1 is the only one doing real work.

**And the "nothing exists in manufacturing" finding below is unconfirmed, not established.**
It came from two searches. Category 1 demonstrated that this search method misses
peer-reviewed journal literature that is not on arXiv — four manufacturing journal papers
were found only when the author supplied DOIs. Treat the absence claim here with the same
scepticism applied to the gap claim in `01-manufacturing-rag.md` §1.8.

---

## Domain ladder result — state this as a finding

**Manufacturing tier: nothing.** Searched for safety-critical AI deployment work in
manufacturing, workplace-safety regulation and OSHA compliance contexts. No paper
addresses verification or abstention for LLMs in workplace safety regulation.

**This confirms the project's existing gap claim, and narrows it usefully.** The absence is
not that manufacturing RAG does not exist — it does (category 1) — but that *no
manufacturing paper treats verification-gated delivery as a requirement*. Say it as a
positive finding.

**Other high-stakes tiers: rich.** Aviation and medicine both have directly transferable
work. The aviation paper below is the single best addition to the thesis from this whole
category.

⚠ A caution on search hygiene: querying "safety-critical AI" returns frontier-AI
governance material (AI Safety Index reports, red-teaming, jailbreaks). That is a
different field and **not** relevant here. The relevant literature is *domain* safety
engineering, not AI-alignment safety.

---

## 2.1 Consequence-aware evaluation in air traffic control

**Revised 2026-10-15 after a full read.** The first version of this section was written
from the abstract and framed the paper as support for verification-gated delivery. That
reading was too generous — see "What it does not support" below.

| Field | Value |
|---|---|
| Title | Beyond Semantic Accuracy: Consequence-Aware Evaluation for Safety-Critical Language Understanding |
| Authors | Yujing Chang; Thinh Pham; Van-Phat Thai; Chunyao Ma; Yash Guleria; Pham Nhut Huy; Sameer Alam |
| Affiliations | ATMRI, Nanyang Technological University; Centre of AI Research, VinUniversity |
| arXiv | 2608.24621 (v2, 2026-08-25) |
| Status | **PREPRINT** — no DOI, no venue. Unreviewed |
| Provenance | `https://arxiv.org/pdf/2608.24621v2`, full text extracted 2026-10-15 |
| Access | `[full text]` |

### What the paper actually critiques

**Not NLI.** The words "entailment" and "natural language inference" appear **zero times**
in the full text. Their target is *evaluation metrics*, named explicitly in §1
`[full text]`:

> "Standard evaluation for speech and task-oriented language understanding often relies on
> surface or semantic metrics such as **word error rate (WER), character error rate (CER),
> intent accuracy, and slot-level F1**... **These metrics typically treat errors uniformly
> across tokens, slots, or intents**, creating a mismatch when actual consequences differ."

Their results table labels the critiqued quantity "NER-F1 (Semantic)". So "semantic
accuracy" here means task-performance scoring, not semantic verification. NLI is a
mechanism; their subject is metrics.

Their own framework, from the Figure 1 caption `[full text]`:

> "An ATC utterance is mapped to an action schema with **consequence-weighted slots**; a
> structured understanding model (Task 1) and a readback safety judgment model (Task 2) are
> evaluated against that schema using **nonlinear metrics that penalize safety-critical
> misses more severely than surface errors.**"

With a safety severity taxonomy of CORRECT / HIGH / CRITICAL / EXTREME, and slot weights
validated by a controller questionnaire (Appendix H).

### Three valid uses

**① §1.2 — the aggregate-versus-instance argument.** This is the strongest use, and the
structure transfers exactly `[full text, §1]`:

> "As these systems enter operational workflows, **average semantic accuracy becomes an
> incomplete proxy for safety-critical reliability**: a harmless formatting difference, a
> recoverable contextual miss, and a wrong control value may score similarly despite very
> different consequences. Safety-critical language understanding is therefore a problem of
> **consequence under operational risk, not just semantic similarity**."

Compare §1.2's own sentence: "A system that is correct 86.66% of the time and silent about
which 86.66% offers the operator no actionable signal at all." Same argument, measured in
another regulated domain. This converts a rhetorical claim into one with a cited parallel.

**② Contribution 3 — the numerical/conditional argument, in consequence terms.** "A
harmless formatting difference... and a wrong control value may score similarly" is
precisely the 200ms → 500ms case: semantically near-identical, operationally critical.
That is EQUATE's finding (`06-numerical-negation-nli.md` §6.1) reached from operational
risk instead of model accuracy — genuine cross-domain triangulation. Their failure modes,
"a misread altitude" and "a dropped execution condition", map onto the numerical and
negation perturbation types.

**③ Positioning — their future work is this thesis.** From the limitations section
`[full text]`:

> "Most importantly, improved scores are still far from deployment-grade ATC reliability.
> **Future work should pair stronger models with multi-layer safety mechanisms such as
> abstention, independent cross-checking, human review, and runtime monitoring.**"

Abstention is REFUSE. Independent cross-checking is the verifier. Human review is
ESCALATE. This is the same rhetorical move the project already makes with Explain-RAG's
future-work line on adaptive confidence thresholds, and it is a strong one: a
safety-critical NLP paper naming the next step, and this thesis building it.

⚠ Note it is **future work, not a finding**. Cite it as a stated research direction, not
as evidence that such mechanisms work.

### ⚠ What it does not support — and where it argues against this thesis

**It does not argue for verification-gated delivery.** It argues for better *evaluation*.
Do not cite it as justification for the trust layer's existence; cite it for the problem
statement and the consequence framing.

**And its critique applies to this thesis's own Chapter 5.** Balanced accuracy and ROC-AUC
over the 302 perturbation pairs "treat errors uniformly" — exactly the complaint. A missed
numerical substitution and a missed entity swap score identically despite different
operational consequence. The paper's prescription is consequence-weighted, nonlinear
metrics.

Three possible responses, in increasing cost:

1. **Acknowledge it.** State in Chapter 5 that reported metrics weight error types
   uniformly, cite this paper, and note consequence-weighted evaluation as future work.
   Cheapest, and honest.
2. **Point at the benchmark design.** The perturbation *types* were chosen by operational
   consequence — numerical thresholds and conditional exceptions carry safety consequence
   in procedural text. That is consequence-aware benchmark construction even without a
   consequence-weighted metric. Worth stating either way; it is a real partial answer.
3. **Adopt a weighted metric.** Report balanced accuracy alongside a severity-weighted
   variant over the three perturbation types. **Appendix J of this paper describes how to
   transfer the framework beyond ATC** by replacing the domain action inventory, critical
   slot mapping and error taxonomy — i.e. a published recipe for porting it to
   manufacturing. Genuinely tractable on a 302-pair set, and it would be a distinctive
   result.

**Recommend 1 + 2.** Option 3 is attractive but it is new experimental work, not a writing
change.

### What to read

- §1 Introduction — the two framing quotes above
- Figure 1 and the consequence-weighted slot schema
- The semantic-safety gap results
- **Appendix J** — cross-domain transfer, if considering option 3
- Appendix H — the controller questionnaire, if defending how weights were set
- **Skip:** the ATC-specific action inventory and readback taxonomy detail

### Role

**Support** for §1.2 and Contribution 3; **positioning** via their future work; and a
**limitation** citation for Chapter 5's uniform error weighting.

⚠ **Unreviewed preprint.** Use it for framing, parallel and research direction. Do not
rely on its measured numbers, and attribute them to ATC rather than to manufacturing.

## 2.2 Human-in-the-loop for high-stakes NLP

| Field | Value |
|---|---|
| Title | From Automation to Collaboration: Human-in-the-Loop Methods for Safe and Trustworthy NLP |
| Authors | Most. Sharmin Sultana Samu; MD. Tanvir Ahmed Seum; Md. Rakibul Islam |
| arXiv | 2605.25226 (v1, 2026-05-24) |
| Status | **PREPRINT** — arXiv comment: "manuscript under review" |
| Provenance | arXiv API, fetched 2026-10-13. Full text at `https://arxiv.org/pdf/2605.25226` |
| Access | `[abstract only]` — **I have not read it.** The tag records my confidence, not availability; the PDF is freely downloadable. **Not recommended for a full read**: a three-author survey, under review, used here for one framing sentence. The abstract carries that sentence |

Verbatim `[abstract only]`:

> "Large language models are widely deployed in high-stakes NLP tasks, yet risks such as
> bias, hallucination, adversarial vulnerability and unreliable generalization remain."

> "**Human supervision is essential** for probe validation, adversarial verification and
> domain-specific annotation, but it is costly and hard to scale."

### Why it matters for the ESCALATE decision

The four-way action space includes ESCALATE — route to a human. That action is currently
justified by intuition. This paper's framing (human supervision is essential but costly
and hard to scale) is the argument for *selective* escalation: you cannot put a human on
every answer, so the system must decide which answers need one.

That is a better defence of ESCALATE than "some questions need a person", and it connects
the decision layer to a named research direction.

⚠ Unreviewed preprint under review. A survey by three authors; treat as a pointer to the
human-in-the-loop literature rather than as strong evidence.

---

## 2.3 Risk documentation — optional

| Field | Value |
|---|---|
| Title | Assessing Language Model Deployment with Risk Cards |
| Authors | Leon Derczynski; Hannah Rose Kirk; Vidhisha Balachandran; Sachin Kumar; Yulia Tsvetkov; M. R. Leiser; Saif Mohammad |
| arXiv | 2303.18190 |
| Status | **PREPRINT** — no DOI, no venue |
| Provenance | arXiv API, fetched 2026-10-13. Full text at `https://arxiv.org/pdf/2303.18190` |
| Access | `[abstract only]` — **I have not read it.** **Not recommended for a full read** unless Contribution 5's auditing audience needs defending; it is the most marginal entry in this category and could be dropped without loss |

A framework for structured documentation of deployment risk. Relevant to the transparency
report's *auditing* audience (Contribution 5, layer 1) if that claim needs support. Lower
priority than §2.1 and §2.2 — include only if Chapter 2 needs a deployment-documentation
citation.

---

## Still missing — and worth getting

| Need | Why | Status |
|---|---|---|
| **ISO 10218** / **ISO/TS 15066** (collaborative robot safety) | Contribution 6's benchmark spans a UR5e cobot. These are *the* governing standards and the knowledge base already contains OSHA and NIOSH documents. Citing them shows domain command | **not searched** — standards, not papers; find the official references |
| Medical/clinical high-stakes RAG beyond the competitor set | the medical tier of the domain ladder | partially covered by MedScore (cat. 4) and MedTrust-RAG (cat. 13) |
| The MDPI *Sensors* (2025) manufacturing-AI-trustworthiness survey | named in the thesis chat as the broad framing citation for why transparency matters in manufacturing AI | **no DOI or volume recorded anywhere** — see `unverified.md` §A |

---

## Summary for Chapter 2

The category is no longer empty, and the honest structure is:

> Safety-critical deployment of language technology has been studied in several regulated
> domains. In air traffic control, Chang et al. (2026) show that standard semantic metrics
> substantially overstate operational reliability, identifying a semantic-safety gap that
> risk-aware fine-tuning narrows but does not close, and conclude that consequence-aware
> evaluation is a necessary complement to conventional NLP metrics before any
> safety-critical deployment claim. Their failure modes — misread numerical values and
> dropped execution conditions — correspond directly to the error categories targeted here.
> No equivalent treatment exists for manufacturing safety: the manufacturing RAG literature
> reports accuracy, cost and latency (Chapter 2, §2.1) without reporting whether individual
> answers are supported by the evidence retrieved for them. That absence is the gap this
> thesis addresses.
