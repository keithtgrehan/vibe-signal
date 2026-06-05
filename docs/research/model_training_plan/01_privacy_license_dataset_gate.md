# Agent 1 - Privacy, GDPR, DPA, And Licensing Gate

Date: 2026-06-05

Status: research_plan_requires_gpt_user_review. This is not legal advice or approval to train.

## Operating Rule

Vibe Signal should treat every data source as blocked until a registry row proves otherwise. Public availability does not mean product-training permission, ethical suitability, privacy safety, or commercial suitability.

Private WhatsApp/gold-review rows remain local-only. They may be used only from ignored local paths under `data/restricted/private_whatsapp/**`, and future scripts must output aggregate metrics or redacted reports only.

## Legal Grounding

Useful official references:

- GDPR Article 5 defines processing principles such as purpose limitation, data minimization, accuracy, storage limitation, integrity/confidentiality, and accountability: https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
- GDPR Article 6 lists lawful bases for processing, including consent and processing requested by the data subject: https://eur-lex.europa.eu/eli/reg/2016/679/art_6/oj/eng
- GDPR Article 9 restricts special-category personal data, including health, sex life, sexual orientation, biometric, religious, political, and similar categories: https://eur-lex.europa.eu/eli/reg/2016/679/art_9/oj/eng
- GDPR Article 13 requires clear information where personal data are collected from the data subject: https://eur-lex.europa.eu/eli/reg/2016/679/art_13/oj/eng
- GDPR Article 14 may apply where personal data are not collected directly from the data subject: https://eur-lex.europa.eu/eli/reg/2016/679/art_14/oj/eng
- GDPR Article 28 governs processor arrangements: https://eur-lex.europa.eu/eli/reg/2016/679/art_28/oj/eng
- GDPR Article 30 records-of-processing, Article 32 security, Article 35 DPIA, and Article 44 international-transfer gates should be reviewed before provider, n8n, cloud, or external dataset use: https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng

Research implication: training/evaluation plans should distinguish user-requested transient analysis from model development, dataset retention, provider transfer, and publication. Those are different processing contexts and need separate review.

Provider, n8n, cloud, or external processing cannot be approved by license review alone. It also needs DPA/subprocessor review, transfer-mechanism review where relevant, retention/delete commitments, security controls, and a purpose-specific privacy review.

## Private Gold Labels

Allowed now:

- local-only label QA;
- aggregate cue-level metrics;
- aggregate deterministic-vs-human disagreement analysis;
- local active-learning sampling by row ID or neutral ID;
- redacted reports that do not expose source identifiers, row text, filenames, or private examples.

Blocked:

- raw row text in git, GitHub, CI, docs, PRs, screenshots, Vercel, Render, n8n, issue text, or logs;
- private workbook/export/model/report artifacts in git;
- private source metadata in public config or docs;
- provider upload unless future rights/legal review explicitly approves it;
- training model artifacts committed to the repo;
- model-quality claims based on private rows.

## Dataset License Classification

Classification values:

- `commercial-training-allowed`: license and terms appear compatible with the intended commercial/product training use, subject to privacy and harm review.
- `research-only`: use is limited to academic/non-commercial research or unclear enough that product use is blocked.
- `benchmark-only`: can inform evaluation design or offline benchmark comparison, but not product training by default.
- `blocked`: do not use for Vibe Signal training/evaluation.
- `requires-legal-review`: insufficient clarity, sensitive domain, provenance complexity, or terms conflict.

## Initial License Matrix

| Source | Primary source | Stated license/status | Vibe classification | Rationale |
| --- | --- | --- | --- | --- |
| Vibe synthetic fixtures | repo-authored | Vibe-owned synthetic | commercial-training-allowed after product review | Safe immediate path, but synthetic performance is not real-world accuracy. |
| Private gold labels | local-only private source pending documented lawful-basis and purpose-specific rights review | not public | requires-legal-review for training, allowed local QA only now | Private rows stay local-only and support aggregate evaluator design. |
| GoEmotions | https://github.com/google-research/google-research/tree/master/goemotions | Google Research repo states datasets under CC BY 4.0; dataset is Reddit comments with emotion labels | benchmark candidate, not-approved metadata-only | Useful taxonomy reference; emotion labels are not internal truth and Reddit/profiling risks require review. |
| Civil Comments | https://www.tensorflow.org/datasets/catalog/civil_comments | TFDS says CC0 | safety benchmark candidate, not-approved metadata-only | Toxicity labels and identity fields create protected-trait and harm-review concerns. |
| Wikipedia Detox | https://meta.wikimedia.org/wiki/Research:Detox/Data_Release | CC0 public domain dedication | safety benchmark candidate, not-approved metadata-only | Useful for unsafe-language checks, not relationship cue training. |
| Stanford Politeness API/corpus | https://github.com/sudhof/politeness | code Apache-2.0; corpus terms need source review | requires-legal-review | Useful request/politeness concepts; do not train on rows without corpus rights review. |
| Switchboard Dialog Act Corpus | https://convokit.cornell.edu/documentation/switchboard.html | CC BY-NC-SA 3.0 | research-only | Non-commercial/share-alike; useful for dialogue-act concepts, not product training. |
| DailyDialog | https://parl.ai/docs/tasks.html | research/non-commercial signals from common distributions | research-only | Dialogue acts useful, but non-commercial status blocks product training. |
| EmpatheticDialogues | https://parl.ai/docs/tasks.html | CC BY-NC | research-only | Support phrasing reference only; not commercial/product training. |
| TweetEval | https://github.com/cardiffnlp/tweeteval | repo says task/Twitter restrictions may apply | benchmark-only | Tweet terms and task-specific licenses need review. |
| Taskmaster | https://github.com/google-research-datasets/Taskmaster | Google dataset repo; license observed separately from use approval and needs per-release review | requires-legal-review | Task-oriented data may help repair/error patterns, but must be registry-reviewed. |
| ProsocialDialog | https://github.com/skywalker023/prosocial-dialog | official repo; license observed separately from use approval and needs direct file review | requires-legal-review | Safety dialogue data can be useful, but content and social-norm labels need harm review. |
| ReDial | https://redialdata.github.io/website/ | CC BY 4.0 | benchmark-only or requires-legal-review | Dialogue structure reference; recommendation domain is weak fit. |
| Negotiation/persuasion datasets | various papers/repos | varies | requires-legal-review or blocked | Risk of coercive optimization. Use only for red-team/harm review unless explicit safe use is approved. |
| Mental-health/support forum datasets | varies | often unclear/sensitive | blocked | Therapy-adjacent and health-risk data conflict with product boundaries. |
| Raw Reddit/forum dumps | varies | often unclear/TOS-bound | blocked or requires-legal-review | Privacy, provenance, and platform terms risks. |

## Fail-Closed Registry Fields

Future dataset registry rows should include:

- `source_id`: neutral ID only.
- `source_name`.
- `source_url`.
- `license_id`.
- `license_url`.
- `terms_url`.
- `retrieved_at`.
- `source_snapshot_hash`.
- `source_owner`.
- `data_type`.
- `contains_personal_data`.
- `contains_special_category_risk`.
- `contains_sensitive_context`.
- `data_subject_notice_basis`.
- `commercial_training_allowed`.
- `product_training_allowed`.
- `benchmark_allowed`.
- `synthetic_derivatives_allowed`.
- `raw_commit_allowed`.
- `redacted_commit_allowed`.
- `provider_upload_allowed`.
- `ci_allowed`.
- `dpa_required`.
- `processor_name`.
- `subprocessors`.
- `transfer_mechanism`.
- `ropa_entry_required`.
- `dpia_required`.
- `storage_root`.
- `artifact_policy`.
- `attribution_required`.
- `retention_rule`.
- `approval_expires_at`.
- `approved_by_role`.
- `legal_review_status`.
- `privacy_review_status`.
- `harm_review_status`.
- `allowed_uses`.
- `blocked_uses`.
- `output_claim_limits`.

Default for missing or unclear fields: blocked.

Validator behavior should reject:

- unknown enum values;
- stale or expired approvals;
- non-primary license or terms URLs when primary sources are available;
- contradictory booleans, such as product training allowed while commercial training is blocked for a commercial use;
- `allowed_uses` that exceed license, terms, privacy, DPA, transfer, or harm-review approvals;
- provider, n8n, or cloud use without DPA/subprocessor, transfer, retention/delete, and security/privacy review fields.

## Gate Decision

Training can proceed only after:

- registry row is complete;
- legal/privacy/harm review status is approved for the specific use;
- no raw private data path is read outside local execution;
- no raw row text reaches CI, PRs, docs, n8n, providers, or public app surfaces;
- output is constrained to observable wording cues and safe next steps.
