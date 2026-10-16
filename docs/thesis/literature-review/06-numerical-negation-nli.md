# Category 6 — Numerical Reasoning & Negation in NLI

**Supports:** Contribution 3 (the hybrid cascade), Objective 2, RQ3
**Prior state:** **zero citations.** Chapter 1 asserted entailment models are "known to
be susceptible" to "numerically similar but materially different values, and conditional
exception language such as 'unless' or 'except when'". The contributions revision
repeated it as "documented to be weak". Documented by whom was answered nowhere in the
project.

**This is now the best-supported claim in the thesis.** The literature does not merely
agree — it reports that NLI models perform *below a majority-class baseline* on both
phenomena.

**Domain ladder:** searched manufacturing first — no manufacturing-domain NLI evaluation
exists. Fell through to general NLP, where the evidence is direct and strong. Pre-2024
by necessity: these are the origin papers for the finding, and nothing 2024+ supersedes
them. Flagged accordingly.

---

## 6.1 Numerical reasoning — EQUATE

| Field | Value |
|---|---|
| Title | EQUATE: A Benchmark Evaluation Framework for Quantitative Reasoning in Natural Language Inference |
| Authors | Abhilasha Ravichander; Aakanksha Naik; Carolyn Rose; Eduard Hovy |
| Venue | Proceedings of the 23rd Conference on Computational Natural Language Learning (CoNLL 2019), ACL, **pp. 349–361** |
| DOI | `10.18653/v1/K19-1033` |
| arXiv | 1901.03735 |
| Status | **PUBLISHED**, peer-reviewed |
| Provenance | Crossref + `https://aclanthology.org/K19-1033.pdf`, full text extracted 2026-10-13 |
| Access | `[full text]` |

### The quote that does the work

> "We benchmark the performance of 9 published NLI models on EQUATE, and find that on
> average, state-of-the-art methods **do not achieve an absolute improvement over a
> majority-class baseline, suggesting that they do not implicitly learn to reason with
> quantities.** We establish a new baseline Q-REAS that manipulates quantities
> symbolically. In comparison to the best performing NLI model, it achieves success on
> numerical reasoning tests (**+24.2%**), but has limited verbal reasoning capabilities
> (**-8.1%**)." `[full text, abstract]`

### Why this is the single most useful paper in the review

It does not just license Contribution 3 — it **empirically validates the cascade design**.

A symbolic quantity manipulator beats the best neural NLI model by +24.2% on numerical
reasoning, while losing 8.1% on verbal reasoning. That is precisely the trade-off the
hybrid cascade exploits: NLI for verbal entailment, rule-based entity and number matching
for quantities. The argument stops being an assertion and becomes a replication of a
published result in a new domain.

Note also, from the experimental setup: "all models except Q-REAS are trained on
MultiNLI" `[full text]` — the same training-data family as `cross-encoder/nli-deberta-v3-base`.

### What to read

- §1 Introduction and the abstract — the headline finding
- §4.2 and Figure 1 — the Q-REAS design, as precedent for a symbolic numerical component
- Table 6 — accuracies of all 9 models across the five test sets, with Δ over majority baseline
- **Skip:** the individual test-set construction details unless replicating the benchmark

### Role
**Support** citation. Grounds Contribution 3's numerical half and RQ3.

---

## 6.2 Numerical reasoning — Stress Test (corroborating)

| Field | Value |
|---|---|
| Title | Stress Test Evaluation for Natural Language Inference |
| Authors | Aakanksha Naik; Abhilasha Ravichander; Norman Sadeh; Carolyn Rose; Graham Neubig |
| Venue | COLING 2018 (per arXiv comment) |
| arXiv | 1806.00692 (v3) |
| Status | PREPRINT record; COLING 2018 venue stated in the arXiv comment — **confirm the ACL Anthology entry for page numbers** |
| Access | `[search snippet]` — not yet read in full |

Reported finding (from search results, **not yet verified against the paper**): no model
exceeded ~33% accuracy on the numerical reasoning stress test, i.e. no better than
random, with models relying on word overlap and shallow lexical cues.

⚠ Treat as unverified until the full text is read. EQUATE (§6.1) already carries this
argument with verified quotes, so this is corroboration rather than a dependency.

---

## 6.3 Negation — Hossain et al., the decisive paper

| Field | Value |
|---|---|
| Title | An Analysis of Natural Language Inference Benchmarks through the Lens of Negation |
| Authors | Md Mosharaf Hossain; Venelin Kovatchev; Pranoy Dutta; Tiffany Kao; Elizabeth Wei; Eduardo Blanco |
| Venue | Proceedings of EMNLP 2020, ACL, **pp. 9106–9118** |
| DOI | `10.18653/v1/2020.emnlp-main.732` |
| Status | **PUBLISHED**, peer-reviewed |
| Provenance | Crossref + `https://aclanthology.org/2020.emnlp-main.732.pdf`, full text extracted 2026-10-13 |
| Access | `[full text]` |

### The quotes that do the work

On prevalence `[full text, §1]`:

> "negation is ubiquitous in regular English texts: **approximately 25% of English
> sentences contain negation** depending on the domain and genre"

> "Despite these facts, **negation is underrepresented and mostly irrelevant in existing
> benchmarks—one can literally disregard the negations and still make correct inference
> judgments in popular datasets.**"

Table 1 `[full text]` — percentage of sentences containing negation:

| Corpus | % with negation |
|---|---|
| General English corpora | 8.69 – 29.92 (over 17% in all but Wikipedia) |
| **RTE** | **7.16** |
| **SNLI** | **1.19** |
| **MNLI** | **22.63** |

On model performance `[full text, §6.1]`:

> "the three transformers obtain worse results with the new pairs including negation,
> especially with SNLI (**≈50% drop** with the three transformers)"

> "Comparing with the results obtained with the majority baseline, we observe that
> **the transformers do not learn to solve pairs with negation unless they are tuned
> with pairs including negation.** Indeed, **all of them obtain worse results than the
> majority baseline in RTE and SNLI**, but not in MNLI."

And fine-tuning does not rescue it `[full text, §6.2]`:

> "Can transformers solve the new text-hypothesis pairs including negation if retrained
> with some of the new pairs including negation? **Only to a certain degree:** with SNLI,
> they benefit but underperform with respect to the original pairs; and with MNLI, they
> only benefit slightly."

### Why this matters specifically for this thesis

The verifier uses `cross-encoder/nli-deberta-v3-base`, trained on the SNLI/MNLI family.
**SNLI contains negation in 1.19% of sentences.** The model has therefore had almost no
exposure to the phenomenon that OSHA and OEM procedural language depends on — "required
unless", "except when", "shall not". That is a direct, citable mechanism for why the
negation-detection component is necessary rather than decorative.

It also predicts the result the perturbation experiment should produce: the negation
subset should be the one where NLI alone performs worst, and where the negation flag
contributes the largest gain in the ablation. If it does not, that is a finding worth
investigating, not a disappointment.

### What to read

- §1 — the two framing quotes above
- §4 and Table 1 — the prevalence analysis and the per-benchmark percentages
- §6.1 and Table 7 — performance on negation-critical pairs vs the majority baseline
- §6.2 and Table 8 — why fine-tuning does not solve it
- **Skip:** §3 negation cue detector architecture (Bi-LSTM+CRF, 0.92 F1) unless building one

### Role
**Support** citation. Grounds Contribution 3's negation half, RQ3, and the cascade ordering.

---

## 6.4 Negation — LLMs are no better

| Field | Value |
|---|---|
| Title | Language models are not naysayers: An analysis of language models on negation benchmarks |
| Authors | Thinh Hung Truong; Timothy Baldwin; Karin Verspoor; Trevor Cohn |
| arXiv | 2306.08189 (2023-06-14) |
| Status | PREPRINT on arXiv; appears in the *SEM 2023 proceedings (`aclanthology.org/2023.starsem-1.10`) — **confirm the Anthology citation** |
| Access | `[search snippet]` |

⚠ **Attribution correction:** a web search summary credited this paper to "Anschütz et
al." That is wrong. The arXiv record gives **Truong, Baldwin, Verspoor & Cohn**. Verified
via the arXiv API.

Reported finding (unverified): LLMs show limited ability to reason under negation,
performing worse than random on most NLI datasets, improving only with instruction tuning.

### Why it earns a place

It forecloses an obvious examiner question — "why not just use a modern LLM instead of
rule-based negation detection?" If the answer is that LLMs also fail on negation, the
rule-based component is justified for any verifier, not just a small NLI model. **Worth
promoting to a full read in Phase 2** for exactly that reason.

---

## 6.5 Also identified, not yet pursued

| Paper | Relevance | Status |
|---|---|---|
| **Adversarial NLI: A New Benchmark for Natural Language Understanding** — Yixin Nie; Adina Williams; Emily Dinan; Mohit Bansal; Jason Weston; Douwe Kiela. arXiv `1910.14599`, ACL 2020 per arXiv comment | annotators exploited numerical/quantitative reasoning to fool models — corroborates §6.1 | verified via arXiv API 2026-10-13; not read |
| MoNLI | downward monotonicity, where negation reverses entailment | **unresolved** — no citation found yet |
| CONDAQA | reasoning about the implications of negation | **unresolved** — no citation found yet |

---

## Summary for Chapter 2

The replacement for "entailment models are known to be weak" is now a citable, sourced
paragraph:

> Entailment models are documented to perform poorly on both phenomena this thesis
> targets with rule-based mechanisms. Ravichander et al. (2019) benchmark nine published
> NLI models on quantitative reasoning and find that on average they achieve no absolute
> improvement over a majority-class baseline, concluding that such models do not
> implicitly learn to reason with quantities; a symbolic quantity manipulator outperforms
> the best neural model by 24.2% on numerical reasoning while losing 8.1% on verbal
> reasoning. Hossain et al. (2020) show that negation occurs in approximately 25% of
> general English sentences but in only 1.19% of SNLI and 7.16% of RTE text-hypothesis
> pairs, and that transformers trained on these corpora perform *worse than a majority
> baseline* on negation-critical pairs — an effect that fine-tuning mitigates only
> partially. Since the entailment model used here is trained on the SNLI/MNLI family,
> and since procedural safety language depends on exactly these two constructions —
> exact numerical thresholds and conditional exceptions — the cascade supplements
> entailment with entity and numerical matching and with explicit negation detection.
