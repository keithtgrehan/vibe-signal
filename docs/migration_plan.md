# Migration Plan

1. Lift only reusable contract, pipeline, observability, schema, transcription, pause-feature, and optional-sidecar patterns into a new standalone repo.
2. Rename the package namespace to `vibesignal_ai`.
3. Remove all legacy market-domain fields and report concepts.
4. Replace prior domain scoring logic with conversation-native deterministic features.
5. Add a strict safety validator for all UI and summary strings.
6. Keep any summary layer optional and late-bound.
7. Verify the MVP with synthetic tests and document what remains.
