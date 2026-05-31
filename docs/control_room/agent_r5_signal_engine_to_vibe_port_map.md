# Agent R5 - Signal Engine to Vibe Engine Port Map

## Scope decision

Port now: provenance, rights registry validation, restricted artifact scanning, evidence object discipline, human review packets, gold-label validation shape, claims gating, and evaluation readiness gates.

Adapt later: retrieval over evidence objects, local ranking helpers, observability utilities, and safe IO/report helpers after deterministic outputs and review workflows are stable.

Leave behind: acquisition, corpus-building, finance extraction, model training, embedding stores, provider-backed reviewer execution, and source-domain scoring.

## Target namespace and output posture

Target package namespace is `vibesignal_ai`. Vibe Engine outputs must stay deterministic-first, local-first, evidence-backed, and communication-pattern-only. Evidence objects support review and optional local retrieval, but they do not override deterministic local outputs and they do not establish truth about emotion, intent, diagnosis, identity, attraction, or relationship outcomes.

## Exact files to port/adapt

| Source file in earnings-call-signal-engine | Target file in vibe-signal | Action | Reason | Required renames | Finance leakage to remove | Tests to add/adapt |
| --- | --- | --- | --- | --- | --- | --- |
| `scripts/resource_registry_common.py` | `scripts/validate_vibe_resource_registry.py` | adapt | Strong rights-tier, provenance, alias, and fail-closed validation pattern. | `signal_engine` to `vibesignal_ai`; source rows to conversation/data resources. | ticker, exchange, transcript vendor, SEC/FRED/IR source logic. | registry valid/invalid, duplicate IDs, malformed booleans, restricted raw/commit/use. |
| `scripts/check_restricted_artifacts.py` | `scripts/check_vibe_restricted_artifacts.py` | adapt | Blocks restricted raw artifacts before commit. | restricted transcript/audio/video to private chat, platform export, provider output, screenshot, audio, video. | webcast, paywall transcript, finance vendor paths. | staged mode and explicit path list tests. |
| `src/signal_engine/retrieval/objects.py` | `src/vibesignal_ai/evidence/objects.py` | adapt | Provenance-backed objects with deterministic override and raw text rights checks. | `case_id` to `conversation_id`; `retrieval_object` to `evidence_object`; `signal_type` to `cue_id`. | ticker, company, fiscal period, event chunks. | evidence required fields, unsafe fields, rights/commit guardrails, JSONL round trip. |
| `src/signal_engine/retrieval/export.py` | `src/vibesignal_ai/evidence/export.py` | adapt | Simple JSONL serialization and validation before write. | retrieval rows to evidence rows. | retrieval priority tied to finance chunks. | invalid evidence refuses write. |
| `scripts/validate_gold_labels.py` | `scripts/validate_vibe_gold_labels.py` | adapt | JSONL-only, reviewer-owned gold label validation. | `signal_family` to `label_type`; evidence terms to evidence spans. | finance label families and event-specific labels. | enum, duplicate label ID, unsafe fields, non-neutral evidence requirements. |
| `scripts/build_label_review_packet.py` | `scripts/build_vibe_review_packet.py` | adapt | Review packet with reviewer columns and non-mutating workflow. | source label packet to cue/evidence packet. | finance labels and source-case text. | Markdown/CSV generation, invalid evidence refusal. |
| `configs/claims_matrix.example.yml` | `configs/claims_matrix.example.yml` | adapt | Product-claim control and launch review gates. | finance claims to communication-pattern claims. | predictive market or event claims. | claims matrix guardrail tests. |
| `src/signal_engine/training/readiness.py` | `scripts/evaluate_vibe_outputs.py` | adapt | Evaluation-gate pattern without model training. | gold count gates to reviewed-label gates. | production model quality claims, retrieval lift claims based on finance tasks. | low-count gate, unsupported claim, provider canonical blocker. |
| Corpus/data-rights policy docs | `docs/data_rights_and_consent_policy.md` and `docs/research/vibe_dataset_benchmark_radar.md` | adapt | Rights, consent, benchmark-only posture. | corpus to conversation set or fixture set. | acquisition, source discovery, transcript vendor language. | validator and residue tests. |
| schema helper style | `schemas/vibe_*.schema.json` | reference only | Keep schema discipline without copying domain fields. | signal schema names to Vibe schema names. | case/entity/event fields. | schema presence and validator tests. |
| observability and safe IO utilities | existing utility modules | reference only | Useful engineering shape, not required for this PR. | none now. | domain report payloads. | later only. |

## Rights registry/resource validator/restricted artifact checker

The registry validator should fail closed on unknown rights, malformed booleans, missing provenance, duplicate IDs, restricted raw-body access, restricted commit access, and restricted training/evaluation use. Alias support may be accepted for migration convenience, but canonical Vibe rows must retain explicit Vibe field names.

The restricted artifact checker should block raw private conversations, platform exports, provider raw outputs, screenshots, audio, video, transcripts, and downloads unless they are under approved docs/config/schema/synthetic-fixture paths.

## Claims matrix

The claims matrix should permit only bounded communication-pattern claims such as directness, specificity, hedging, overload, pressure wording, boundary wording, consent clarity, and repair opportunity. It must block claims about deception, hidden intent, true emotion, diagnosis, protected traits, attraction, relationship outcomes, workplace or education outcomes, biometric analysis, manipulation scoring, production model quality, and statistical significance unless a future gated evaluation explicitly allows a narrow non-product statement.

## Evidence/retrieval objects

Vibe evidence objects replace Signal Engine retrieval objects. Every displayed cue should be traceable to an evidence object with `conversation_id`, message or turn identifiers, offsets when available, evidence text hash, provenance, and interpretation limits. Evidence objects cannot override deterministic outputs and cannot make raw restricted text commit-safe.

## Gold label validator and promotion guardrails

Gold labels remain human-reviewed communication-pattern labels with evidence spans. Weak labels, provider rows, external dataset rows, review packet suggestions, and synthetic exploratory rows cannot become product gold automatically. Any promotion path should remain dry-run by default until a separate reviewed workflow exists.

## Review packet workflow

Review packets may present evidence-backed cue candidates to reviewers. The reviewer decides whether to accept, reject, or relabel. Packet copy must state that machine cues are suggestions, accepted labels need evidence spans, and labels are for communication-pattern review only.

## Evaluation loop

Use a gate scaffold, not a model benchmark. Below 50 reviewed labels, make no benchmark or ML claims. Below 100 reviewed labels, make no retrieval-quality claims. Below 500 reviewed labels, make no model-quality claims. Any unsafe claim fails the gate. Provider outputs are never canonical.

## Corpus policy docs

Replace corpus acquisition posture with local, consented conversation-set and synthetic fixture posture. External research datasets are metadata-only benchmark or calibration references by default. No external dataset rows become Vibe gold labels automatically.

## Tests to adapt/create

- Registry validation for valid rows, duplicate IDs, bad booleans, restricted raw/commit/use, and provenance placeholders.
- Restricted artifact blocking for risky raw paths and safe prefixes.
- Evidence object validation for required fields, unsafe fields, interpretation limits, rights restrictions, and JSONL round trip.
- Gold label validation for enums, required fields, duplicate IDs, evidence spans, and unsafe fields.
- Review packet generation and invalid evidence refusal.
- Claims matrix validation and unsupported-claim blocking.
- Evaluation gate behavior for label-count thresholds and unsafe/provider-canonical blockers.
- Red-line output blocker tests for prohibited claims and allowed neutral comparison language.
- No-source-domain-residue tests for ported files.

## What to rename

- `signal_engine` -> `vibesignal_ai`
- `case_id` -> `conversation_id`
- `transcript` -> `conversation_segment` or `message_thread`
- `signal_type` -> `pattern_label` or `cue_id`
- `retrieval_object` -> `evidence_object`
- `corpus` -> `conversation_set` or `fixture_set`
- `evidence_span` -> `message_span`

## What to delete due to source-domain leakage

Delete or avoid: ticker, trading, alpha, buy/sell, buy signal, sell signal, earnings call, revenue, EPS, margin, guidance revision, analyst pressure, market signal, investor relations, SEC EDGAR, FRED, IR provider logic, finance acquisition jobs, finance corpus manifests, event windows, source-domain scoring, training candidates, vector or embedding implementation, and provider-backed reviewer execution.

## Acceptance criteria

- No finance/ticker/trading residue in new Vibe product files outside this explicit deletion map and residue tests.
- No raw user data committed.
- No external dataset downloads.
- No model training code.
- No provider calls during validation.
- Every displayed cue can be backed by an evidence object.
- Red-line blocker catches emotion/intent/deception/diagnosis/attraction/protected-trait and coercive claims.
- Review workflow stays reviewer-owned.
- Tests and validators pass.

## Minimal safe PR plan

1. Start from latest `origin/main`, which already includes Phases 1-7.
2. Add this R5 control-room document and canonical R2 dataset radar.
3. Expand metadata-only research-source config and validators.
4. Materialize synthetic fixture packs and fixture schema tests.
5. Add deterministic red-line blocker and cue taxonomy if safe.
6. Add claims matrix and evaluation gate scaffolds.
7. Add source-domain residue tests.
8. Run full Python validation, staged artifact checks, residue greps, and mobile tests only if dependencies already exist.
9. Push a draft PR for review.

## Final cutline

Vibe Engine should inherit guardrail, evidence, review, provenance, and evaluation-control scaffolding only. It should not inherit source-domain acquisition, finance extraction, training, provider review execution, or broad affect/intent logic.
