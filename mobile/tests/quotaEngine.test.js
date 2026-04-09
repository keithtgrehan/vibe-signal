import test from "node:test";
import assert from "node:assert/strict";

import {
  buildQuotaViewModel,
  createInitialCommerceState,
  recordCompletedAnalysisForQuota,
  resolveQuotaState,
} from "../src/commerce/quotaEngine.js";

test("trial week starts with 10 free uses", () => {
  const now = new Date("2026-04-08T10:00:00.000Z");
  const initial = createInitialCommerceState(now);
  const resolved = resolveQuotaState(initial, { now, premiumActive: false });

  assert.equal(resolved.snapshot.current_period_type, "trial_week");
  assert.equal(resolved.snapshot.allowed_uses_in_current_period, 10);
  assert.equal(resolved.snapshot.remaining_uses, 10);
  assert.equal(resolved.snapshot.paywall_required, false);
});

test("post-trial weekly quota resets to 5 uses on the next 7-day cycle", () => {
  const firstOpen = "2026-04-01T10:00:00.000Z";
  const exhaustedTrial = {
    first_opened_at: firstOpen,
    current_period_start: firstOpen,
    current_period_type: "trial_week",
    uses_in_current_period: 10,
    completed_analysis_ids: ["a1"],
    cached_premium_state: {},
  };

  const resolved = resolveQuotaState(exhaustedTrial, {
    now: new Date("2026-04-09T10:00:01.000Z"),
    premiumActive: false,
  });

  assert.equal(resolved.snapshot.current_period_type, "weekly_free");
  assert.equal(resolved.snapshot.allowed_uses_in_current_period, 5);
  assert.equal(resolved.snapshot.uses_in_current_period, 0);
  assert.equal(resolved.snapshot.remaining_uses, 5);
});

test("premium access bypasses quota exhaustion", () => {
  const exhaustedState = {
    ...createInitialCommerceState(new Date("2026-04-08T10:00:00.000Z")),
    uses_in_current_period: 10,
  };

  const resolved = resolveQuotaState(exhaustedState, {
    now: new Date("2026-04-08T10:00:01.000Z"),
    premiumActive: true,
  });

  assert.equal(resolved.snapshot.premium_active, true);
  assert.equal(resolved.snapshot.paywall_required, false);
  assert.equal(resolved.snapshot.remaining_uses, Number.POSITIVE_INFINITY);
});

test("successful analysis decrements usage once and failures are caller-controlled", () => {
  const initial = createInitialCommerceState(new Date("2026-04-08T10:00:00.000Z"));
  const recorded = recordCompletedAnalysisForQuota(initial, {
    analysisId: "analysis_1",
    now: new Date("2026-04-08T11:00:00.000Z"),
    premiumActive: false,
  });

  assert.equal(recorded.ok, true);
  assert.equal(recorded.recorded, true);
  assert.equal(recorded.snapshot.remaining_uses, 9);

  const duplicate = recordCompletedAnalysisForQuota(recorded.state, {
    analysisId: "analysis_1",
    now: new Date("2026-04-08T11:05:00.000Z"),
    premiumActive: false,
  });
  assert.equal(duplicate.recorded, false);
  assert.equal(duplicate.snapshot.remaining_uses, 9);
});

test("quota view model exposes paywall flags and reset timing", () => {
  const snapshot = {
    current_period_end: "2026-04-15T10:00:00.000Z",
    current_period_type: "weekly_free",
    remaining_uses: 0,
    paywall_required: true,
    premium_active: false,
  };
  const viewModel = buildQuotaViewModel(snapshot, new Date("2026-04-08T10:00:00.000Z"));

  assert.equal(viewModel.periodLabel, "Weekly free usage");
  assert.equal(viewModel.paywallVisible, true);
  assert.match(viewModel.resetTiming, /Resets in/i);
});

test("premium quota view model derives renewal timing from entitlement expiry", () => {
  const snapshot = {
    current_period_end: "2026-04-15T10:00:00.000Z",
    current_period_type: "weekly_free",
    remaining_uses: Number.POSITIVE_INFINITY,
    paywall_required: false,
    premium_active: true,
  };
  const viewModel = buildQuotaViewModel(
    snapshot,
    new Date("2026-04-08T10:00:00.000Z"),
    {
      expiresAt: "2026-05-08T10:00:00.000Z",
    }
  );

  assert.match(viewModel.resetTiming, /Renews around/i);
  assert.equal(viewModel.resetAt, "2026-05-08T10:00:00.000Z");
});
