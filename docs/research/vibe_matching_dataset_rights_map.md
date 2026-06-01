# Vibe Matching Dataset Rights Map

Metadata-only review. No downloads. No raw rows. Unclear sources are manual-review or blocked.

| Source | Modality | Task | License / terms posture | Commercial use | Training use | Research-only status | Download method | Safe Vibe use | Blocked Vibe use | Registry suggestion | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Synthetic Vibe Matching Fixtures | text | communication-fit fixtures | hand-authored synthetic fixtures | blocked until commercial approval | research-only synthetic training | approved for v0 harness | committed synthetic fixture | tests, deterministic eval, research baseline | real-user or public quality claims | `synthetic_vibe_matching` training-ready | high |
| GoEmotions | text | emotion annotations | manual-review | blocked | blocked | metadata-only | none | taxonomy comparison | emotion-truth claims | reference-only | low |
| DailyDialog | text | dialogue acts/topics | non-commercial/manual-review | blocked | blocked for matching v0 | metadata-only | none | dialogue-act design reference | raw rows or gold-label promotion | reference-only | low |
| EmpatheticDialogues | text | supportive dialogue | non-commercial/manual-review | blocked | blocked for matching v0 | metadata-only | none | repair/support phrasing reference | train response model by default | reference-only | low |
| MELD | multimodal | emotion dialogue | media-rights restricted | blocked | blocked | eval-only metadata | none | benchmark caveats | face/voice/body inference | eval-only | low |
| CMU-MOSI | multimodal | sentiment benchmark | restricted academic access | blocked | blocked | manual-review | none | calibration caveats | hidden-state or media inference | restricted | low |
| CMU-MOSEI | multimodal | sentiment benchmark | restricted academic access | blocked | blocked | manual-review | none | calibration caveats | hidden-state or media inference | restricted | low |
| MSP-Podcast | audio | speech emotion | restricted academic access | blocked | blocked | manual-review | none | audio-rights caveats | raw audio, health, identity inference | restricted | low |
| IEMOCAP | audio/video | acted emotion | restricted academic access | blocked | blocked | manual-review | none | acted-dialog caveats | treat acted labels as user truth | restricted | low |
| Civil Comments | text | toxicity | Kaggle/source terms require review | blocked | blocked | metadata-only | none | safety taxonomy caveats | protected-trait or relationship advice | reference-only | low |
| Wikipedia Toxicity/Subtypes | text | toxicity | manual-review | blocked | blocked | metadata-only | none | moderation taxonomy caveats | score people as abusive | reference-only | low |
| HateXplain | text | hate-speech rationales | manual-review | blocked | blocked | metadata-only | none | rationale design reference | protected-trait inference | reference-only | low |
| ProsocialDialog | text | safety/prosocial dialogue | manual-review | blocked | blocked | metadata-only | none | boundary-support review | train chatbot from rows | reference-only | low |
| Anthropic HH-RLHF | text | preference/safety | provider dataset terms require review | blocked | blocked | metadata-only | none | preference-data caveats | product gold labels | reference-only | low |
| SafetyBench | text | safety benchmark | manual-review | blocked | blocked | metadata-only | none | safety taxonomy reference | production safety claim | reference-only | low |
| Consent/coercion datasets | text/mixed | sensitive safety | harm/consent review required | blocked | blocked | manual-review | none | review criteria only | survivor-report ingestion, coercion scoring | blocked/manual-review | low |
| Neurodivergent communication datasets | transcript/text | accessibility research | ethics/consent review required | blocked | blocked | manual-review | none | accessibility process review | neurotype or diagnosis inference | blocked/manual-review | low |
| Dating/relationship public datasets | text/profile | dating/recommendation | source-specific manual review | blocked | blocked | manual-review | none | metadata/prior-art only | attraction, cheating, success prediction | blocked/manual-review | low |
| Similar open-source matching/dialogue repos | code/docs | implementation reference | repo-specific license review | blocked by default | blocked by default | metadata-only | none | architecture inspiration | copied code without attribution/license review | reference-only | low |
