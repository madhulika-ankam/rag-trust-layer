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
- [x] Basic RAG pipeline working (loader, chunker, retriever) — verified live,
      retrieve() returns correct relevant chunks from the persisted Chroma
      index. NOT the same as a full RAG pipeline — see gaps below.
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

## Next Steps (as of 2026-08-06)

The core Trust Layer (decompose → verify → score → decide → report) is
fully implemented and tested (39/39 tests passing) and has been run
end-to-end against fixture data, producing correct results. It has NOT yet
been run against real RAG output — see gap #1 below, which blocks that.

In priority order:

1. **Build the LLM answer-generation step.** This is the biggest gap. The
   RAG pipeline (`src/rag/`) only retrieves chunks — nothing generates an
   answer from them. Per the tech stack, this should be a local Llama 3 or
   Mistral model. Without this, there's no real "generated answer" to run
   the Trust Layer against; everything tested so far has used hand-written
   fixture answers, not actual RAG output.
2. **Wire RAG output into the Trust Layer.** Nothing currently calls
   `decompose()` → `verify()` → `score()` → `decide()` → `generate_report()`
   on real retrieved chunks + a real generated answer. Once step 1 exists,
   add this glue (likely in `src/main.py` or a new orchestration entry
   point).
3. **Rebuild the Chroma index.** Found a staleness bug: the persisted index
   at `data/chroma` has metadata citing
   `29 CFR 1910.147 (up to date as of 4-30-2026).pdf`, but the current file
   in `data/raw` is dated `7-23-2025` — the index was built from an
   older/differently-named snapshot. Citations in the transparency report
   would point to a filename that no longer exists until this is rebuilt.
4. **Confirm Bridgeport Mill manual status.** `KneeMill-Complete-Manual.pdf`
   is already in `data/raw` — check whether this is the manual that was
   "pending from Megahed" before treating it as still missing.
5. Module 2 (Retrieval Coverage Check) — not yet built.
6. NLI model finalized (base vs. large) — still open, tradeoff not decided.
7. Minor: `src/rag/retriever.py` imports the deprecated
   `langchain_community.vectorstores.Chroma`; migrate to `langchain_chroma`
   at some point (not urgent).
8. Evaluation framework (RAGAS-based) — not yet built.

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