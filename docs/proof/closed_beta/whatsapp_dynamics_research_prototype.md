# WhatsApp Dynamics Research Prototype

## What Was Built

- Local-only analyzer: `tools/analyze_whatsapp_dynamics.py`
- Synthetic fixture exporter: `tools/export_synthetic_dynamics_fixtures.py`
- Weak-label/synthetic baseline scaffold: `tools/train_private_dynamics_baseline.py`
- Safety tests for restricted paths, aggregate-only reports, audio schema validation, synthetic export, and baseline input refusal.
- Research docs for taxonomy, final thesis, and a future action endpoint design.

## What Was Not Built

- No production endpoint.
- No live Vibe Signal backend or frontend integration.
- No deterministic engine change after inspecting the existing cue taxonomy and matcher files.
- No external API calls.
- No analytics, tracking, auth, payment, or provider wiring.
- No relationship score, attraction label, deception label, diagnosis, neurotype label, or hidden-state output.

## Why This Is Local-Only

Private WhatsApp material must remain under `data/restricted/private_whatsapp`. The analyzer writes private-derived reports under the same restricted tree by default and refuses non-restricted output unless explicitly overridden for synthetic-safe use. Model artifacts default to the ignored restricted model directory.

## Four Report Pillars

- Emotional trajectory map: reframed as a possible emotion/cue trajectory using aggregate observable wording patterns and timing clusters.
- Conversational asymmetry metrics: response latency, word count, message count, direct asks, and unanswered ask candidates.
- Multi-modal synchronicity: optional text/audio feature divergence only.
- Relationship health synthesis: explicitly reframed as a communication pattern summary, not a diagnosis or score.

## Safety Reframing

The prototype summarizes observable wording patterns, communication pressure, timing ambiguity, repair opportunity, response imbalance, evidence-backed cues, and low-confidence signals that require human interpretation.

It does not read emotions, score relationships, identify hidden states, infer intent, or prove what someone means.

## Private Data Handling

- Uses `self` and `other` only.
- Does not print raw text.
- Does not print participant names.
- Does not write raw examples into reports.
- Does not commit restricted private reports, processed messages, raw chats, audio telemetry, embeddings, matrices, private labels, or models.
- Synthetic fixtures are generated from fixed templates and aggregate category weights only.

## Research Inspiration Notes

- GoEmotions inspired broad category coverage and safe mapping from 27 labels to observable cue families.
- VAD/PAD inspired bounded valence, arousal, and dominance proxy framing.
- THUNLP Model_Emotion inspired prompt/evaluation structure and category-level documentation ideas.
- No code, model weights, prompts, datasets, or production claims were copied from those sources.
- Any direct source use would require a separate license/source review.

## Validation Commands

```bash
python -m py_compile tools/analyze_whatsapp_dynamics.py tools/export_synthetic_dynamics_fixtures.py tools/train_private_dynamics_baseline.py
python -m pytest tests/test_whatsapp_dynamics_research_safety.py -q
python -m pytest tests/test_private_whatsapp_ingestion_safety.py -q
python scripts/check_no_raw_content_leaks.py
python scripts/check_public_copy_safety.py
python scripts/check_vibe_restricted_artifacts.py --staged
git diff --check
```

## Known Limitations

- Metrics are deterministic heuristics over redacted local data.
- Ask detection can miss indirect requests and overcount rhetorical questions.
- Latency can reflect sleep, work, travel, device access, calls, or in-person follow-up.
- Audio telemetry is optional and cannot prove emotion or intent.
- Weak-label/synthetic training is not human-reviewed and is not a model-quality claim.

## Next Manual Step

Review 100 private windows tomorrow before treating any model output as useful.
