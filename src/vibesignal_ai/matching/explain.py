"""Safe explanations for Vibe matching results."""

from __future__ import annotations

from typing import Any

from ..safety.redline_output_blocker import check_output_text


DEFAULT_SAFE_SUMMARY = "This match result describes observable communication patterns only."


def build_factor_lists(score_parts: dict[str, float], cue_counts: dict[str, int]) -> tuple[list[str], list[str]]:
    alignment: list[str] = []
    friction: list[str] = []

    if score_parts.get("specificity", 0.0) > 0:
        alignment.append("Specificity and concrete timing cues are present.")
    if score_parts.get("alignment", 0.0) > 0:
        alignment.append("Messages include agreement or shared-plan wording.")
    if score_parts.get("low_pressure", 0.0) > 0:
        alignment.append("Low-pressure wording supports boundary-respecting communication.")
    if score_parts.get("repair", 0.0) > 0:
        alignment.append("Repair wording creates a clearer path to reset the exchange.")
    if score_parts.get("consent_clarity", 0.0) > 0:
        alignment.append("Consent or opt-out wording is visible in the exchange.")
    if score_parts.get("directness", 0.0) > 0:
        alignment.append("Direct request wording makes the ask easier to identify.")

    if cue_counts.get("pressure", 0):
        friction.append("Pressure wording may reduce communication fit.")
    if cue_counts.get("boundary_pressure", 0):
        friction.append("Boundary-pressure wording creates a communication-friction cue.")
    if cue_counts.get("overloaded_message", 0) or cue_counts.get("cognitive_load", 0):
        friction.append("Dense or multi-part messages may increase reading load.")
    if cue_counts.get("ambiguity", 0) or cue_counts.get("unclear_ask", 0):
        friction.append("Ambiguity cues make the ask or reply less stable to analyze.")
    if cue_counts.get("specificity_drop", 0):
        friction.append("A later reply has fewer concrete details than the earlier ask.")
    if cue_counts.get("answer_evasion_pattern", 0):
        friction.append("A reply does not directly answer a previous ask.")
    if cue_counts.get("contradiction_against_prior_message", 0):
        friction.append("A reply conflicts with an earlier stated availability or commitment.")
    if cue_counts.get("unsupported_claim_shift", 0):
        friction.append("A strong claim appears without concrete supporting detail.")

    if not alignment:
        alignment.append("No strong alignment factor is visible from the current text.")
    if not friction:
        friction.append("No major deterministic friction cue is visible from the current text.")
    return alignment[:5], friction[:5]


def build_summary(
    *,
    band: str,
    score: float,
    alignment: list[str],
    friction: list[str],
    override: str | None = None,
) -> tuple[str, str, str]:
    raw_summary = override or (
        "The match score reflects observable communication-pattern compatibility "
        f"with a {band} fit band and score {score:.2f}."
    )
    redline = check_output_text(raw_summary)
    if redline["status"] == "block":
        return DEFAULT_SAFE_SUMMARY, "block", "Unsafe summary wording was replaced with neutral communication-pattern language."

    safe_explanation = (
        "Compatibility is based on explicit cues such as directness, specificity, "
        "pressure, repair wording, consent clarity, boundary respect, and answer alignment."
    )
    if alignment and friction:
        safe_explanation += f" Stronger factor: {alignment[0]} Main friction: {friction[0]}"
    return raw_summary, "allow", safe_explanation


def compact_evidence(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compacted: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        evidence_id = str(row.get("evidence_id", ""))
        if not evidence_id or evidence_id in seen:
            continue
        seen.add(evidence_id)
        compacted.append(
            {
                "evidence_id": evidence_id,
                "message_id": str(row.get("message_id", "")),
                "cue_family": str(row.get("cue_family", "")),
                "evidence_text": str(row.get("evidence_text", "")),
                "safe_phrase": str(row.get("safe_phrase", "")),
                "confidence": float(row.get("confidence", 0.5) or 0.5),
            }
        )
    return compacted
