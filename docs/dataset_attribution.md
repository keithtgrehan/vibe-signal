# Dataset Attribution Register

This document is metadata-only. It does not grant permission to download, train on, redistribute, embed, or benchmark raw third-party rows.

## Internal Synthetic Vibe Fixtures

- Status: allowed for synthetic-only tests and research scaffolds.
- Attribution: Vibe Signal synthetic fixtures.
- Required caveat: synthetic regression coverage is not real-world validation or model-quality proof.

## GoEmotions

- Status: research/benchmark candidate metadata only.
- Source: Google Research, "GoEmotions: A Dataset of Fine-Grained Emotions."
- Public description: 58k English Reddit comments labeled with 27 emotion categories or neutral.
- Required caveat: no raw Reddit comments may be committed; any future benchmark use needs dataset-specific rights, privacy, and attribution review.

## TweetEval Sentiment

- Status: research/benchmark candidate metadata only.
- Source: CardiffNLP TweetEval.
- Public description: unified tweet-classification benchmark; this registry entry is sentiment-only.
- Required caveat: no tweet text, IDs, or exports may be committed; non-sentiment subsets require separate review.

## DailyDialog

- Status: non-commercial/research metadata only.
- Required caveat: commercial training and product model training are blocked.

## Blocked Candidates

- `dair-ai/emotion`: blocked pending license/provenance/privacy review.
- `EmpatheticDialogues`: blocked pending license/provenance/privacy review.
- Sensitive safety, neurodivergent, accessibility, transcript, audio, video, and multimodal candidates: blocked pending consent, privacy, harm, and rights review.
