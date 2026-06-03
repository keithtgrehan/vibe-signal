# App Review Notes

Status: draft operator notes. This does not claim App Store approval or compliance.

## Product Boundary

Vibe Signal is a communication-support tool. It reviews observable wording cues and gives cautious, evidence-backed suggestions. It is not a dating assistant, attraction detector, deception detector, diagnosis tool, therapist, lie detector, manipulation coach, or emotional-truth engine.

## Data Handling Summary

- The app is configured to call the Render backend through `EXPO_PUBLIC_API_URL`.
- Closed-beta QA uses synthetic examples first.
- Users are warned to submit only permissioned messages and avoid highly sensitive content.
- This sprint does not add analytics/tracking SDKs.
- This sprint does not add raw message persistence, external datasets, embeddings, vectors, checkpoints, model files, or training.

## Reviewer Checklist Before Submission

- Confirm all placeholder text is removed from App Store Connect metadata.
- Confirm privacy/support/delete/export links are live and legally reviewed.
- Confirm consent gate appears before private/pasted analysis.
- Confirm the low-signal fallback avoids overreading short/context-light text.
- Confirm the UI does not show numeric confidence as a user-facing trust claim.
- Confirm legal review approves any statement about storage, deletion, export, and beta handling.

## External Policy References

- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Expo EAS build profile docs: https://docs.expo.dev/build/eas-json/
