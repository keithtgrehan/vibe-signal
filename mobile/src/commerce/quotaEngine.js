import {
  TRIAL_PERIOD_DAYS,
  TRIAL_WEEK_FREE_USES,
  WEEKLY_PERIOD_DAYS,
  WEEKLY_FREE_USES,
} from "./config.js";

const DAY_MS = 24 * 60 * 60 * 1000;
const TRIAL_PERIOD_MS = TRIAL_PERIOD_DAYS * DAY_MS;
const WEEKLY_PERIOD_MS = WEEKLY_PERIOD_DAYS * DAY_MS;
const MAX_CONSUMED_ANALYSIS_IDS = 50;

function toDate(value, fallback = new Date()) {
  const text = String(value || "").trim();
  if (!text) {
    return fallback;
  }
  const parsed = new Date(text);
  return Number.isNaN(parsed.getTime()) ? fallback : parsed;
}

function toIso(date) {
  return new Date(date).toISOString();
}

function normalizeAnalysisIds(value) {
  return Array.isArray(value)
    ? value.map((item) => String(item || "").trim()).filter(Boolean).slice(-MAX_CONSUMED_ANALYSIS_IDS)
    : [];
}

function buildDefaultPremiumCache() {
  return {
    premium_active: false,
    entitlement_status: "inactive",
    source: "",
    product_id: "",
    entitlement_id: "",
    expires_at: "",
    last_synced_at: "",
    cache_state: "empty",
  };
}

export function createInitialCommerceState(now = new Date()) {
  const start = toDate(now);
  return {
    first_opened_at: toIso(start),
    current_period_start: toIso(start),
    current_period_type: "trial_week",
    uses_in_current_period: 0,
    completed_analysis_ids: [],
    cached_premium_state: buildDefaultPremiumCache(),
  };
}

function resolvePeriod(firstOpenedAt, now) {
  const firstOpen = toDate(firstOpenedAt, now);
  const diff = now.getTime() - firstOpen.getTime();
  if (diff < TRIAL_PERIOD_MS) {
    return {
      current_period_start: toIso(firstOpen),
      current_period_end: toIso(firstOpen.getTime() + TRIAL_PERIOD_MS),
      current_period_type: "trial_week",
      allowed_uses: TRIAL_WEEK_FREE_USES,
    };
  }

  const weeklyStartBase = firstOpen.getTime() + TRIAL_PERIOD_MS;
  const weeklyOffset = Math.floor((now.getTime() - weeklyStartBase) / WEEKLY_PERIOD_MS);
  const currentPeriodStartMs = weeklyStartBase + weeklyOffset * WEEKLY_PERIOD_MS;
  return {
    current_period_start: toIso(currentPeriodStartMs),
    current_period_end: toIso(currentPeriodStartMs + WEEKLY_PERIOD_MS),
    current_period_type: "weekly_free",
    allowed_uses: WEEKLY_FREE_USES,
  };
}

export function resolveQuotaState(rawState = {}, { now = new Date(), premiumActive = false } = {}) {
  const baseState = {
    ...createInitialCommerceState(now),
    ...(rawState || {}),
    cached_premium_state: {
      ...buildDefaultPremiumCache(),
      ...(rawState?.cached_premium_state || {}),
    },
  };

  const firstOpenedAt = toDate(baseState.first_opened_at, now);
  const period = resolvePeriod(firstOpenedAt, now);
  const isSamePeriod =
    String(baseState.current_period_start || "") === period.current_period_start &&
    String(baseState.current_period_type || "") === period.current_period_type;

  const usesInCurrentPeriod = isSamePeriod
    ? Math.max(0, Number(baseState.uses_in_current_period || 0))
    : 0;
  const completedAnalysisIds = isSamePeriod
    ? normalizeAnalysisIds(baseState.completed_analysis_ids)
    : [];

  const remainingUses = premiumActive
    ? Number.POSITIVE_INFINITY
    : Math.max(0, period.allowed_uses - usesInCurrentPeriod);

  const nextState = {
    ...baseState,
    first_opened_at: toIso(firstOpenedAt),
    current_period_start: period.current_period_start,
    current_period_type: period.current_period_type,
    uses_in_current_period: usesInCurrentPeriod,
    completed_analysis_ids: completedAnalysisIds,
  };

  const snapshot = {
    first_opened_at: nextState.first_opened_at,
    current_period_start: nextState.current_period_start,
    current_period_end: period.current_period_end,
    current_period_type: nextState.current_period_type,
    uses_in_current_period: nextState.uses_in_current_period,
    allowed_uses_in_current_period: premiumActive ? null : period.allowed_uses,
    remaining_uses: remainingUses,
    paywall_required: !premiumActive && remainingUses === 0,
    premium_active: Boolean(premiumActive),
  };

  return {
    state: nextState,
    snapshot,
  };
}

export function recordCompletedAnalysisForQuota(
  rawState = {},
  { analysisId = "", now = new Date(), premiumActive = false } = {}
) {
  const normalizedAnalysisId = String(analysisId || "").trim();
  const resolved = resolveQuotaState(rawState, { now, premiumActive });

  if (premiumActive) {
    return {
      ok: true,
      recorded: false,
      status: "premium_unlimited",
      state: resolved.state,
      snapshot: resolved.snapshot,
    };
  }

  if (resolved.snapshot.paywall_required) {
    return {
      ok: false,
      recorded: false,
      status: "paywall_required",
      blocked_reason: "free_limit_reached",
      state: resolved.state,
      snapshot: resolved.snapshot,
    };
  }

  if (normalizedAnalysisId && resolved.state.completed_analysis_ids.includes(normalizedAnalysisId)) {
    return {
      ok: true,
      recorded: false,
      status: "analysis_already_recorded",
      state: resolved.state,
      snapshot: resolved.snapshot,
    };
  }

  const nextState = {
    ...resolved.state,
    uses_in_current_period: resolved.state.uses_in_current_period + 1,
    completed_analysis_ids: normalizedAnalysisId
      ? [...resolved.state.completed_analysis_ids, normalizedAnalysisId].slice(-MAX_CONSUMED_ANALYSIS_IDS)
      : [...resolved.state.completed_analysis_ids],
  };
  const nextResolved = resolveQuotaState(nextState, { now, premiumActive });
  return {
    ok: true,
    recorded: true,
    status: "analysis_recorded",
    state: nextResolved.state,
    snapshot: nextResolved.snapshot,
  };
}

function formatDuration(now, resetAt) {
  const deltaMs = Math.max(0, resetAt.getTime() - now.getTime());
  const totalHours = Math.ceil(deltaMs / (60 * 60 * 1000));
  if (totalHours <= 24) {
    return `${totalHours}h`;
  }
  const totalDays = Math.ceil(totalHours / 24);
  return `${totalDays}d`;
}

function formatCalendarDate(date) {
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
  }).format(date);
}

export function buildQuotaViewModel(snapshot = {}, now = new Date(), premiumState = {}) {
  const premiumResetAt = String(premiumState?.expiresAt || "").trim();
  const resetAt = toDate(
    snapshot.premium_active && premiumResetAt ? premiumResetAt : snapshot.current_period_end || now,
    now
  );
  return {
    usesLeft:
      snapshot.premium_active
        ? "Unlimited"
        : `${Math.max(0, Number(snapshot.remaining_uses || 0))} left`,
    periodLabel: snapshot.current_period_type === "trial_week" ? "Trial week" : "Weekly free usage",
    resetTiming: snapshot.premium_active
      ? premiumResetAt
        ? `Renews around ${formatCalendarDate(resetAt)}`
        : "Premium active"
      : `Resets in ${formatDuration(now, resetAt)}`,
    paywallVisible: Boolean(snapshot.paywall_required),
    premiumActive: Boolean(snapshot.premium_active),
    resetAt: snapshot.premium_active && premiumResetAt ? premiumResetAt : snapshot.current_period_end || "",
  };
}
