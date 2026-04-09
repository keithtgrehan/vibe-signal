import test from "node:test";
import assert from "node:assert/strict";

import { getLoggingConfig } from "../src/services/loggingConfig.js";

function restoreEnv(name, value) {
  if (typeof value === "undefined") {
    delete process.env[name];
    return;
  }
  process.env[name] = value;
}

test("logging config disables safely when no API URL is configured", () => {
  const originalEnable = process.env.EXPO_PUBLIC_ENABLE_LOGGING;
  const originalApi = process.env.EXPO_PUBLIC_API_URL;
  const originalVersion = process.env.EXPO_PUBLIC_APP_VERSION;

  process.env.EXPO_PUBLIC_ENABLE_LOGGING = "true";
  process.env.EXPO_PUBLIC_API_URL = "";
  process.env.EXPO_PUBLIC_APP_VERSION = "1.0.0";

  const config = getLoggingConfig();

  assert.equal(config.enabled, true);
  assert.equal(config.apiUrl, "");
  assert.equal(config.ready, false);
  assert.deepEqual(config.warnings, ["logging_enabled_without_api_url"]);

  restoreEnv("EXPO_PUBLIC_ENABLE_LOGGING", originalEnable);
  restoreEnv("EXPO_PUBLIC_API_URL", originalApi);
  restoreEnv("EXPO_PUBLIC_APP_VERSION", originalVersion);
});

test("logging config accepts a valid HTTPS API URL", () => {
  const originalEnable = process.env.EXPO_PUBLIC_ENABLE_LOGGING;
  const originalApi = process.env.EXPO_PUBLIC_API_URL;

  process.env.EXPO_PUBLIC_ENABLE_LOGGING = "1";
  process.env.EXPO_PUBLIC_API_URL = "https://api.example.test/";

  const config = getLoggingConfig();

  assert.equal(config.enabled, true);
  assert.equal(config.apiUrl, "https://api.example.test");
  assert.equal(config.ready, true);
  assert.deepEqual(config.warnings, []);

  restoreEnv("EXPO_PUBLIC_ENABLE_LOGGING", originalEnable);
  restoreEnv("EXPO_PUBLIC_API_URL", originalApi);
});
