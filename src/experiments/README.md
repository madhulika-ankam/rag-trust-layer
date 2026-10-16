# Experiments behind the Chapter 5 tables

Every script here reads frozen artefacts in `data/processed/` and writes a
table to stdout. None of them regenerates an answer, so re-running any of
them reproduces a published number exactly.

Run from the repository root with `venv/bin/python src/experiments/<name>.py`.

| script | what it produces | thesis use |
|---|---|---|
| `claim_length.py` | claim-length distribution straight from the decomposer, no NLI — seconds, not minutes | Ch 3, decomposition design |
| `length_effect.py` | entailment against claim length, by band, with Spearman correlations and the similarity control | **Ch 5, the central finding** |
| `claim_quality_before_after.py` | claim counts, lengths, entailment and verdicts for two `verified.jsonl` files | Ch 5, effect of the decomposer fix |
| `granularity.py` | chunk vs sentence NLI granularity on the 30 labelled answers | Ch 3, §3.6 |
| `granularity_by_length.py` | the same comparison computed WITHIN each claim-length band, on labelled perturbation pairs — shows sentence wins at every length, and carries the control condition for the length effect | **Ch 3 §3.6 and Ch 5** |
| `length_or_propositions.py` | tests whether claim length or proposition count drives the collapse — a **negative result**, the two cannot be separated in this corpus | Ch 5, stated as a limitation |
| `escalate_rules.py` | five ESCALATE rules: false alarms on fully-good answers, contradiction counts | Ch 3, §3.6 |
| `aggregator_comparison.py` | four answer-level aggregators plus a threshold sweep under the acceptance constraints | Ch 3, §3.7 |
| `ground_truth_table.py` | all 30 labelled answers, decision then vs now, by human judgement group | **Ch 5, the headline table** |
| `dump_per_chunk_features.py` | regenerates `perchunk_*.jsonl` — per-chunk similarity, NLI, entity and negation features for all claims | input to the three scripts above |

## Regenerating the inputs

```bash
# per-chunk features (slow: runs NLI over 161 answers x 5 chunks)
venv/bin/python src/experiments/dump_per_chunk_features.py \
    data/processed/perchunk_sentence.jsonl sentence
venv/bin/python src/experiments/dump_per_chunk_features.py \
    data/processed/perchunk_chunk.jsonl chunk

# the verified records the whole evaluation rests on
venv/bin/python -m src.run_verification
```

## A caution about `ground_truth_table.py`

It reads the live `AGGREGATOR` from `src/trust_layer/scorer.py`. It used to
hardcode `'current'`, which made it silently disagree with the system it was
supposed to be measuring — the 30-answer table said 7/13 fully-good answers
delivered while the system actually delivered 6. If this script and a sweep
ever disagree, check that both are reading the same configuration before
believing either.
