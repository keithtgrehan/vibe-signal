# Experiments Plan

## Purpose

- Prepare VibeSignal AI for local calibration work without turning the production app into a heavy research stack
- Keep all dataset-specific work separate from the deterministic-first product path

## What Exists In This Pass

- Dataset location conventions in [datasets.py](/Users/keith/Desktop/VibeSignal AI/src/vibesignal_ai/experiments/datasets.py)
- Setup-status adapters for:
  - [meld_adapter.py](/Users/keith/Desktop/VibeSignal AI/src/vibesignal_ai/experiments/meld_adapter.py)
  - [muse_adapter.py](/Users/keith/Desktop/VibeSignal AI/src/vibesignal_ai/experiments/muse_adapter.py)
  - [msp_podcast_adapter.py](/Users/keith/Desktop/VibeSignal AI/src/vibesignal_ai/experiments/msp_podcast_adapter.py)
- Lightweight evaluation summary helper in [evaluation.py](/Users/keith/Desktop/VibeSignal AI/src/vibesignal_ai/experiments/evaluation.py)

## Intended Local Dataset Layout

- `data/MELD/`
- `data/MuSE/`
- `data/MSP-Podcast/`

## Current Scope Limits

- No training loops were added
- No dataset downloads were automated
- No experiment notebooks or CLI wrappers were added in this pass
- No production scoring depends on these datasets

## Recommended Next Steps

1. Add explicit local manifests for whichever datasets are licensed and available on this machine.
2. Create small calibration scripts outside the production pipeline for:
   - speech/acoustic threshold calibration
   - contradiction/alignment adapter sanity checks
   - emotion-shift correlation review
3. Use DailyDialog, GoEmotions, SNLI, MultiNLI, and ANLI only as future-support datasets for narrow calibration questions, not as direct product labels.

## Licensing And Usage Notes

- Each dataset keeps its own original license and access terms
- Do not treat these adapters as a redistribution layer
- Keep experiment artifacts and reports separate from user-facing product outputs
