# Vibe Cue Taxonomy

## Purpose

The Vibe cue taxonomy is a deterministic-first layer for observable message features. It emits evidence objects for visible text cues such as direct asks, specificity, hedging, urgency, reassurance, pressure, conflict, alignment, topic shifts, ambiguity, cognitive load, unclear asks, overloaded messages, escalation-risk patterns, repair opportunities, boundary pressure, consent clarity, and response timing.

It does not infer true emotions, diagnosis, attachment style, attraction, hidden intent, deception, or whether a person is a certain kind of person.

## Source Scope

- Synthetic fixtures in tests.
- Local user-supplied text passed directly to the analyzer.
- No raw datasets, external dataset rows, downloads, model training, embeddings, vector stores, or provider calls.

## Config

The taxonomy lives in `configs/vibe_cue_taxonomy.yml`. Each cue row includes:

- `cue_id`
- `cue_family`
- regex `patterns` or a named deterministic `computed_rule`
- optional `reducers`
- `confidence`
- `explanation`
- `safe_phrase`
- blocked interpretations

## Evidence Objects

The analyzer returns evidence objects with:

- `cue_id`
- `cue_family`
- `evidence_text`
- `span_start`
- `span_end`
- `confidence`
- `explanation`
- `safe_phrase`

The legacy evidence aliases `cue_name`, `start_offset`, and `end_offset` are retained for existing review-packet and evidence tests.

## Safe Phrasing

Generated cue text must use phrasing such as:

- `message contains ...`
- `text cues suggest ...`

Generated cue text must not say a person feels something, diagnose anyone, score attachment style, optimize persuasion, or tell a user how to make someone like them.

## CLI

```bash
python scripts/analyze_vibe_text.py \
  --text "Maybe confirm Friday? No pressure, when you can."
```

The CLI runs locally and returns JSON. It reports `provider_used: false`, `model_trained: false`, and `vector_artifacts_created: false`.

## Intentionally Not Implemented

- External corpus ingestion.
- Dataset downloads.
- Model training or fine-tuning.
- Embeddings or vector indexes.
- Provider/API fetching.
- Emotion-truth or diagnostic claims.
