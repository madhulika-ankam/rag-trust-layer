# Proposed Revision — Chapter 1 Contributions and Objective 4

Working document. Nothing here has been applied to
`chapter-1-introduction.md`; this is a proposal to react to, written so the
current and revised versions sit side by side.

**Status of the evidence behind it — UPDATED 2026-09-24: the paper has now
been read in full.** Every ⚠ below is resolved, and resolved in this thesis's
favour. Verbatim from the PDF:

> "Given a query q, the decomposition layer emits verifiable claim skeletons"
> — §4.2

> "Claim-selective RAG uses the same kind of signal **earlier in the pipeline,
> before the final response is formed**, and maps each claim to an explicit
> action and certificate state rather than only scoring a completed answer."
> — §2

> "A conventional RAG policy emits one response r = LM(q, E) and is then
> evaluated as a whole. This is too coarse for mixed evidence... **We instead
> treat the response as a decision over claims.**" — §3

**They decompose the question, using templates, before any response exists.
No LLM-generated answer is ever verified in their system.** §4 describes it as
"the post-retrieval decision layer" — post-*retrieval*, not post-generation.

So the post-hoc differentiation holds, and the query-vs-answer distinction in
contribution 2 below — flagged as the least certain claim when this was
drafted — is confirmed.

Two further facts worth using:

- **Their ground truth is weak.** §5.3: a 100-item human re-audit agrees with
  their weak labels on 73/100, κ = 0.5027. They state that their results should
  be read as "a protocol-level certificate and action comparison, **not as a
  substitute for expert clinical adjudication**." This thesis uses an
  expert-validated published benchmark.
- **Their headline has a shortcut problem.** §6.1: metadata-only controls
  (intent-majority, source+intent) reach 0.90–0.93 action accuracy **without
  evidence**, "exceeding the full selector on action accuracy alone." They
  report this honestly, but it means action prediction is substantially
  recoverable without verification doing the work.

Provenance: single-author v1 preprint (Shao Kan, Jinglue Technology
Development, Nanjing), arXiv 21 May 2026, no venue. Real and citable prior
art — "concurrent preprint work" is accurate framing.

---

## Why this revision exists

The contributions list was written when the four-way decision formalisation
was believed to be unprecedented. arXiv:2605.21949, *Claim-Selective
Certification for High-Risk Medical RAG*, describes claim decomposition,
per-claim evidence scoring, and four-way action selection in a safety-critical
domain. ⚠

That does not remove the contribution. It relocates it.

```
BEFORE                          AFTER
──────────────────────          ──────────────────────
Headline: four-way              Headline: post-hoc middleware
decision formalisation          over an unmodified pipeline
        ↓                               ↓
Contested by 2605.21949         Their approach requires access
                                to the generation process.
                                This one does not.
```

The decision module stops being the novelty claim and becomes *how the
middleware works*. The pluggability property, currently contribution 1 and
under-argued, carries the weight instead.

---

## The contributions, current → proposed

### Contribution 1 — promote and sharpen

**Current:**

> A pluggable trust and transparency architecture for RAG systems, defined by a
> minimal interface (query, retrieved chunks, generated answer) that permits
> integration with any RAG pipeline without modification to that pipeline.

**Proposed:**

> **A post-hoc trust and transparency architecture for RAG systems.** The layer
> operates entirely downstream of generation, requiring only three strings from
> the host system — the user query, the retrieved chunks, and the generated
> answer — and no modification to its retrieval, prompting, or generation
> components. This distinguishes it from verification approaches that act
> during response construction, which require access to the generation process
> and therefore cannot be added to an already-deployed RAG system. The
> architectural consequence is that verification-gated delivery becomes
> available to existing deployments as an addition rather than a redesign.

**What changed:** "pluggable" is asserted in the current version; the revision
*argues* it, and names the alternative it is being distinguished from without
yet citing anyone. The final clause is the deployment argument — it connects
the property to why it matters, which the original left implicit.

---

### Contribution 2 — differentiate from both papers, not one

**Current:**

> Claim-level verification. Prior work integrating natural language inference
> into RAG pipelines — notably Explain-RAG [10] — applies entailment checking at
> the level of the complete generated answer... This thesis decomposes answers
> into atomic claims and verifies each independently...

**Problem:** correct as written, but incomplete. It differentiates from
answer-level verification (Explain-RAG) while claim-level verification itself
is no longer distinctive. ⚠

**Proposed:**

> **Claim-level verification of generated output.** Verification approaches
> integrating natural language inference into RAG pipelines — notably
> Explain-RAG [10] — apply entailment checking to the complete generated answer,
> producing a single label and confidence score, which identifies that an answer
> is problematic without identifying which statement within it is unsupported.
> This thesis decomposes the generated answer into atomic claims and verifies
> each independently against retrieved evidence, enabling per-claim source
> attribution and the identification of a single unsupported statement within an
> otherwise well-grounded answer. Claim-level granularity has also been applied
> in concurrent work on medical RAG [NEW REF], where claim units are derived
> from the *query* and mapped to actions during response construction; ⚠ the
> decomposition here operates on the *generated answer* after the fact, which is
> what permits the post-hoc property described in contribution 1.

**What changed:** cites the competing work rather than being silent about it,
and turns the overlap into support for contribution 1. The answer-versus-query
decomposition distinction is doing real work here — **and it is the single
claim most in need of verification against the PDF.** ⚠

---

### Contribution 3 — unchanged

The hybrid cascade is not contested by 2605.21949. They use cue-based relation
scoring; this uses NLI plus entity matching plus negation detection. Different
instruments for the same job.

Worth adding one sentence when Chapter 4 is written: the entity and negation
mechanisms exist because entailment models are documented to be weak on
numerical precision and conditional exception language, and the Layer 4 subset
experiments test exactly that. That converts the claim from assertion to
hypothesis-under-test.

---

### Contribution 4 — the one that must change

**Current:**

> A four-way decision formalisation (ANSWER / WARN / REFUSE / ESCALATE) that
> converts verification output into delivery control. Existing verification
> approaches report groundedness as an informational score returned alongside
> the answer; the answer is delivered regardless of that score. This work treats
> the score as decision-governing.

**Problem:** "existing verification approaches report groundedness as an
informational score" is now false as a general statement. 2605.21949 maps claim
scores to explicit actions including withholding. ⚠ This is the sentence a
committee member can disprove with one search.

**Proposed:**

> **An evidence-based delivery decision over a completed answer.** Verification
> output is converted into one of four actions — ANSWER, WARN, REFUSE, or
> ESCALATE — applied to the answer as delivered rather than reported alongside
> it. Evaluation frameworks such as RAGAS compute groundedness as a descriptive
> metric for offline system assessment and deliver every response regardless of
> its score. Concurrent work in medical RAG likewise maps claim-level evidence
> signals to a four-way action space [NEW REF]; ⚠ the formalisation here differs
> in operating at answer level on a completed response, which permits the
> decision to be applied by a wrapper around an existing system rather than
> integrated into its generation path.

**What changed:** the false general claim is gone. The comparison narrows to
RAGAS (where it is still true and defensible) and the medical work is cited
directly. The distinguishing property is stated as *where* the decision applies,
not *that* a four-way decision exists.

---

### Contribution 5 — unchanged

The three-layer transparency report is not addressed by either paper.

---

### Contribution 6 — align with the four-configuration design

**Current:**

> Empirical evaluation on an expert-validated manufacturing safety benchmark
> spanning three generations of manufacturing technology... against a standard
> RAG baseline.

**Proposed:**

> **Empirical evaluation** on an expert-validated manufacturing safety benchmark
> spanning three generations of manufacturing technology — a manually operated
> mill, a computer-controlled lathe, and a collaborative robot — against three
> comparison configurations: an unverified RAG baseline, a score-reporting
> configuration representative of current evaluation-framework practice, and an
> LLM-judge verification variant. The design isolates the contribution of the
> verification mechanism from that of the decision layer.

**What changed:** matches the Layer 2 design in `EVALUATION_PLAN.md`. The final
sentence is the reason the design exists — A-vs-D alone shows that the system
helps, not *what* about it helps.

---

## Objective 4 — apply the replacement already written

`EVALUATION_PLAN.md` closes with a section titled "Revised Objective 4"
containing the replacement text. It was written and never applied to the
chapter. Verbatim:

> **Objective 4.** Evaluate the resulting system against three comparison
> configurations — an unverified RAG baseline, a score-reporting configuration
> representative of current evaluation-framework practice, and an LLM-judge
> verification variant — on an expert-validated manufacturing safety benchmark,
> measuring unsupported-answer delivery rate, groundedness, decision accuracy,
> and coverage.

Note the metric name: **unsupported-answer delivery rate**, not "hallucination
rate at output." The plan uses the former throughout because it is measured at
the point of delivery. Sections 1.5 and 1.7 of the chapter still use the older
phrasing; worth unifying on one term across the whole document.

---

## Draft differentiation paragraph for Chapter 2 ⚠

Provisional — written from the abstract and related-work section, not a full
read. Rewrite against the PDF.

> Concurrent work on claim-selective certification for medical retrieval-augmented
> generation [NEW REF] shares this thesis's central structure: generated content
> is decomposed into verifiable claim units, each is scored against retrieved
> evidence, and the resulting signal determines whether a claim is stated
> directly, stated with conditions, contested, or withheld. Both approaches are
> motivated by the same asymmetry — that in high-risk domains an unsupported
> claim carries disproportionate cost while blanket abstention suppresses usable
> evidence. The approaches differ in where they intervene. Claim-selective
> certification operates before the final response is formed, mapping each claim
> to an action from which the response is then assembled, and therefore requires
> access to the generation process. The layer proposed here operates after
> generation is complete, taking the query, retrieved chunks, and generated
> answer as its only inputs and returning a delivery decision over the answer as
> a whole. The practical consequence is one of deployability: an existing RAG
> system can adopt post-hoc verification without modification to its generation
> path, whereas integration into response construction requires that path to be
> under the implementer's control.

**Do not submit this paragraph as written.** Its load-bearing claim — that they
intervene before the response is formed — comes from a single sentence in their
related-work section. If their implementation is in fact post-hoc, or supports
both modes, this paragraph is wrong and the differentiation needs rebuilding on
mechanism and domain instead.

---

## Before this is final

```
✓ Read arXiv:2605.21949 in full  (2026-09-24)
  → QUERY, via templates (§4.2)
  → operates before the response is formed (§2, §3)
  → single-author v1 preprint, no venue
  → "post-retrieval", never post-generation
  → the differentiation HOLDS

□ Get the full citation for [NEW REF]
  Shao Kan (2026). "Claim-Selective Certification
  for High-Risk Medical Retrieval-Augmented
  Generation." arXiv:2605.21949 [cs.CL], 21 May 2026.
  → confirm the arXiv listing renders the author
    name in this order before submitting

□ Unify terminology
  → "unsupported-answer delivery rate" everywhere
  → currently mixed with "hallucination rate at output"

□ Decide on Module 2 (retrieval coverage check)
  → §1.5 currently claims it "may flag insufficiency"
  → not built; either build it or move to future tense

□ Clean the broken citation tag in §1.2
  → (cite index="53-1">"you risk safety"</cite>
```

The first item gates everything else here. If the paper turns out to differ
from the characterisation above, most of this document changes.
