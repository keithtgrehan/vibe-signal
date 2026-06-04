# WhatsApp Dynamics Research Agent Findings

This research note defines a privacy-safe prototype scope for local WhatsApp conversation dynamics analysis. It uses GoEmotions, VAD/PAD, and THUNLP Model_Emotion only as conceptual references for taxonomy coverage, prompt/evaluation structure, and documentation ideas. It does not copy code, vendor datasets, download models, or make production claims from those methods.

Sources reviewed:

- GoEmotions paper: https://arxiv.org/abs/2005.00547
- GoEmotions catalog: https://tensorflow.google.cn/datasets/catalog/goemotions
- THUNLP Model_Emotion: https://github.com/thunlp/Model_Emotion
- Mehrabian and Russell PAD article: https://journals.sagepub.com/doi/10.2466/pms.1974.38.1.283
- Speech emotion recognition survey reference: https://www.sciencedirect.com/science/article/pii/S0031320310004619

## Agent 1 - Emotion Taxonomy Researcher

### Safe Emotion Taxonomy

Use a two-layer taxonomy:

- Internal research tags only: GoEmotions-like 27 categories plus neutral, VAD dimensions, and per-label prompt/evaluation ideas.
- User-facing output only: observable cue families such as directness, specificity, hedging, urgency, reassurance, pressure, conflict, alignment, ambiguity, cognitive load, topic shift, repair opportunity, and boundary pressure.

GoEmotions is useful for coverage because it defines 27 fine-grained text categories plus neutral across a large Reddit-comment dataset. That does not make those labels a truth source for private WhatsApp exchanges.

VAD/PAD should be used as coarse research framing only:

- Valence: positive or negative wording tone.
- Arousal: activation in wording, punctuation, urgency, repetition, or intensity markers.
- Dominance: control or constraint language, reframed in product output as pressure wording or choice-limiting wording.

THUNLP Model_Emotion is conceptually useful for per-category task separation, prompt/evaluation structure, and analysis documentation. This prototype should borrow only the idea of structured category evaluation and ablation-style safety checks.

### Blocked Labels

Do not expose labels or scores for hidden intent, motive, sincerity, deception, guilt, attraction, affection, commitment, relationship compatibility, attachment style, neurotype, diagnosis, trauma state, coercive personality, abuse verdict, cheating, rejection outcome, or what someone really means.

Avoid person-level labels such as angry person, avoidant, anxious, manipulative, lying, interested, cold, unsafe, or emotionally unavailable.

### Allowed Wording

Use these framing patterns:

- possible emotional signal
- observable wording patterns
- evidence-backed cue
- low-confidence signal
- requires human interpretation
- communication pressure
- timing ambiguity
- repair opportunity
- response imbalance

Safe examples:

- "Possible emotional signal: this message contains urgency wording."
- "Observable wording patterns: repeated punctuation and a direct request."
- "Evidence-backed cue: pressure-reducing wording appears in the exchange."
- "Low-confidence signal: the context is short and requires human interpretation."

### Mapping From GoEmotions-Like Labels To Observable Communication Cues

| GoEmotions-like label | Safe observable cue mapping |
| --- | --- |
| admiration | Praise wording, positive evaluation, appreciation phrase. |
| amusement | Laughter tokens, playful markers, joking wording; low-confidence signal. |
| anger | Conflict-related wording, intense punctuation, direct disagreement; never infer felt anger. |
| annoyance | Complaint wording, repeated friction markers, dismissive phrasing; requires human interpretation. |
| approval | Agreement wording, yes wording, plan acceptance. |
| caring | Supportive offer, check-in, reassurance wording; do not infer care or affection. |
| confusion | Clarification request, uncertainty marker, "I do not understand" wording. |
| curiosity | Question asking, information-seeking wording. |
| desire | Preference or want wording; never infer attraction. |
| disappointment | Unmet-expectation wording; low-confidence signal. |
| disapproval | Negative evaluation or disagreement wording. |
| disgust | Strong negative reaction wording; avoid moral or person verdict. |
| embarrassment | Self-conscious wording, apology, or self-correction; requires human interpretation. |
| excitement | Exclamation, positive anticipation, high-activation wording; do not infer true emotion. |
| fear | Concern or risk wording; never diagnose anxiety. |
| gratitude | Thanks or appreciation wording. |
| grief | Loss or sadness wording; sensitive support cue, not diagnosis. |
| joy | Positive affect wording, celebration markers, emoji-like markers; low-confidence signal. |
| love | Affection words only as text spans; never infer attraction or commitment. |
| nervousness | Uncertainty or concern wording; never infer anxiety disorder or neurotype. |
| optimism | Future-positive wording and expectation markers. |
| pride | Accomplishment wording or achievement mention. |
| realization | New-understanding wording such as "I see" or "got it." |
| relief | Pressure-reduction wording; requires human interpretation. |
| remorse | Apology or repair wording; do not infer remorse as an inner state. |
| sadness | Low-valence wording; sensitive, low-confidence signal. |
| surprise | Unexpectedness wording or punctuation. |
| neutral | No strong cue; short or context-light text may be insufficient evidence. |

### License/Source Review Notes

GoEmotions and THUNLP Model_Emotion should remain source-reviewed research references. Any direct code use would require a separate license/source review note before implementation. This prototype should use original rules, original docs, and synthetic fixtures only.

## Agent 2 - Conversation Dynamics Researcher

### Metrics List

- Response latency: time from one role's message to the next message by the other role.
- Median response latency by role.
- Response latency distribution by role with p10, p25, median, p75, p90, max.
- Same-day response rate.
- Fast response rate using a configured threshold.
- Message volume asymmetry.
- Word-count asymmetry.
- Average message length by role.
- Turn-taking balance.
- Consecutive-message run lengths.
- Unanswered ask candidates.
- Unanswered ask candidate rate by role.
- Direct ask rate.
- Unclear timing rate.
- Chronological cue shifts by day and week.

### Formulas

Let messages be sorted by timestamp and use `self` / `other` role labels only.

- `message_count[role] = count(messages where role == role)`
- `total_words[role] = sum(word_count(message.text) for role)`
- `average_words[role] = total_words[role] / max(1, message_count[role])`
- `message_asymmetry = (message_count.self - message_count.other) / max(1, total_messages)`
- `word_asymmetry = (total_words.self - total_words.other) / max(1, total_words.self + total_words.other)`
- A response event occurs when adjacent sorted messages have different roles.
- `latency_seconds = current.timestamp - previous.timestamp`
- `median_latency[responder] = median(latencies where responder == role)`
- `unanswered_ask_candidate = ask-like message with no opposite-role reply within the configured response window`
- `direct_ask_rate = direct_ask_count / max(1, message_count)`
- `unclear_timing_rate = unclear_timing_count / max(1, message_count)`
- `chronological_shift = metric[current_window] - metric[previous_window]`

### Minimum Viable Report Structure

- Date range analyzed.
- Total messages analyzed.
- Role-only breakdown using `self` and `other`.
- Response timing metrics.
- Participation metrics.
- Turn-taking metrics.
- Ask follow-up metrics.
- Chronological cue shift table.
- Safety note: aggregate role-level metrics only, no raw messages, no names, no inferred hidden states, no score.

### Limitations

Latency can reflect sleep, work, travel, time zones, device access, notification settings, in-person follow-up, or calls. Word counts and message counts do not measure care, sincerity, attention, or emotional state. Ask detection can miss indirect requests or overcount rhetorical questions. Chronological shifts show changes in observable patterns, not causes.

## Agent 3 - Multimodal Safety Researcher

### Audio Schema

Expected CSV columns for this prototype:

- `audio_id`
- `message_id`
- `speaker_role`
- `timestamp`
- `pitch_mean`
- `pitch_std`
- `energy_mean`
- `voice_break_rate`
- `pause_rate`
- `wav2vec_cluster`
- `valence_proxy`
- `arousal_proxy`
- `dominance_proxy`

### Safe Interpretation Rules

Pitch, energy, pauses, voice breaks, and embedding clusters cannot prove emotion, intent, deception, affection, anger, stress, or mental state. These features are affected by microphone quality, background noise, illness, fatigue, accents, speaking style, device distance, and context.

Use safe language:

- "text and audio features point in different directions"
- "audio dynamics shifted compared with the local aggregate baseline"
- "the system detected a pacing or energy change, not a confirmed emotion"

### Blocked Claims

Do not say:

- "They are hiding anger."
- "They are lying."
- "They are secretly upset."
- "They are manipulating you."
- "Their voice proves their real feelings."
- "The audio reveals their intent."
- "The model detected suppressed emotion."

### Confidence Rules

Use low confidence by default for audio-only interpretation. Increase confidence only for narrow observations such as higher energy than local aggregate baseline or longer pauses than usual. Never assign high confidence to emotion, intent, deception, or hidden-state claims. If text and audio differ, report feature divergence only.

## Agent 4 - Implementation Planner

### Implementation Plan

Build a local-only CLI pipeline:

1. Analyze restricted redacted WhatsApp JSONL from `data/restricted/private_whatsapp`.
2. Write aggregate-only markdown and JSON reports under `data/restricted/private_whatsapp/reports`.
3. Optionally validate and aggregate an audio matrix by `message_id`.
4. Export synthetic, private-inspired fixtures under `data/synthetic/private_inspired`.
5. Optionally train a weak-label/synthetic sklearn baseline locally only, writing an aggregate report under `reports/engine_eval`.
6. Keep all production frontend/backend/mobile runtime paths untouched.

### Files To Create

- `tools/analyze_whatsapp_dynamics.py`
- `tools/export_synthetic_dynamics_fixtures.py`
- `tools/train_private_dynamics_baseline.py`
- `tests/test_whatsapp_dynamics_research_safety.py`
- `docs/research/whatsapp_dynamics_research/final_thesis.md`
- `docs/research/whatsapp_dynamics_research/action_endpoint_design.md`
- `docs/proof/closed_beta/whatsapp_dynamics_research_prototype.md`
- `data/synthetic/private_inspired/dynamics_fixtures.jsonl` if the synthetic export passes safety checks.

### Files Not To Touch

- `backend/**`
- `web/**`
- `mobile/**`
- provider integration files
- production endpoint files
- deployment config
- `data/restricted/private_whatsapp/raw/**`
- `data/restricted/private_whatsapp/processed/**`
- `data/restricted/private_whatsapp/reports/**` for committed artifacts
- `data/restricted/private_whatsapp/models/**` for committed artifacts

### Validation Commands

```bash
python -m py_compile tools/analyze_whatsapp_dynamics.py tools/export_synthetic_dynamics_fixtures.py tools/train_private_dynamics_baseline.py
python -m pytest tests/test_whatsapp_dynamics_research_safety.py -q
python -m pytest tests/test_private_whatsapp_ingestion_safety.py -q
python scripts/check_no_raw_content_leaks.py
python scripts/check_public_copy_safety.py
python scripts/check_vibe_restricted_artifacts.py --staged
git diff --check
```

### Acceptance Criteria

- Private input is read only from `data/restricted/private_whatsapp`.
- Private-derived outputs default only to `data/restricted/private_whatsapp/reports`.
- Non-restricted private output requires `--allow-synthetic-output`.
- Synthetic fixtures contain no copied private phrases longer than three words.
- No raw private text is printed.
- No names are printed.
- Reports use `self` / `other` only.
- Audio is represented as bounded feature divergence only.
- No backend, frontend, mobile, provider, analytics, auth, payment, or production endpoint change is introduced.
