"""Safe explanations for Vibe matching results."""

from __future__ import annotations

from typing import Any

from ..safety.redline_output_blocker import check_output_text


DEFAULT_SAFE_SUMMARY = "This match result describes observable communication patterns only."
LOW_SIGNAL_SAFE_SUMMARY = (
    "There is not enough evidence-backed wording to estimate a communication pattern band."
)
LOW_SIGNAL_EXPLANATION = (
    "The visible text is too short, one-sided, or sparse for a normal result. No action is required; "
    "add more permissioned context only if you want a broader wording-pattern review."
)


REPAIR_SUGGESTIONS = {
    "ambiguity": "Ask for the missing detail in one sentence, without adding pressure.",
    "unclear_ask": "Restate the ask with one concrete next step.",
    "answer_evasion_pattern": "If clarity matters, ask the original question again with room to pause or decline.",
    "specificity_drop": "Ask for the missing time, plan, or constraint instead of guessing.",
    "contradiction_against_prior_message": "Confirm which plan is current without accusing the other person.",
    "unsupported_claim_shift": "Use a concrete example or pause before escalating the exchange.",
    "pressure": "Try a lower-pressure version that makes no response an acceptable option.",
    "boundary_pressure": "Pause and restate the boundary-respecting option before continuing.",
    "escalation_risk": "Pause before replying and, if needed, use calmer repair language.",
    "overloaded_message": "Split the message into one ask and one context sentence.",
    "cognitive_load": "Reduce the message to the single next action you want to clarify.",
    "repair_opportunity": "Use the repair opening to restate intent and reduce pressure.",
    "reassurance": "Treat reassurance as visible wording only; ask for clarity if needed.",
    "directness": "Keep the direct ask while leaving room for a no or later.",
    "specificity": "Keep concrete details visible so the ask is easier to answer.",
    "consent_clarity": "Keep the opt-out or consent check explicit.",
}


def repair_suggestion_for(cue_family: str) -> str:
    return REPAIR_SUGGESTIONS.get(
        str(cue_family or "").strip(),
        "Use a short clarification that respects boundaries and leaves room to pause.",
    )


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
    result_state: str = "ready",
    signal_strength: str = "medium",
    override: str | None = None,
) -> tuple[str, str, str]:
    if result_state == "low_signal":
        raw_summary = override or LOW_SIGNAL_SAFE_SUMMARY
    else:
        raw_summary = override or (
            "This result describes observable communication-pattern compatibility with "
            f"a {band} communication pattern band and {signal_strength} signal strength."
        )
    redline = check_output_text(raw_summary)
    if redline["status"] == "block":
        return DEFAULT_SAFE_SUMMARY, "block", "Unsafe summary wording was replaced with neutral communication-pattern language."

    if result_state == "low_signal":
        return raw_summary, "allow", LOW_SIGNAL_EXPLANATION

    safe_explanation = (
        "Communication fit is based on visible cues such as directness, specificity, "
        "urgency, pressure wording, repair wording, consent clarity, boundary respect, "
        "and answer alignment."
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
                "cue_id": str(row.get("cue_id", row.get("cue_family", ""))),
                "cue_family": str(row.get("cue_family", "")),
                "evidence_text": str(row.get("evidence_text", "")),
                "span_start": int(row.get("span_start", row.get("start_offset", 0)) or 0),
                "span_end": int(row.get("span_end", row.get("end_offset", 0)) or 0),
                "safe_phrase": str(row.get("safe_phrase", "")),
                "explanation": str(row.get("explanation", "")),
                "confidence": float(row.get("confidence", 0.5) or 0.5),
                "signal_strength": "medium" if float(row.get("confidence", 0.5) or 0.5) >= 0.55 else "low",
                "interpretation_limits": dict(row.get("interpretation_limits") or {
                    "does_not_infer_true_emotion": True,
                    "does_not_detect_deception": True,
                    "does_not_score_personality": True,
                }),
                "repair_suggestion": repair_suggestion_for(str(row.get("cue_family", ""))),
            }
        )
    return compacted
