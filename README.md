# vibe-signal
# VibeSignal AI

VibeSignal AI is a mobile-first AI analysis product with a Python analysis core and a commerce layer designed to support a freemium-to-subscription model.

The current build is structured to keep the trusted analysis and entitlement logic authoritative on the Python side, while the mobile app handles device identity, purchase initiation, and entitlement refresh. The product is being built cautiously: evidence-backed implementation first, no fake production claims, and clear separation between what is working now and what still depends on live store infrastructure. This follows the same “built now vs planned later” discipline used elsewhere in the project.  [oai_citation:0‡README.md](sediment://file_00000000ece4724686893e145ad84df2)  [oai_citation:1‡capstone-master.md](sediment://file_00000000b624724698d7d5d5e142f097)

## Current status

Implemented now:

- Expo-managed mobile shell
- Secure device installation identity using SecureStore
- Fail-closed behavior when secure storage is unavailable
- Anonymous device-scoped app-user registration
- Authoritative Python-side entitlement state and usage metering
- 10 free completed analyses per anonymous device
- Blocking after free usage unless subscription entitlement is confirmed
- Normalized Apple and Google purchase artifact shapes
- Python-side malformed purchase artifact rejection
- Hashed or minimized purchase-reference handling rather than raw token persistence

Still scaffold only:

- Real StoreKit transaction flow
- Real Google Play Billing flow
- Real Apple receipt verification
- Real Google purchase-token verification
- Real restore and sync against live store accounts
- End-to-end store proof on device/simulator
- Mobile JS test execution in an environment with Node/npm

## Architecture

### Mobile layer
The mobile app is responsible for:

- secure installation identity
- purchase initiation
- restore requests
- entitlement refresh requests
- fail-closed handling when required dependencies are missing

The mobile app is **not** the source of truth for entitlement.

### Python commerce layer
The Python side is authoritative for:

- anonymous user registration
- usage counting
- free-tier enforcement
- subscription status handling
- purchase artifact validation
- final entitlement decisions

This keeps the trusted logic server-side and avoids granting access based only on client-side purchase initiation. That separation is consistent with the broader project principle of keeping trusted core logic distinct from optional surrounding layers.  [oai_citation:2‡earnings_call_system_execution_roadmap.md](sediment://file_000000007e20720a972dcb2f782bc61e)

## Entitlement model

Current structured entitlement state includes:

- `usage_count`
- `free_remaining`
- `subscription_status`
- `entitlement_state`
- `blocked_reason`

Current blocked reasons include:

- `free_limit_reached`
- `subscription_inactive`
- `subscription_expired`
- `purchase_unverified`
- `provider_not_ready`
- `missing_consent`
- `secure_storage_unavailable`

Only successful completed analyses are counted toward usage.

## Repository structure

```text
mobile/
  src/commerce/
    deviceIdentity.js
    billingService.js
    entitlementClient.js
    appleStoreKitAdapter.js
    googlePlayBillingAdapter.js
  tests/

src/vibesignal_ai/commerce/
  __init__.py
  config.py
  models.py
  store.py
  service.py
  verification.py
  api.py
  analysis_runner.py

tests/
  test_commerce.py

docs/
  handoff_status.md
  privacy_data_flow.md
  provider_disclosure_notes.md


Development principles
	•	Python-side entitlement remains authoritative
	•	Mobile never grants entitlement on local purchase initiation alone
	•	Secure storage is mandatory for installation identity
	•	Missing critical dependencies must fail closed
	•	Do not claim live billing support before it exists
	•	Keep built vs planned clearly separated
	•	Prefer narrow, hard, testable steps over broad fake completeness

These principles match the existing repo stance of evidence first, minimal hype, and explicit separation between current build and future roadmap.  ￼  ￼

Testing

Python tests currently cover the commerce path, including entitlement handling and malformed purchase artifact rejection.

Example commands:

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/test_commerce.py

What comes next

The next real engineering milestone is not “more scaffolding.” It is one actual native purchase path wired end to end on a single platform.

Recommended next step:
	1.	run the mobile repo in an environment with Node, npm, and Expo tooling
	2.	wire one real store path first, preferably iOS or Android, not both at once
	3.	pass its purchase artifact into the existing Python verification surface
	4.	keep verification outcomes truthful until live vendor verification is implemented

Notes

This repo is private and intended for product development, iteration, and future commercialization. The current implementation is a hardened commerce and entitlement foundation, not a finished live subscription app.

