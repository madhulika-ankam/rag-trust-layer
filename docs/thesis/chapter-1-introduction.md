# Chapter 1 — Introduction

## 1.1 Background and Context

Manufacturing remains one of the most economically significant and, simultaneously, one of the most hazardous sectors of industrial activity. The sector employs over 12.7 million workers in the United States and generated more than $2.9 trillion in annual GDP in 2024, yet it also reported over 320,000 workplace injuries, placing it among the most dangerous occupational domains [1]. Being struck by objects or equipment and being caught in or compressed by equipment rank among the most common categories of workplace injury, and the associated economic burden is substantial: the manufacturing sector spends approximately $7.5 billion annually on direct medical payments and lost wages [1].

A recurring contributing factor is the difficulty operators face in accessing accurate procedural and safety information at the moment it is needed. Modern shop floors combine legacy manually operated equipment, computer-controlled machinery, and collaborative robotic systems, each with distinct operating procedures, safety interlocks, and hazard profiles. Variations across equipment make it difficult for operators to reliably recall the correct procedure for every system they interact with, and this difficulty is compounded under production time pressure. Traditional safety training — delivered in classroom or lecture format at fixed intervals — is static and poorly matched to this reality, leaving operators without a means of resolving specific procedural questions as they arise [1].

Retrieval-Augmented Generation (RAG), introduced by Lewis et al. [2], offers a plausible technical response to this gap. Rather than relying solely on a language model's parametric knowledge, RAG retrieves relevant passages from an external corpus and conditions generation on that retrieved evidence. Applied to manufacturing, this permits a conversational system grounded in equipment manuals, regulatory standards, and safety guidance — capable, in principle, of answering an operator's question in seconds rather than requiring them to locate and search a several-hundred-page manual.

A growing body of work has demonstrated the technical feasibility of this approach. Singh et al. [3] developed a multimodal manufacturing safety chatbot grounded in a curated corpus of OSHA regulations, NIOSH safety alerts, and original equipment manufacturer manuals, evaluating twenty-four distinct RAG configurations against an expert-validated benchmark. Their best-performing configuration achieved 86.66% accuracy at approximately $0.005 per query and roughly ten seconds of end-to-end latency — figures that suggest such systems are technically and economically viable for deployment.

---

## 1.2 Problem Statement

Technical feasibility, however, has not translated into practical adoption.

In a user study conducted inside an operating factory, Kernan Freire et al. [4] deployed an LLM-based knowledge assistant with access to factory documentation and expert-contributed operational knowledge, then evaluated operator response. Participants recognised genuine benefits — faster information retrieval and more efficient issue resolution — but nevertheless expressed a clear preference for consulting human colleagues when a colleague was available. Their stated reasons were specific. A participant characterised the risk directly, noting that if system responses are not adequate, (cite index="53-1">"you risk safety"</cite>. Others cited the comparative efficiency of asking an expert working nearby, and the study reports particular concern that hallucinated responses could produce dangerous situations in a facility processing chemicals [4].

This reluctance is not technophobia, and treating it as such misdiagnoses the problem. It is a rational response to a structural property of standard RAG systems: they return a generated answer with no indication of whether that answer is actually supported by the retrieved evidence. The operator receives fluent, confident prose whether the underlying retrieval was excellent or irrelevant, and whether the model faithfully reproduced the retrieved content or fabricated around it.

Under those conditions the operator has no basis for discriminating between a well-grounded answer and a hallucinated one. In a safety-critical environment where acting on incorrect procedural guidance can cause injury, the only defensible policy under undifferentiated uncertainty is to distrust every answer equally — which, in practice, means falling back on human consultation wherever it is available and disregarding the system.

The same barrier is documented beyond the single-factory case. An interview study of RAG deployment across industrial organisations identifies difficulty in verifying the accuracy of generated information as a persistent obstacle alongside hallucination itself [5]. Work on industrial LLM reliability similarly observes that deployment has not consistently produced sustained adoption, and identifies as a central barrier the requirement that industrial outputs be not merely plausible on average but correct for the specific instance and auditable after the fact [6].

**The barrier to adoption is therefore not the capability of these systems but the verifiability of their output.** A system that is correct 86.66% of the time and silent about which 86.66% offers the operator no actionable signal at all.

---

## 1.3 Motivation and Significance

Two observations motivate this work.

First, the failure mode is asymmetric. An operator who under-relies on a correct system loses time. An operator who over-relies on an incorrect system may follow an unsafe procedure. Recent analysis of RAG behaviour notes that users may over-rely on such systems on the assumption that retrieval guarantees faithfulness — an assumption the same work shows to be unwarranted, as models frequently override retrieved evidence [7]. In safety-critical manufacturing, the cost of miscalibrated trust is not measured in inconvenience.

Second, the scenario in which these systems are most valuable is precisely the scenario in which verification support is most absent. Kernan Freire et al. [4] note that their tool was never intended to replace human-to-human interaction; rather, its value emerges when no human expert is present, or when the available expert does not know or recall the solution to a specific issue. They identify the night shift — a single operator running a production line with limited recourse to colleagues — as the concrete case. In that setting the operator's realistic alternatives are to guess, to search a lengthy manual under time pressure, or to halt production. A verified answer is materially better than all three; an unverified one may be worse than any of them.

The objective of this work is consequently not to increase operator reliance on automated systems in general. It is to make reliance appropriate to each individual answer — a property referred to in the human-AI interaction literature as trust calibration [7]. A system that communicates when its output is well-supported, when it is partially supported, and when it should not be acted upon at all allows the operator to act confidently where confidence is warranted and to seek human consultation where it is not. Notably, Singh et al. [3] identify evaluation of trust calibration, over-reliance, and under-reliance as explicit future work arising from their own deployment — an open question this thesis takes as its starting point.

By making per-answer reliability visible, the system is expected to support greater overall adoption — not because operators trust it uniformly more, but because they can identify which answers warrant action and which require human consultation. Whether this translates into measurable adoption gains requires a deployment study with practising operators, identified here as future work.

---

## 1.4 Research Objectives

This thesis pursues four objectives:

**Objective 1.** Design a domain-agnostic trust and transparency layer that operates as middleware atop any existing RAG pipeline, requiring only the user query, the retrieved chunks, and the generated answer as input, and requiring no modification to the underlying retrieval or generation components.

**Objective 2.** Develop a claim-level verification pipeline that decomposes generated answers into atomic verifiable statements and evaluates each against retrieved evidence using complementary mechanisms — semantic similarity, entity and numerical matching, negation detection, and natural language inference — arranged in a computational cascade.

**Objective 3.** Formalise an evidence-based decision mechanism that converts verification output into one of four actions — ANSWER, WARN, REFUSE, or ESCALATE — thereby treating groundedness as a signal that governs delivery rather than as a post-hoc evaluation metric.

**Objective 4.** Evaluate the resulting system against a standard RAG baseline on an expert-validated manufacturing safety benchmark, measuring the rate at which unsupported answers reach the user, the groundedness of delivered answers, decision accuracy, and answer coverage.

### Research Questions

**RQ1.** Can claim-level verification against retrieved evidence reliably distinguish grounded from ungrounded RAG-generated answers in manufacturing safety contexts?

**RQ2.** Does an evidence-based decision layer reduce the delivery of unsupported answers without unacceptably reducing the proportion of queries that receive an answer?

**RQ3.** Which verification mechanisms contribute most to detection performance, and do rule-based mechanisms targeting numerical precision and conditional exceptions address failure modes that entailment-based verification alone does not?

---

## 1.5 Scope and Limitations

The scope of this work is bounded in four respects, stated here to prevent overclaiming.

**The system does not reduce hallucination at generation time.** The underlying language model hallucinates at the same rate with or without the proposed layer. What the layer changes is the proportion of hallucinated answers that reach the user. Following the terminology of Ji et al. [8] and Maynez et al. [9], the system targets both intrinsic hallucination — generated content that contradicts the retrieved source — and extrinsic hallucination — content that can neither be supported nor refuted by the retrieved source. In both cases the intervention is at the point of delivery, not the point of generation.

**The system does not modify retrieval.** Improvements to chunking strategy, embedding models, or retrieval ranking are outside scope. Where retrieval fails to surface relevant evidence, the proposed layer can detect that the generated answer is unsupported, but it cannot supply the missing evidence.

**Human trust and adoption are not directly measured.** This work measures system reliability — hallucination rate at output, groundedness, decision accuracy — and provides transparency signals intended to support calibrated trust. Establishing that operator trust actually calibrates in response to those signals, and that this translates into greater real-world adoption, would require a deployment study with practising operators. This work does not conduct such a study. The anticipated outcome — that making per-answer reliability visible supports greater adoption by allowing operators to identify which answers warrant action — is identified as the primary direction for future work.

**Omission is addressed only partially.** Where an answer is technically accurate but omits safety-critical information present in the retrieved evidence, the retrieval coverage check may flag insufficiency. Where the relevant information was never retrieved, the system has no basis for detecting its absence.

---

## 1.6 Contributions

This thesis makes the following contributions:

1. **A pluggable trust and transparency architecture for RAG systems**, defined by a minimal interface (query, retrieved chunks, generated answer) that permits integration with any RAG pipeline without modification to that pipeline.

2. **Claim-level verification.** Prior work integrating natural language inference into RAG pipelines — notably Explain-RAG [10] — applies entailment checking at the level of the complete generated answer, producing a single label and confidence score. This thesis decomposes answers into atomic claims and verifies each independently, enabling identification of which specific statement within an otherwise acceptable answer is unsupported, and enabling per-claim source attribution.

3. **A hybrid cascade verification pipeline** combining semantic similarity, entity and numerical matching, negation detection, and NLI-based entailment checking. The rule-based components specifically target failure modes to which entailment models are known to be susceptible in technical documentation — numerically similar but materially different values, and conditional exception language such as "unless" or "except when" — which carry direct safety consequences in procedural guidance.

4. **A four-way decision formalisation** (ANSWER / WARN / REFUSE / ESCALATE) that converts verification output into delivery control. Existing verification approaches report groundedness as an informational score returned alongside the answer; the answer is delivered regardless of that score. This work treats the score as decision-governing.

5. **A three-layer transparency report** comprising a machine-readable trust score, a per-claim citation trail identifying the source document supporting each statement, and a natural-language explanation of the decision, addressing the distinct needs of automated auditing, safety engineering review, and shop-floor use respectively.

6. **Empirical evaluation** on an expert-validated manufacturing safety benchmark spanning three generations of manufacturing technology — a manually operated mill, a computer-controlled lathe, and a collaborative robot — against a standard RAG baseline.

---

## 1.7 Thesis Organisation

**Chapter 2** reviews related work across three areas: hallucination in retrieval-augmented generation and its taxonomies; verification and factual consistency methods, including natural language inference approaches; and prior work on RAG deployment in manufacturing and other safety-critical domains. The chapter establishes the specific gap this thesis addresses.

**Chapter 3** presents the design of the trust and transparency layer, describing each module, the cascade ordering of verification mechanisms and its rationale, the scoring formulation, the decision thresholds, and the interface that supports pluggability.

**Chapter 4** describes the implementation, including the baseline RAG pipeline, the knowledge base construction, model selections, and the engineering of each verification component.

**Chapter 5** presents the evaluation methodology and results, comparing the proposed system against the baseline across hallucination rate at output, groundedness, decision accuracy, and coverage, together with an ablation analysis of individual verification mechanisms.

**Chapter 6** discusses the findings, states the limitations of the approach, and identifies directions for future work.

---

## References

[1] Cited within Singh, R., Hamilton, A., White, A., Wise, M., Yousif, I., Carvalho, A., Shan, Z., Abrisham Baf, R., Mayyas, M., Cavuoto, L. A., & Megahed, F. M. (2025). *A Multimodal Manufacturing Safety Chatbot: Knowledge Base Design, Benchmark Development, and Evaluation of Multiple RAG Approaches.* arXiv:2511.11847. — **Note: these statistics originate from U.S. Bureau of Labor Statistics, Bureau of Economic Analysis, and Liberty Mutual sources cited in that paper. Retrieve and cite the primary sources directly rather than citing them second-hand.**

[2] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* Advances in Neural Information Processing Systems 33. arXiv:2005.11401.

[3] Singh, R., et al. (2025). *A Multimodal Manufacturing Safety Chatbot: Knowledge Base Design, Benchmark Development, and Evaluation of Multiple RAG Approaches.* arXiv:2511.11847.

[4] Kernan Freire, S., et al. (2024). *Knowledge Sharing in Manufacturing using Large Language Models: User Evaluation and Model Benchmarking.* arXiv:2401.05200. Published in *Frontiers in Artificial Intelligence*, 7:1293084. — **Verify author list and exact citation format from the published Frontiers version.**

[5] *Retrieval-Augmented Generation in Industry: An Interview Study on Use Cases, Requirements, Challenges, and Evaluation.* arXiv:2508.14066. — **Retrieve full author list and publication venue.**

[6] *Toward Epistemic Stability: Engineering Consistent Procedures for Industrial LLM Hallucination Reduction.* arXiv:2603.10047. — **Retrieve full author list and publication venue.**

[7] *Facet-Level Tracing of Evidence Uncertainty and Hallucination in RAG.* arXiv:2604.09174. — **Retrieve full author list and publication venue.**

[8] Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., Ishii, E., Bang, Y., Madotto, A., & Fung, P. (2023). *Survey of Hallucination in Natural Language Generation.* ACM Computing Surveys, 55(12), 1–38. arXiv:2202.03629.

[9] Maynez, J., Narayan, S., Bohnet, B., & McDonald, R. (2020). *On Faithfulness and Factuality in Abstractive Summarization.* Proceedings of ACL 2020. arXiv:2005.00661. — **Verify exact title and author list.**

[10] Nadaf, S., & Chavan, U. B. (2025). *Explain-RAG: An Explainable RAG Framework with Chain-of-Thought Reasoning, NLI Verification, and Source Attribution.* 2025 IEEE 4th International Conference for Advancement in Technology (ICONAT), Goa, India. DOI: 10.1109/ICONAT66879.2025.11362770.

---

## Citation Verification Notes

Every claim in this draft is drawn from a source verified during research. However, before submission you must:

1. **Retrieve full author lists** for references [5], [6], and [7] — these were identified via search result excerpts, and complete author lists were not confirmed.
2. **Replace second-hand statistics in [1]** with direct citations to the BLS, BEA, and Liberty Mutual primary sources.
3. **Verify [9]** — the exact title of the Maynez et al. paper should be confirmed against the ACL Anthology.
4. **Confirm the published version of [4]** — the Frontiers article and the arXiv preprint may differ slightly in content and pagination.
5. **Check whether [6] and [7] are peer-reviewed** — both are recent arXiv preprints. If unpublished, either note this or find published alternatives for load-bearing claims.

No statistic, quotation, or claim in this draft was generated without a verified source. Where a source could not be fully verified, that is flagged above rather than silently filled in.
