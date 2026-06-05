# Agent 3 - NLP Modeling Approaches

Date: 2026-06-05

Status: research_plan_requires_gpt_user_review. No training code or model artifact is approved by this document.

## Recommended Stack

The safe stack is layered:

1. deterministic cue engine remains production default;
2. weak supervision compares rule outputs against local human labels;
3. classical local multi-label classifier prototypes cue detection;
4. embedding or SetFit prototypes only after label volume and evaluation gates improve;
5. transformer fine-tuning only after enough labels and source rights exist.

## Deterministic Rules Plus Cue Taxonomy

Strengths:

- transparent;
- evidence-span friendly;
- easy to block unsafe interpretations;
- deterministic regression tests are stable;
- no external training data required;
- easy to keep private data out of CI.

Weaknesses:

- brittle phrasing coverage;
- false positives from short context;
- poor semantic generalization;
- hard to rank uncertain examples without human review.

Use now:

- keep as product path;
- add aggregate local eval later;
- use rule disagreement to select rows for review.

## Weak Supervision

Useful sources:

- Snorkel weak-supervision paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC7075849/
- Snorkel arXiv: https://arxiv.org/abs/1711.10160

Recommended use:

- convert deterministic cues into labeling functions;
- add label functions for low-signal, hard negatives, and blocked outputs;
- compare weak labels to human-reviewed rows;
- never promote weak labels to gold without review.

Output should be aggregate metrics:

- coverage;
- overlap;
- conflict;
- per-cue precision against local gold;
- top confusion pairs.

## Classical Baselines

Start with:

- `TfidfVectorizer` word n-grams and character n-grams;
- deterministic cue counts and boolean features;
- one-vs-rest logistic regression;
- calibrated thresholds;
- abstain if below threshold or evidence is missing.

Consider later:

- LinearSVC with calibrated decision scores;
- random forest only for feature importance experiments, not first path;
- XGBoost only if dependency and explainability cost are justified.

Relevant docs:

- scikit-learn text feature extraction: https://scikit-learn.org/stable/modules/feature_extraction.html
- scikit-learn calibration: https://scikit-learn.org/stable/modules/calibration.html

Why logistic regression first:

- works with small sparse text features;
- easy to inspect top features;
- easier to calibrate and threshold;
- low dependency cost;
- lower overfitting risk than a transformer on small labels.

## Sentence Embeddings

Useful source:

- Sentence Transformers docs: https://huggingface.co/docs/hub/en/sentence-transformers
- Sentence-BERT paper: https://arxiv.org/abs/1908.10084

Use cases:

- nearest-neighbor retrieval for synthetic fixture similarity;
- cluster review rows by cue confusion;
- find duplicate or near-duplicate synthetic cases;
- candidate active-learning selection.

Risks:

- embedding spaces can blur safety boundaries;
- nearest examples must not be shown if they come from private rows;
- vector artifacts derived from private rows must stay local-only and ignored.

Recommendation:

- use embeddings first for local analysis and sampling, not product prediction.

## SetFit

Useful source:

- SetFit docs: https://huggingface.co/docs/setfit/en/index
- SetFit paper: https://arxiv.org/abs/2209.11055

Fit:

- promising for few-shot prototypes;
- useful after the label schema stabilizes;
- supports multi-label workflows, but still needs careful thresholding and evaluation.

Do not use until:

- each target cue has enough reviewed positives and hard negatives;
- embeddings/model artifacts remain local-only;
- the output renderer can enforce evidence and cannot-infer boundaries.

## Transformer Fine-Tuning

Candidates later:

- DistilBERT;
- MiniLM;
- DeBERTa-small;
- RoBERTa-base.

Useful docs:

- Hugging Face text classification: https://huggingface.co/docs/transformers/tasks/sequence_classification

Do not train now:

- 30 rows is not enough;
- private labels cannot leave the local machine;
- source rights for public datasets are not approved;
- transformer outputs are harder to explain and calibrate;
- a fine-tuned model could overfit private wording patterns.

Minimum before considering:

- 2,000-5,000 reviewed rows or legally approved training corpus;
- 200+ positives per important cue;
- frozen held-out local gold set;
- blocked-output rate at zero on red-team suite;
- abstention and evidence-span gates working.

## Calibration, Abstention, And Low-Signal Detection

Model outputs should not be treated as truth probabilities. They need:

- per-cue thresholds;
- calibration curves;
- reliability diagrams;
- low-signal label;
- explicit abstention when evidence is weak;
- refusal to infer intent, attraction, truthfulness, diagnosis, or outcomes.

Calibration source:

- scikit-learn `CalibratedClassifierCV`: https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html

## Active Learning

Sampling queues:

- high model uncertainty;
- deterministic/model disagreement;
- cue conflicts;
- rare cue coverage;
- low-signal edge cases;
- safe-output red-team failures;
- reviewer-rejected rows.

Useful source:

- modAL uncertainty sampling docs: https://modal-python.readthedocs.io/en/latest/content/query_strategies/uncertainty_sampling.html

Use row IDs and aggregate summaries only. Do not put raw private text in n8n, GitHub issues, PRs, or reports.

## ONNX And Deployment

Relevant source:

- ONNX Runtime docs: https://onnxruntime.ai/docs/

Do not export models for product yet. If a local baseline later passes gates, prefer:

- local artifact under ignored restricted model area;
- model card in repo without artifact;
- checksum/provenance metadata without private source labels;
- no web bundle model until legal/privacy review approves it.

## Model Card Outline

Future model card should include:

- model purpose;
- training data categories, not raw examples;
- excluded data;
- private data handling;
- source registry version;
- label schema version;
- evaluation splits;
- cue metrics;
- abstention behavior;
- safe-output tests;
- blocked capabilities;
- known failure modes;
- deployment restrictions;
- review approvals.

