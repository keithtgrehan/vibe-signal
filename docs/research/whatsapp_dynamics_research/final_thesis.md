# WhatsApp Dynamics Research Thesis

Build a local-only, evidence-first WhatsApp dynamics research report that summarizes observable patterns and optional audio-feature divergence without claiming true emotions, hidden intent, or relationship health.

The prototype should analyze only redacted local artifacts under `data/restricted/private_whatsapp`, write private-derived reports under the same restricted tree, and expose only aggregate communication dynamics using `self` and `other`.

The four report pillars are:

- Possible emotion/cue trajectory based on aggregate observable wording and timing clusters.
- Conversational asymmetry metrics based on response latency, word count, message count, and unanswered ask candidates.
- Multi-modal synchronicity based on optional text/audio feature divergence, never emotional truth.
- Communication pattern summary that explicitly states it is not a relationship health diagnosis.

GoEmotions, VAD/PAD, and THUNLP Model_Emotion are research inspirations only. Useful ideas include 27-category coverage, VAD proxy framing, prompt/evaluation structure, category mapping, and activation-analysis documentation style. No code, prompts, models, datasets, or production claims should be copied from those sources without a separate license/source review.

The implementation should fail closed on privacy: no raw private WhatsApp data, no participant names, no exact private examples, no external APIs, no live Vibe Signal integration, and no committed restricted artifacts.
