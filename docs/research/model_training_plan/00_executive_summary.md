# Vibe Signal NLP Training Plan - Executive Summary

Date: 2026-06-05

Status: research_plan_requires_gpt_user_review. This is not legal advice, not compliance approval, and not approval to train or deploy a model.

## Bottom Line

Do not train a production model from the current private gold set. Approximately 30 human-reviewed rows are useful for label QA, evaluator design, deterministic cue calibration, and active-learning planning, but they are too small and too privacy-sensitive to support a production model.

The strongest safe path is:

1. keep the deterministic cue engine as the production default;
2. build a local-only gold evaluator around the reviewed rows;
3. expand synthetic fixtures and hard negatives;
4. use weak supervision to compare deterministic labels against human labels;
5. train the first local-only baseline only after enough reviewed rows exist;
6. add embedding or transformer models only after legal, privacy, safety, and evaluation gates pass.

No private rows, private workbooks, private exports, private model artifacts, or external dataset rows should be committed, uploaded, bundled, served, or routed through n8n.

## Agent Outputs

- Agent 1, privacy/license gatekeeper: fail-closed source registry, private gold local-only rules, dataset license matrix.
- Agent 2, public dataset scout: candidate datasets classified for planning, with external sources kept as not-approved metadata-only until source-specific registry approval.
- Agent 3, NLP modeling researcher: deterministic plus weak supervision first; classical local baseline before embeddings; transformer fine-tuning later only if justified.
- Agent 4, label taxonomy designer: multi-label cue schema with evidence spans, severity, safe next step, reject, low-signal, reviewer confidence, and unsafe-output flags.
- Agent 5, evaluation architect: evaluation gates before training and before product integration.
- Agent 6, synthetic data researcher: synthetic fixture expansion, counterfactuals, hard negatives, and red-team sets.
- Agent 7, tooling researcher: lightweight local stack, ignored artifact roots, pytest gates, and no dependency bloat for this sprint.
- Agent 8, product safety researcher: safe model output contract, abstention, evidence-first UI mapping, and blocked output registry.
- Agent 9, n8n ops researcher: metadata-only operational workflows; no raw private content or private source metadata.

## Can We Train Now With 30 Rows?

No for production, and not even as a product-affecting beta feature.

Safe uses now:

- review label schema quality;
- check reviewer consistency;
- smoke-test evaluator code locally later;
- compare deterministic cue outputs against human-reviewed labels using aggregate metrics;
- identify high-confusion cue pairs;
- design active-learning sampling;
- calibrate weak-label rules without exporting private rows.

Blocked now:

- production model training;
- fine-tuning transformer models on private rows;
- provider upload of private rows;
- CI runs over private rows;
- committing model artifacts derived from private rows;
- reporting row-level examples in docs or PRs.

## Recommended First Model Path

Do not start with a transformer. The first trainable model should be a local-only, interpretable baseline:

- TF-IDF word/character features;
- deterministic cue outputs as structured features;
- multi-label one-vs-rest logistic regression first;
- LinearSVC only if probability calibration is handled separately;
- explicit abstention thresholds;
- per-cue evidence requirement supplied by deterministic span selection, not by a free-form model.

The baseline should never produce final user-facing copy directly. It may only suggest cue candidates to a safe renderer that enforces evidence, cannot-infer language, and safe next steps.

## Label Counts Before Training

Minimum thresholds before any local-only baseline training:

- Schema/evaluator smoke: 50-100 reviewed rows, still not product-affecting.
- Weak-label calibration: 250-400 reviewed rows with enough cue coverage and hard negatives.
- First classical baseline: 600-1,000 reviewed rows for broad cue-family prediction, with at least 80-100 positive examples for each primary cue family and at least 200 low-signal or negative examples.
- Embedding/SetFit prototype: 40-80 positives per cue for an offline prototype, but 150+ positives per important cue before product consideration.
- Transformer fine-tune: 2,000-5,000 reviewed rows or a legally approved external training source, plus 200+ positives per important cue and stable holdout performance.

These numbers are planning gates, not claims that performance will be sufficient.

## Dataset Classification Summary

Commercial-training-allowed after source-specific review:

- Vibe-owned synthetic fixtures.
- Some permissively licensed public safety or dialogue datasets may be allowed for narrow benchmark or safety-classifier work, but each source needs a registry entry and legal/harm review before product training.

External benchmark candidates after registry approval:

- Civil Comments and Wikipedia Detox for toxicity/safety red-team design, currently metadata-only until approved.
- TweetEval because underlying Twitter/X constraints may apply, currently metadata-only until approved.
- GoEmotions as a taxonomy/reference candidate only; do not treat labels as internal state or product truth.

Research-only or non-commercial by default:

- DailyDialog.
- EmpatheticDialogues.
- Switchboard Dialog Act Corpus.
- Many ParlAI open-domain dialogue tasks.

Blocked or legal-review-required:

- private conversations without explicit rights;
- mental-health or therapy-adjacent support forums;
- survivor-report, harassment, workplace, education, or protected-trait datasets;
- raw Reddit/forum dumps without clear license, consent, and privacy review;
- persuasion or negotiation datasets for product behavior unless the output contract blocks coercive use.

## Legal And Privacy Gates

Before any training or benchmark use beyond metadata:

- source registry row exists and fails closed;
- license and terms are verified from primary source;
- allowed use is explicit for the intended purpose;
- sensitive-domain and protected-trait risks are documented;
- private rows stay local-only under `data/restricted/private_whatsapp/**`;
- no provider upload, no CI artifact, no n8n raw-content workflow;
- output report contains only aggregate metrics or redacted summaries;
- Keith/user reviews the plan before implementation.

## Implementation Sequence

1. Phase 0 - Legal/data-rights gate.
2. Phase 1 - Label schema plus local gold evaluator.
3. Phase 2 - Synthetic fixture expansion.
4. Phase 3 - Weak-label baseline.
5. Phase 4 - Classical local baseline.
6. Phase 5 - Embedding/SetFit prototype.
7. Phase 6 - Transformer fine-tune only if justified.
8. Phase 7 - Product integration behind feature flag.
9. Phase 8 - Monitoring/evaluation loop.

The detailed phase plan is in `10_recommended_implementation_sequence.md`.

## Sources Used

Key sources are linked in the detailed research files. Official or high-trust sources include EUR-Lex GDPR Articles 5, 6, 9, 13, 14, 28, 30, 32, 35, and 44; Google Research dataset documentation; TensorFlow Datasets; Wikimedia Detox release notes; ParlAI task documentation; ConvoKit; Hugging Face docs; scikit-learn docs; Snorkel paper; SetFit docs; ONNX Runtime docs; and project-local Vibe Signal guardrail docs.
