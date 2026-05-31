# Vibe Dataset Radar

This radar is metadata-only. No external dataset is downloaded in this PR.

External datasets are benchmark and calibration references by default. Dataset labels are annotator judgments, not truth. No dataset row becomes a product gold label automatically.

| Source | Default Vibe Use | Blocked Use |
| --- | --- | --- |
| GoEmotions | Label-taxonomy comparison for communication-pattern evaluation design | True-emotion inference or model training by default |
| DailyDialog | Dialogue-act and conversational structure reference | Product gold labels or raw body commits |
| EmpatheticDialogues | Supportive-response benchmark reference | Claiming empathy labels are emotional truth |
| MELD | Multimodal benchmark reference | Inferring true emotion from voice/video |
| CMU-MOSEI | Multimodal benchmark reference | Biometric or attraction inference |
| CMU-MOSI | Multimodal benchmark reference | Deception or diagnosis claims |
| MSP-Podcast | Audio benchmark reference | Mental-health or identity inference |
| IEMOCAP | Audio/video benchmark reference | True-emotion claims |
| Toxicity/harassment placeholder | Boundary-safe language benchmark reference | Scoring people as manipulative or abusive |
| Synthetic Vibe fixtures | Immediate evaluation path | Treating synthetic examples as real user data |

## Default Posture

- Benchmark/calibration reference only.
- Metadata-only registry rows.
- License and terms review required before any download.
- Synthetic fixtures are the immediate evaluation path.
- No model training in this PR.
- No provider calls in this PR.
