function isNonEmptyString(value) {
  return String(value || "").trim().length > 0;
}

function isFiniteNumber(value) {
  return Number.isFinite(Number(value));
}

function isBoolean(value) {
  return typeof value === "boolean";
}

export function validateEventPayload(eventType, payload = {}) {
  const errors = [];
  const normalizedType = String(eventType || "").trim();

  if (!["analysis", "quota", "billing", "state"].includes(normalizedType)) {
    errors.push("unsupported_event_type");
  }

  if (!isNonEmptyString(payload.event_id)) {
    errors.push("missing_event_id");
  }
  if (!isNonEmptyString(payload.user_id)) {
    errors.push("missing_user_id");
  }
  if (!isFiniteNumber(payload.client_timestamp)) {
    errors.push("invalid_client_timestamp");
  }
  if (!isFiniteNumber(payload.sequence_number) || Number(payload.sequence_number) < 1) {
    errors.push("invalid_sequence_number");
  }
  if (!isNonEmptyString(payload.session_id)) {
    errors.push("missing_session_id");
  }
  if (!isNonEmptyString(payload.platform)) {
    errors.push("missing_platform");
  }

  if (normalizedType === "analysis") {
    if (!isBoolean(payload.success)) {
      errors.push("invalid_analysis_success");
    }
    if (!isNonEmptyString(payload.mode)) {
      errors.push("missing_analysis_mode");
    }
  }

  if (normalizedType === "quota") {
    if (!isNonEmptyString(payload.type)) {
      errors.push("missing_quota_type");
    }
    if (!isFiniteNumber(payload.remaining_after) || Number(payload.remaining_after) < -1) {
      errors.push("invalid_remaining_after");
    }
  }

  if (normalizedType === "billing") {
    if (!isNonEmptyString(payload.type)) {
      errors.push("missing_billing_type");
    }
    if (!isNonEmptyString(payload.status)) {
      errors.push("missing_billing_status");
    }
  }

  if (normalizedType === "state") {
    if (!isBoolean(payload.premium_active)) {
      errors.push("invalid_premium_active");
    }
    if (!isFiniteNumber(payload.remaining_uses) || Number(payload.remaining_uses) < -1) {
      errors.push("invalid_remaining_uses");
    }
    if (!isBoolean(payload.paywall_required)) {
      errors.push("invalid_paywall_required");
    }
  }

  return {
    ok: errors.length === 0,
    status: errors.length === 0 ? "payload_valid" : "invalid_event_payload",
    errors,
  };
}
