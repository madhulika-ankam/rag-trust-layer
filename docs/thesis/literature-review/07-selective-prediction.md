# Category 7 — Selective Prediction, Abstention & Risk-Coverage

**Supports:** Objective 3, Contribution 4, the ANSWER/WARN/REFUSE/ESCALATE module,
Experiment 4.4 (threshold sweep)
**Prior state:** the decision module **is** selective prediction, and Chapter 1 never
names the field. Several papers were identified in the thesis chat but none was given a
resolvable citation, and the two foundational references existed as author-year only.

**This is the largest structural exposure in the thesis** — bigger than any individual
missing reference. Not naming the field invites the question "are you aware this is
selective prediction?", which is much worse than citing it and differentiating.

**Domain ladder:** no manufacturing-domain abstention work exists. The RAG tier is rich
and recent (five 2026 preprints), and the foundations are classical ML. Foundations are
pre-2024 by necessity.

---

## 7.1 El-Yaniv & Wiener — the origin of risk-coverage

| Field | Value |
|---|---|
| Title | **On the Foundations of Noise-free Selective Classification** |
| Authors | Ran El-Yaniv; Yair Wiener (Technion) |
| Venue | *Journal of Machine Learning Research* **11(53), pp. 1605–1641** |
| Date | 2010. Submitted 10/09, revised 4/10, published 5/10 |
| Status | **PUBLISHED**, peer-reviewed. JMLR has no DOI; cite volume/pages |
| Provenance | `https://jmlr.org/papers/v11/el-yaniv10a.html`, confirmed 2026-10-13 |
| Access | `[search snippet]` — metadata and abstract framing confirmed |

**The attribution in the project is correct.** An initial search cast doubt on whether
Wiener was a co-author; the JMLR record confirms both authors. The project's
`El-Yaniv & Wiener (2010)` is right — it just needed a title and locator.

### Why it is the right foundational citation

The paper coins and formalises the **risk-coverage trade-off** — the exact framework the
thesis's evaluation uses. Its stated concern `[search snippet]`: the trade-off between how
often a classifier answers (coverage) and how accurate those answers are. That is the
ANSWER-rate-versus-error-rate curve the decision module produces.

Citing it converts "we chose four thresholds" into "we instantiate a selective classifier
and report its risk-coverage behaviour" — which is a direct, literature-grounded response
to Dr. Maier's objection.

⚠ The title is "Noise-**free** Selective Classification". The thesis's setting is noisy
(NLI output is probabilistic), so cite it for the *framework*, not as a claim that the
noise-free analysis applies directly.

---

## 7.2 Geifman & El-Yaniv — risk-coverage for neural networks

| Field | Value |
|---|---|
| Title | Selective Classification for Deep Neural Networks |
| Authors | Yonatan Geifman; Ran El-Yaniv |
| Venue | NIPS 2017, **pp. 4878–4887** (per DBLP) |
| arXiv | 1705.08500 (2017-05-23) |
| Status | **PUBLISHED**, peer-reviewed. Page numbers from DBLP — **confirm against the NeurIPS proceedings** |
| Provenance | arXiv API, fetched 2026-10-13 |
| Access | metadata verified |

The bridge from the classical theory to neural models: constructing a selective
classifier from an already-trained network, with a user-specified risk level.

**That construction is architecturally what the trust layer does** — it wraps an existing
model and adds a reject option without retraining it. This is a *stronger* precedent for
Contribution 1's post-hoc property than anything in the RAG literature, because it
establishes the pattern as a recognised one in ML generally.

Follow-up worth knowing: SelectiveNet (Geifman & El-Yaniv, ICML 2019) integrates the
reject option into training — i.e. the *non*-post-hoc alternative. **Unresolved citation**,
but useful as a contrast if the pluggability argument needs reinforcing.

---

## 7.3 SABER — the closest methodological match

| Field | Value |
|---|---|
| Title | Trust or Abstain? A Self-Aware RAG Approach |
| Authors | Xi Zhu; Ziqi Wang; Kai Mei; Wujiang Xu; Minghao Guo; Bangji Yang; Jiajun Fan; Dimitris N. Metaxas |
| arXiv | 2605.18792 |
| Status | **PREPRINT** — no DOI, no venue |
| Provenance | arXiv API, fetched 2026-10-13 |
| Access | `[search snippet]` from prior project work |

The thesis chat calls this "literally your experiment design" and "essentially your
Experiment 4.4 — copy the table structure." Reported to sweep τ from 0.05 to 0.95 in
0.05 steps, reporting Score, Coverage, Risk-on-answered, and abstention F1.

**Priority for a full read in Phase 2.** It is both the strongest methodological
precedent and a potential competitor; the project has never read it in full.

---

## 7.4 The four metrics, each with a source

The project settled on four decision-layer metrics. Each now has a citation:

| Metric | Definition | Source |
|---|---|---|
| **Coverage** | fraction of queries answered | El-Yaniv & Wiener (2010) §7.1 |
| **Selective risk** | error rate among answered | El-Yaniv & Wiener (2010); Geifman & El-Yaniv (2017) |
| **Over-abstention rate** | refused despite being answerable | LIT-RAGBench `2603.06198` |
| **Abstention F1** | overall decision quality | SABER `2605.18792` |

This table is the answer to "on what basis are these numbers?" for the *decision layer*
specifically — distinct from the verifier-validation answer, which comes from SummaC and
TRUE (category 5).

---

## 7.5 RAG-specific abstention — the recent tier

All verified via the arXiv API, 2026-10-13. Status varies — **one is peer-reviewed**, the
other three are preprints. Author lists below are from the arXiv records.

| Paper | Authors / status | Role |
|---|---|---|
| **LIT-RAGBench:** Benchmarking Generator Capabilities of Large Language Models in Retrieval-Augmented Generation (`2603.06198`) | Koki Itai; Shunichi Hasegawa; Yuta Yamamoto; Gouki Minegishi; Masaki Otsuki — **PUBLISHED: "conference paper at LREC 2026"** | supplies **over-abstention rate** as a named metric, and it is peer-reviewed. ⚠ the title emphasises *generator capabilities* — confirm the metric is actually defined there before citing it for that purpose |
| **Citation-Enforced RAG for Fiscal Document Intelligence:** Cited, Explainable Knowledge Retrieval in Tax Compliance (`2603.14170`) | Akhil Chandra Shanivendra (single author) — preprint, 22 pages | grounds abstention in *retrieval confidence* rather than generative uncertainty. **This is the justification for Module 2 (Retrieval Coverage Check)** — designed but unbuilt. Read §7.2. ⚠ single-author applied-systems preprint; use for the argument, not as strong evidence |
| **Prompt-Based Abstention Fails Under Misleading Context:** A Controlled Study of Small Frozen RAG Models (`2608.22228`) | Yohanes Andre Setiawan (single author) — preprint; arXiv comment says "Committed to AACL-IJCNLP 2026", i.e. **not yet accepted** | **positioning** citation: for RAG, most abstention work folds into broader system evaluation or targets frontier models. Also: prompt-based abstention *fails*, which argues for a mechanism outside the prompt |
| **Entropy Alone is Insufficient for Safe Selective Prediction in LLMs** (`2603.21172`) | Edward Phillips; Fredrik K. Gustafsson; Sean Wu; Anshul Thakur; David A. Clifton — preprint | argues uncertainty-based abstention is inadequate alone. Supports evidence-grounded over confidence-based abstention. Contains E-AURC and TCE definitions |

**Note the convergence.** Three of these four independently argue that abstention based on
model confidence or prompting is insufficient, and that it should be grounded in evidence
or retrieval instead. That is the thesis's core design choice, and it is now supported by
converging recent work rather than asserted.

---

## 7.5b Refusal as a training objective — a third family

Added 2026-10-16. Cross-reference to `03-hallucination-taxonomies.md` §3.4.

§7.1–7.5 cover two families: classical **selective prediction** (reject option on a
trained model) and **evidence-grounded abstention** in RAG. There is a third, and §7 did
not mention it: refusal **learned during training**.

Zhang et al. (2025, *Computational Linguistics* 51(4), DOI `10.1162/COLI.a.16`) report
that refusal responses are incorporated into supervised fine-tuning data so that models
learn to decline specific questions, citing the Moss project (Sun et al., 2023b), Llama
Team (2024) and Wan et al. (2024), and observe that models so tuned "could learn to refuse
to answer specific questions, therefore helping reduce hallucinations."

**Why it belongs in this category.** It is the alternative mechanism for achieving the same
outcome as REFUSE, and it sits on the opposite side of the thesis's defining axis:

| Family | When the refusal decision is made | Requires |
|---|---|---|
| SFT-learned refusal | during generation, from learned behaviour | model + training pipeline access |
| Selective prediction | after scoring, on a trained model | model output scores |
| **This thesis** | after generation, from evidence verification | query, chunks, answer — nothing from the model |

Naming all three makes Objective 3's positioning complete, and **strengthens Contribution
1** rather than threatening it: the established route to a refusing model is retraining it.

⚠ Sun et al. (2023b), Llama Team (2024) and Wan et al. (2024) are **second-hand through
the survey** and not independently resolved. Logged in `unverified.md`.

---

## 7.6 Answerability — the Module 2 foundation

| Field | Value |
|---|---|
| Title | Know What You Don't Know: Unanswerable Questions for SQuAD |
| Authors | Pranav Rajpurkar; Robin Jia; Percy Liang |
| arXiv | 1806.03822 |
| Status | ACL 2018 (per arXiv comment) — **confirm the Anthology citation for page numbers** |
| Provenance | arXiv API, fetched 2026-10-13 |
| Access | metadata verified |

The foundation for detecting that a question cannot be answered from the available
evidence. Relevant to §1.5's acknowledged omission and to the unbuilt Module 2.

---

## Summary for Chapter 2 — and the one thing that must change

The decision module needs to be **named as selective prediction** and then differentiated.
Draft:

> The decision mechanism proposed here is an instance of selective prediction, the
> framework formalised by El-Yaniv and Wiener (2010) and extended to neural models by
> Geifman and El-Yaniv (2017), in which a model may decline to answer and is evaluated on
> the resulting trade-off between coverage and selective risk. Within retrieval-augmented
> generation, recent work has examined abstention driven by generative uncertainty and by
> prompting, and reports both to be insufficient: entropy-based signals alone do not yield
> safe selective prediction, and prompt-based abstention degrades under misleading context.
> Approaches that instead ground the decision in retrieval or evidence availability report
> better alignment between the decision and the evidence it rests on. This thesis takes the
> latter position, grounding delivery decisions in per-claim verification against retrieved
> evidence, and extends the binary answer/abstain formulation to a four-way action space
> that distinguishes a qualified answer from a refusal and from an escalation.

**Why this is safe to write.** Naming the field costs nothing and removes the worst
question. The four-way extension of a binary formulation is a real, modest, defensible
contribution — and unlike "nobody has formalised four-way decisions", it survives contact
with `2605.21949`.
