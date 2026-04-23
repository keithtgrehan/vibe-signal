# Share Card / Low-Signal Report

## Commit-readiness verdict
YES WITH KNOWN LIMITS

## Exact validation performed
- Passed: `node --test tests/providerScreenModel.test.js`
- Passed: `node --test tests/localAnalysisGuardrails.test.js`
- Earlier in this hardening session, before the final UI-only compatibility fix, passed: `node --test tests/useQuota.test.js tests/mobileEventLogger.test.js tests/eventClient.test.js`
- Passed bounded Metro startup check:
  - `CI=1 node -e "spawn('npx', ['expo', 'start', '--offline', '--port', '8092'], ...)"`  
  - Metro reached startup and exited cleanly under the timed CI/offline wrapper.

## Validation attempted but not counted as a pass
- `npm test -- tests/providerScreenModel.test.js tests/localAnalysisGuardrails.test.js tests/analysisHistoryStore.test.js tests/useQuota.test.js tests/mobileEventLogger.test.js tests/eventClient.test.js`
  - launched `node --test` but did not complete cleanly in this shell session, so it is not used as evidence.
- `CI=1 npx expo export --platform android --output-dir dist-export`
  - started Metro but did not complete with a usable export artifact in this environment, so it is not counted as a bundle-validation pass.

## Exact remaining risks
- No on-device iPhone validation was performed.
- The share flow is still screenshot-prep plus text fallback, not real image export.
- Native share sheet behavior, screenshot ergonomics, keyboard overlap feel, and result reveal feel were not manually exercised on hardware.
- `src/components/PaywallCard.js` and `src/components/paywallViewModel.js` remain modified in the worktree but were outside this exact verification scope.

## Recommended manual device checks before release
1. Paste a very short repetitive sample and confirm the app says no strong shift was detected.
2. Paste a short but clearly changed exchange and confirm it does not downgrade to low-signal mode.
3. Reopen at least one older history item and confirm result rendering does not crash when fields are missing.
4. Toggle `Prepare for screenshot` on and off and confirm the card stays visually stable.
5. Tap `Share this signal` and confirm native share-sheet behavior on iPhone.
6. Tap `Copy insight text` and confirm clipboard contents are sensible.
7. Confirm the staged reveal feels smooth and not laggy on device.
8. Run one full analysis on device and confirm telemetry still lands as expected for `analysis`, `state`, `quota`, and `billing`.

## Suggested commit message
`Harden low-signal result handling and mobile share-card flow`
