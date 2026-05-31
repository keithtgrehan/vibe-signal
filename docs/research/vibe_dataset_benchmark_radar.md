# Vibe Dataset Benchmark Radar

This is the canonical R2 dataset and benchmark radar for Vibe Engine.

## Operating posture

- No dataset downloads are performed in this PR.
- No raw dataset rows are committed.
- No external dataset row becomes a Vibe gold label automatically.
- Dataset labels are annotator judgments or task labels, not internal truth.
- External datasets are benchmark, calibration, literature, or harm-review references by default.
- Synthetic fixtures are the immediate evaluation path.
- Model training remains out of scope unless future rights, privacy, provenance, safety, and evaluation gates all pass.
- Sensitive-population, coercion, harassment, disability, medical, survivor-report, and neurodivergent-language sources require harm review and profiling blocks before any use beyond metadata notes.

## Product boundaries

Vibe Engine supports observable communication-pattern review: clarity, agency, overload reduction, explicit asks, boundary-safe language, consent wording, and repair messages. It must never infer neurodivergence, protected traits, diagnosis, attraction, deception, hidden intent, or internal emotional truth from text, audio, video, screenshots, or provider output.

## Candidate source radar

| Source | Modality | Default Vibe status | Safe reference use | Blocked use |
| --- | --- | --- | --- | --- |
| GoEmotions | text | metadata-only benchmark reference | Compare taxonomy shape for perceived/annotated language categories. | Treat labels as emotional truth or use rows as product gold labels. |
| DailyDialog | text | metadata-only benchmark reference | Dialogue-act and topic-shift evaluation design. | Commit raw conversations or auto-promote labels. |
| EmpatheticDialogues | text | metadata-only benchmark reference | Supportive phrasing review for clarity and repair scaffolds. | Train a response model by default. |
| MELD | multimodal | metadata-only benchmark reference | Multimodal benchmark constraints and media-rights notes. | Analyze faces, voices, or bodies for biometric conclusions. |
| CMU-MOSEI | multimodal | metadata-only benchmark reference | Calibration-design reference only. | Infer internal states, attraction, identity, or diagnosis. |
| CMU-MOSI | multimodal | metadata-only benchmark reference | Calibration-design reference only. | Use media as product input without rights and safety review. |
| MSP-Podcast | audio | metadata-only benchmark reference | Audio-rights and benchmark-design notes. | Commit raw audio or draw health/identity conclusions. |
| IEMOCAP | audio/video | metadata-only benchmark reference | Acted-dialog benchmark caveats. | Treat acted labels as user truth. |
| Wikipedia Toxicity Subtypes | text | metadata-only safety reference | Harassment and boundary-language evaluation design. | Score a person as abusive or manipulative. |
| Civil Comments | text | metadata-only safety reference | Toxicity and moderation caveats. | Use labels as dating or relationship advice. |
| Wikipedia Detox | text | metadata-only safety reference | Rewrite-safety study reference. | Generate coercive rewrites. |
| HateXplain | text | metadata-only safety reference | Rationale annotation design notes. | Infer protected traits about users or speakers. |
| Anthropic HH-RLHF | text | metadata-only safety reference | Preference-data caveats for safe-response review. | Use provider preference rows as Vibe gold labels. |
| ProsocialDialog | text | metadata-only safety reference | Prosocial response and boundary-support review. | Auto-send user conversations to a provider. |
| Bot Adversarial Dialogue | text | metadata-only safety reference | Adversarial red-line case design. | Train or deploy a chatbot from rows. |
| SafetyBench | text | metadata-only safety reference | Safety benchmark taxonomy reference. | Claim production safety based on benchmark mention alone. |
| MeTooMA | text | literature-only blocked reference | Harassment harm-review framing. | Download survivor-report rows or use for profiling. |
| SafeCity | text/geospatial | literature-only blocked reference | Safety and privacy risk review. | Location profiling or raw report ingestion. |
| ComMA | text | literature-only blocked reference | Coercion/manipulation taxonomy review. | Score manipulation or advise coercion. |
| Bangla cyberbully/harassment/threat dataset | text | metadata-only safety reference | Cross-language safety taxonomy caveats. | Use without language, rights, and harm review. |
| Workplace Sexual Harassment repo | text | literature-only blocked reference | Boundary and harassment policy context. | Workplace/hiring decisions or survivor-report ingestion. |
| ASDBank/TalkBank | language transcript | metadata-only/literature reference | Accessibility and consent-model review. | Infer autism or disability from text. |
| AUTALIC | language transcript | metadata-only/literature reference | Neurodivergent communication support literature review. | Classify neurotype. |
| AphasiaBank/TalkBank | language transcript | metadata-only/literature reference | Accessibility and consent-model review. | Infer medical status. |
| Synthetic Vibe fixtures | text | commit-safe synthetic evaluation | Immediate deterministic tests and review packet fixtures. | Treat synthetic examples as real user data. |

## Promotion rules

External rows can inform evaluation design only after rights, consent, privacy, and harm review. They cannot be written into `data/vibe_gold/` without an explicit human review workflow that records provenance, allowed use, and evidence spans. Synthetic fixtures are allowed for tests because they are hand-authored and not copied from private conversations or external datasets.

## Next review gates

Before any future use beyond metadata references, require a source-specific rights review, privacy review, harm review, provenance hash, raw-body storage decision, commit decision, and explicit blocked-use list. Future evaluation claims must be checked by the Vibe evaluation gates and claims matrix.
