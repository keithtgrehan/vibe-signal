# Dependency Matrix

## Base Path

- Purpose: lightweight deterministic-first app runtime
- Included by default:
  - `emoji`
  - `langdetect`
  - `rapidfuzz`
  - `spacy`
  - `pysbd`
- Notes:
  - This is the default and recommended local path
  - No Torch-based audio stack is required in the base path

## Optional `audio_advanced`

- Purpose: heavier local acoustic support
- Packages:
  - `opensmile`
  - `silero-vad`
- Runtime flags:
  - `VIBESIGNAL_ENABLE_OPENSMILE=1`
  - `VIBESIGNAL_ENABLE_VAD=1`
- Notes:
  - Disabled by default
  - Structured metrics only
  - Core pipeline still runs when these packages are missing

## Optional `nli`

- Purpose: local contradiction/alignment support for Response Consistency Check
- Packages:
  - `transformers`
  - `torch`
- Runtime flags:
  - `VIBESIGNAL_ENABLE_NLI=1`
  - `VIBESIGNAL_NLI_MODEL=<local model path or cached model id>`
- Notes:
  - Disabled by default
  - Uses local model loading only
  - Current adapter expects the model to already be available locally

## Optional `experiments`

- Purpose: local calibration scaffolding and dataset evaluation helpers
- Packages:
  - none required in this pass
- Notes:
  - This is not a production inference path
  - Dataset adapters are scaffolding only

## Optional `providers_openai`

- Purpose: OpenAI API connector
- Packages:
  - `openai`
- Notes:
  - Disabled by default
  - Requires explicit provider consent and configuration

## Optional `providers_anthropic`

- Purpose: Anthropic Messages connector
- Packages:
  - `anthropic`
- Notes:
  - Disabled by default
  - Requires explicit provider consent and configuration

## Optional `providers_groq`

- Purpose: Groq connector
- Packages:
  - `groq`
- Notes:
  - Disabled by default
  - Requires explicit provider consent and configuration

## Dataset Notes

- Calibration-ready scaffolding added for:
  - MELD
  - MuSE
  - MSP-Podcast
- Future-support notes included for:
  - DailyDialog
  - GoEmotions
  - SNLI
  - MultiNLI
  - ANLI
