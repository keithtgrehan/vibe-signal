# VibeSignal AI

VibeSignal AI is a standalone local repo for deterministic-first conversation pattern analysis.

Some users explore changes in communication patterns when trying to understand relationship dynamics.

The current bounded pass keeps the system deterministic-first, comparison-based, and reviewable. It does not make verdicts, does not attempt truth detection, and does not produce cheating or pass/fail claims.

## What It Does

- Analyzes WhatsApp exports, pasted chats, and interview/audio transcript segments
- Normalizes speakers, shorthand, emoji, attachment placeholders, and language hints
- Produces structured message, turn, response-pair, topical-block, shift-event, and UI-summary artifacts
- Keeps any summary layer optional and late-bound

## Architecture

- `src/vibesignal_ai/commerce`: anonymous app-user identity, usage metering, purchase verification contracts, entitlement computation, and gated metered analysis
- `src/vibesignal_ai/contracts`: strict conversation metadata contract and path builder
- `src/vibesignal_ai/ingest`: WhatsApp, pasted-chat, audio ingest, normalization, and segmentation
- `src/vibesignal_ai/pipeline`: deterministic orchestration and artifact enforcement
- `src/vibesignal_ai/features`: transparent scoring and comparison modules
- `src/vibesignal_ai/providers`: optional external provider connectors
- `src/vibesignal_ai/safety`: output policy, banned terms, and soft-verdict validators
- `src/vibesignal_ai/summaries`: optional structured summary layer
- `src/vibesignal_ai/ui`: safe UI payload builders
- `mobile/`: mobile-ready secure credential storage, provider state helpers, and billing scaffolding

## Supported Modes And Inputs

- Modes: `relationship_chat`, `interview`, `generic`, `mixed_session`
- Inputs: WhatsApp exports, pasted chat, audio note, interview audio, generic audio
- Source metadata also supports mixed text-plus-audio sessions for future flows

## Current Deterministic Features

- Conversation Shift Radar
- Response Consistency Check
- Confidence & Clarity
- What Changed?
- Grouped turns, topical blocks, response linking, and event exports

## Output Artifacts

Each run writes a deterministic artifact bundle including:

- `raw/messages.json`
- `processed/segments.json`
- `processed/turns.json`
- `processed/response_pairs.json`
- `processed/topical_blocks.json`
- `derived/shift_radar.json`
- `derived/consistency.json`
- `derived/confidence_clarity.json`
- `derived/what_changed.json`
- `exports/shift_events.csv`
- `exports/consistency_events.csv`
- `exports/ui_payloads.json`
- `exports/pattern_summary.json`
- `exports/ui_summary.json`
- `exports/optional_summary.json` only when summary mode is enabled
- `conversation_metadata.json`
- `logs/` observability artifacts

## Safety Policy

- Output language stays descriptive and comparison-based
- The system avoids verdicts, accusations, motive claims, hidden-intent claims, and outcome predictions
- UI-facing and summary-facing strings pass through banned-term and soft-verdict validators
- Optional summaries consume structured signals only, never raw chat or raw audio

## Local-First Provider Modes

- `local_only`
  - default
  - no external provider calls
- `external_summary_optional`
  - only after explicit opt-in
  - sends a minimal structured signal bundle and optional selected excerpts
- `provider_disabled`
  - explicit fallback state when a provider is not configured or not enabled

Local deterministic results and external AI summaries are stored separately.

## Local Dependencies

This repo keeps the default path lightweight:

- `emoji` for readable emoji normalization
- `langdetect` for lightweight language hints
- `rapidfuzz` for conservative speaker alias cleanup
- `pySBD` for sentence-boundary detection in chat and transcript text
- `spaCy` for deterministic structure cues that strengthen directness, specificity, and clarity scoring

Install locally with:

```bash
python3 -m pip install --user -r requirements.txt
```

If `spaCy` installs without the small English model, the code still falls back to a blank sentencizer and regex heuristics. To enable the richer lightweight English cues locally, run:

```bash
python3 -m spacy download en_core_web_sm
```

## Optional Heavy Integrations

- `openSMILE`:
  - package: `opensmile`
  - runtime flag: `VIBESIGNAL_ENABLE_OPENSMILE=1`
  - purpose: optional structured acoustic support only
- `Silero VAD`:
  - package: `silero-vad`
  - runtime flag: `VIBESIGNAL_ENABLE_VAD=1`
  - purpose: optional pause and silence support only
- local NLI contradiction/alignment adapter:
  - packages: `transformers`, `torch`
  - runtime flag: `VIBESIGNAL_ENABLE_NLI=1`
  - purpose: optional statement-relation support for Response Consistency Check

These heavy integrations are disabled by default. The base pipeline still runs when none of them are installed.

For newer packaging tools, the repo also declares optional groups in [pyproject.toml](/Users/keith/Desktop/VibeSignal AI/pyproject.toml):

- `audio_advanced`
- `nli`
- `experiments`
- `providers_openai`
- `providers_anthropic`
- `providers_groq`

On this machine's older system `pip`, the reliable path is still direct package installation plus `PYTHONPATH=src`.

Optional local audio support still depends on `ffmpeg`, plus `numpy`, `soundfile`, and `faster-whisper` if you want raw-audio transcription.

## Experiments

- Calibration scaffolding now exists for:
  - MELD
  - MuSE
  - MSP-Podcast
- Future-support notes are included for:
  - DailyDialog
  - GoEmotions
  - SNLI
  - MultiNLI
  - ANLI
- These experiment adapters are not part of the production scoring path.

## Optional External Providers

- OpenAI
  - provider flag: `VIBESIGNAL_ENABLE_OPENAI_PROVIDER=1`
  - global flag: `VIBESIGNAL_ENABLE_EXTERNAL_PROVIDERS=1`
- Anthropic
  - provider flag: `VIBESIGNAL_ENABLE_ANTHROPIC_PROVIDER=1`
  - global flag: `VIBESIGNAL_ENABLE_EXTERNAL_PROVIDERS=1`
- Groq
  - provider flag: `VIBESIGNAL_ENABLE_GROQ_PROVIDER=1`
  - global flag: `VIBESIGNAL_ENABLE_EXTERNAL_PROVIDERS=1`

All provider paths are off by default. Provider summaries use structured signals first and remain separate from local deterministic outputs.

This repo includes config interfaces for:

- `byok`
- `backend_proxy`
- `disabled`

It does not store real provider API keys in source code. Mobile BYOK storage now lives in the [mobile support layer](/Users/keith/Desktop/VibeSignal AI/mobile) and is implemented with `expo-secure-store`, not AsyncStorage or plaintext storage. A backend proxy service still is not implemented in this repo.

## Mobile Secure Storage

- The repo now includes a minimal mobile support module under [mobile/](/Users/keith/Desktop/VibeSignal AI/mobile)
- Secure credential storage uses `expo-secure-store`
- Secure device installation identity storage also uses `expo-secure-store`
- BYOK credentials fail closed when secure storage is unavailable
- Installation identity bootstrap also fails closed when secure storage is unavailable
- Disconnecting a provider deletes its stored credential
- Provider readiness payloads now distinguish:
  - `local_only`
  - `provider_disabled`
  - `provider_not_configured`
  - `secure_storage_unavailable`
  - `provider_enabled_no_credential`
  - `provider_ready`
  - `provider_error`

This keeps the UI from overstating whether an external provider is actually usable.

## Subscription And Entitlements

- The sellable app path now assumes:
  - `10` free completed analyses per anonymous device-scoped app user
  - then `€2.99/month` for unlimited use
- Billing scaffolding is prepared for:
  - Apple StoreKit product ID `vibesignal_pro_monthly_ios`
  - Google Play Billing product ID `vibesignal_pro_monthly_android`
- Usage metering counts completed analyses only
- Entitlement decisions are made in the authoritative Python commerce layer, not only in mobile UI state
- Purchase verification contracts and restore/sync flows are present, but live App Store / Play receipt-token verification still depends on store-console wiring that is not completed in this repo yet
- The mobile billing layer now normalizes Apple and Google purchase artifacts, but it still treats them as unverified until the Python entitlement authority confirms status
- BYOK provider credentials remain separate from billing and are still stored only in secure mobile storage

## Local Run

```bash
python3 -m pip install --user -r requirements.txt
PYTHONPATH=src python3 -m vibesignal_ai analyze --input tests/fixtures/relationship_chat_hardened.txt --type whatsapp --mode relationship_chat --out ./outputs --rights-asserted
```

If you also want heavier optional integrations, install them separately as needed:

```bash
python3 -m pip install --user opensmile
python3 -m pip install --user silero-vad
python3 -m pip install --user transformers torch
python3 -m pip install --user openai anthropic groq
```

For a direct repo run:

```bash
PYTHONPATH=src python3 -m vibesignal_ai analyze --input tests/fixtures/relationship_chat_hardened.txt --type whatsapp --mode relationship_chat --out ./outputs --rights-asserted
```

Optional provider summaries are only intended for:

- mobile BYOK flows that retrieve the provider credential from secure on-device storage, or
- a future backend proxy path that keeps provider-owned keys off the client

The plain Python CLI in this repo is still best treated as a local-only path unless you explicitly wire one of those credential flows yourself.

On newer `pip` versions, optional dependency groups from `pyproject.toml` should also work. On this machine's system `pip 21`, `PYTHONPATH=src` remained the reliable local run path.

For the mobile support layer, install JavaScript dependencies in a future Expo shell with:

```bash
cd mobile
npm install
```

This machine does not currently have `node` or `npm`, so the mobile unit tests were added but could not be executed here in this pass.
