# Source Reuse Audit

## Copied From Source Repo 1

Path: `/Users/keith/Documents/New project/earnings-call-sentiment-from-voice-transcript-with-an-optional-video-24-02-2026-chunking-embedding`

- `src/earnings_call_sentiment/case_contract.py`
  Adapted into `src/vibesignal_ai/contracts/conversation_contract.py`
- `src/earnings_call_sentiment/io_utils.py`
  Adapted into `src/vibesignal_ai/utils/io_utils.py`
- `src/earnings_call_sentiment/schema_utils.py`
  Adapted into `src/vibesignal_ai/utils/schema_utils.py`
- `src/earnings_call_sentiment/observability.py`
  Reused structurally in `src/vibesignal_ai/utils/observability.py`
- `src/earnings_call_sentiment/transcriber.py`
  Adapted into `src/vibesignal_ai/audio/transcriber.py`
- `src/earnings_call_sentiment/audio/pause_features.py`
  Adapted into `src/vibesignal_ai/audio/pause_features.py`
- `src/earnings_call_sentiment/audio/segment_aggregate.py`
  Adapted into `src/vibesignal_ai/audio/segment_aggregate.py`
- `src/earnings_call_sentiment/question_shifts.py`
  Used as a structural starting point for `src/vibesignal_ai/features/shift_radar.py`

## Copied From Source Repo 2

Path: `https://github.com/keithtgrehan/earnings-call-signal-engine`

- `src/earnings_call_sentiment/nlp_sidecar.py`
  Used as a structural starting point for `src/vibesignal_ai/summaries/summary_rewriter.py`

## Adapted In VibeSignal AI

- Case metadata became strict conversation metadata
- Analyst-question shift logic became conversation shift radar
- Audio hesitation helpers now support interview-style clarity scoring
- Optional NLP sidecar became an optional structured summary layer
- Pipeline outputs now target safe comparison cards rather than finance reports

## Dropped On Purpose

- Guidance extraction and guidance revision matching
- Revenue, EPS, margin, and finance topic logic
- Event-study logic and pricing-window logic
- Company, ticker, exchange, sector, and fiscal-period fields
- Investor or trader framing
- Finance UI/reporting artifacts
- Model routing and finance-specific sidecars

## Original To VibeSignal AI

- WhatsApp and pasted-chat parsers
- Speaker normalization, language hints, turn grouping, response linking, and topical block detection
- Conversation-native consistency, directness, specificity, and hedging features
- Output safety validator and banned-term policy
- Soft-verdict safety validation and safe UI summary export
- Safe UI payload builders for the five MVP cards plus the canonical UI summary artifact
- Conversation-first README, docs, tests, and handoff notes
