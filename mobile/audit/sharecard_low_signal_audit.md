# Share Card / Low-Signal Audit

## Files changed
- `src/screens/providerScreenModel.js`
- `src/screens/localAnalysisGuardrails.js`
- `src/screens/ProviderSettingsScreen.js`
- `src/components/SignalShareCard.js`
- `tests/providerScreenModel.test.js`
- `tests/localAnalysisGuardrails.test.js`
- `audit/sharecard_low_signal_audit.md`
- `audit/sharecard_low_signal_report.md`

## Risks reviewed
- Weak-input detection ordering and thresholds
- Whether valid short inputs can be downgraded incorrectly
- Handling of repetitive input, no-shift input, and high-similarity input
- Missing `analysisMode` / `suggestion` fields
- Older saved/history payload compatibility
- Render safety when result payloads are partial
- `SignalShareCard` behavior with partial props
- Screenshot-prep mode enter/exit behavior
- Clipboard fallback behavior
- Reveal sequencing and cleanup behavior
- Duplicate tap or double-render risk in result actions

## Issues found
1. Older saved/history payloads were being reopened directly in `ProviderSettingsScreen`, which meant new fields like `analysisMode` and `suggestion` were not normalized before render.
2. Accidental duplicate files existed in `src/screens/`:
   - `ProviderSettingsScreen 2.js`
   - `ProviderSettingsScreen 3.js`
   - `providerScreenModel 2.js`
   - `providerScreenModel 3.js`
   These were clear commit-noise and regression-risk candidates if staged accidentally.
3. Test coverage around low-signal boundaries was too thin for commit confidence:
   - no explicit "short but valid" signal case
   - no explicit "long but still low-signal" case
   - no explicit older-payload / missing-field guardrail case

## Fixes applied
1. Normalized all results passed through `presentResult(...)` with `sanitizeLocalAnalysisResult(...)` before state is set. This hardens history reopen behavior and partial payload safety.
2. Removed the accidental duplicate screen/model files from `src/screens/`.
3. Added focused tests for:
   - short but clearly shifted input staying in signal mode
   - long high-similarity input falling back to low-signal mode
   - missing `analysisMode` / `suggestion` fields staying render-safe in the guardrail sanitizer

## Issues intentionally left unchanged
1. Share remains screenshot-prep plus text/clipboard fallback only. No image export library was added.
2. Share-action buttons are not single-flight locked; they rely on ordinary press behavior and are acceptable for this scope.
3. No native iPhone validation was performed here, so keyboard feel, screenshot ergonomics, and native share-sheet behavior remain manual-check items.
4. `src/components/PaywallCard.js` and `src/components/paywallViewModel.js` are still modified in the worktree from earlier work, but they were outside this exact audit scope and were not changed in this pass.
5. `../README 2.md` is untracked outside `mobile/` and was intentionally left untouched because it is out of scope.
