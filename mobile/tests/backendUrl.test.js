import assert from "node:assert/strict";
import test from "node:test";

import { formatBackendUrlStatus, parseBackendBaseUrl } from "../src/services/backendUrl.js";

test("parseBackendBaseUrl accepts clean http and https origins", () => {
  assert.deepEqual(parseBackendBaseUrl("https://vibe-signal.onrender.com/"), {
    ok: true,
    status: "api_url_ready",
    apiUrl: "https://vibe-signal.onrender.com",
    host: "vibe-signal.onrender.com",
  });

  assert.equal(parseBackendBaseUrl("http://127.0.0.1:8000").apiUrl, "http://127.0.0.1:8000");
});

test("parseBackendBaseUrl rejects non-base or credential-bearing URLs", () => {
  const invalidInputs = [
    "ftp://example.test",
    "https://example.test/api",
    "https://example.test?token=secret",
    "https://example.test#secret",
    "https://user:pass@example.test",
  ];

  for (const value of invalidInputs) {
    const result = parseBackendBaseUrl(value);
    assert.equal(result.ok, false);
    assert.equal(result.status, "invalid_api_url");
    assert.equal(result.apiUrl, "");
  }
});

test("formatBackendUrlStatus never echoes raw invalid URL input", () => {
  const status = formatBackendUrlStatus("https://user:pass@example.test/api?token=secret");

  assert.equal(status, "Configured backend URL must be a clean http(s) base URL.");
  assert.equal(status.includes("user"), false);
  assert.equal(status.includes("pass"), false);
  assert.equal(status.includes("token"), false);
});
