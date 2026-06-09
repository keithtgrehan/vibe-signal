# App Store Metadata Risk Review - 2026-06-09

Status: Pending owner/App Store metadata review.

Known blocker:

- `mobile/app.json` does not have `ios.bundleIdentifier`. Do not invent this value. Owner must provide the final bundle identifier before EAS TestFlight submission.

Required review items:

- App name, subtitle, description, keywords:
- Screenshots use synthetic messages only:
- Privacy policy URL:
- Terms URL:
- Support URL:
- Data request/delete URL:
- App Privacy Details data inventory:
- TestFlight beta description:
- Features to test:
- Export compliance answers in App Store Connect:
- Account deletion path, if accounts are enabled:
- Subscription/IAP metadata, if purchase flow is in beta:

Blocked claims:

- GDPR or EU AI Act compliance
- Accuracy, validation, trained model, or production-grade model claims
- Emotion detection, compatibility prediction, hidden intent, attraction prediction, deception certainty, diagnosis, neurotype inference, or manipulation advice

Use this as a checklist only; it is not legal approval.
