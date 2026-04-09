# Provider Validation Proof

## Scope

This proof pass focused on replacing assumptions with execution evidence where the current environment allowed it.

## What Was Executed

- Full Python test suite:
  - see [python_test_run.txt](/Users/keith/Desktop/VibeSignal AI/docs/proof/phase_validation_2026-04-07/python_test_run.txt)
- Targeted Python provider tests:
  - see [python_provider_test_run.txt](/Users/keith/Desktop/VibeSignal AI/docs/proof/phase_validation_2026-04-07/python_provider_test_run.txt)
- Real invalid-key network attempts against provider endpoints:
  - see [provider_invalid_key_network.txt](/Users/keith/Desktop/VibeSignal AI/docs/proof/phase_validation_2026-04-07/provider_invalid_key_network.txt)

## Provider-By-Provider Status

### OpenAI

- Invalid-key live request: executed
- Result:
  - HTTP status: `401`
  - normalized status: `invalid_credentials`
- Valid-key live request: not executed
- Reason:
  - no test key was available in this environment

### Anthropic

- Invalid-key live request: executed
- Result:
  - HTTP status: `401`
  - normalized status: `invalid_credentials`
- Valid-key live request: not executed
- Reason:
  - no test key was available in this environment

### Groq

- Invalid-key live request: executed
- Result:
  - HTTP status: `403`
  - normalized status: `invalid_credentials`
- Valid-key live request: not executed
- Reason:
  - no test key was available in this environment

## What This Does And Does Not Prove

- Proven:
  - the repo has a live invalid-key handling path that maps these provider responses into the expected normalized status category
- Not proven:
  - a valid-key ready path against a real provider
  - real provider summary generation from the mobile runtime on this machine

## Notes

- A fake malformed key was used for these network attempts.
- No real provider key was written to disk.
- One provider response echoed a key-shaped string in the raw error body; that proof artifact was redacted immediately after capture.
