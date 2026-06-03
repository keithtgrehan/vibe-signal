# PR #19 RC Merge-Readiness Review

Date: 2026-06-03.

Status: `PARTIAL_PASS_WITH_EXTERNAL_BLOCKERS`.

This review was run from `origin/main` after PR #19 merged. It is metadata-only and contains no raw chats, tester messages, screenshots, secrets, request bodies, response bodies, raw external datasets, embeddings, vectors, checkpoints, or model files.

## Findings Fixed

- Public-copy risk: public/tester surfaces had a few broad blocked words in legal/disclaimer copy. Those were rewritten to safer health/identity-label language while preserving the product boundary.
- Privacy risk: feedback metadata previously included a hash of optional free-text feedback. The stored metadata now omits that hash so feedback storage remains metadata-only.
- Regression cost: the red-line output blocker reloaded static YAML policy files on every validation call. Static policy loading is now cached in memory only.
- Fixture gap: the synthetic WhatsApp regression loop now generates exactly 1,000 synthetic messages and writes both fixture and unsafe-output reports.
- False-positive gap: tests now cover risky inference prompts, low-signal fallback, urgency vs pressure, contradiction vs deception language, reassurance vs identity labels, and evidence-field completeness.

## Non-Blocking Notes

- Public-copy scanner findings are allowlisted only for internal safety, tests, research, proof, or source-register files.
- The synthetic regression report is not real-world accuracy, model-quality proof, legal approval, or production readiness.
- The `cheating_ambiguous` synthetic category is private regression metadata only. It must never become consumer-facing product copy or a product capability claim.

## Remaining Merge Risks

- Full validation must pass on the branch before merge.
- Real-device iPhone/TestFlight QA has not been run.
- Legal/privacy review has not been completed.
- Tester invites remain blocked until those external gates pass.
