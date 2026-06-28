#!/usr/bin/env node
/**
 * Verifly raw HTTP example — single verify with built-in `fetch` (Node 18+).
 *
 * No SDK, no dependencies. Just a Bearer token and the verify endpoint.
 *
 * Setup:
 *   export VERIFLY_API_KEY=vf_...        # get one free at https://verifly.email
 * Run:
 *   node raw_api.js
 */
const BASE = "https://verifly.email";
const API_KEY = process.env.VERIFLY_API_KEY;

if (!API_KEY) {
  console.error(
    "Set VERIFLY_API_KEY first. Get a free key (100 credits, no card) with:\n" +
      "  curl -X POST https://verifly.email/api/v1/autonomous/register \\\n" +
      "    -H 'Content-Type: application/json' \\\n" +
      "    -d '{\"email\":\"you@example.com\",\"password\":\"a-strong-password\"}'"
  );
  process.exit(1);
}

async function verify(email) {
  const url = `${BASE}/api/v1/verify?email=${encodeURIComponent(email)}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${API_KEY}` },
  });
  if (!res.ok) throw new Error(`Verifly API ${res.status}: ${await res.text()}`);
  return res.json();
}

async function main() {
  for (const email of ["founder@stripe.com", "test@gmial.com", "noreply@github.com"]) {
    const r = await verify(email);
    const hint = r.did_you_mean ? `  (did you mean ${r.did_you_mean}?)` : "";
    console.log(
      `${email.padEnd(26)} -> ${r.result.padEnd(14)} ${r.recommendation}${hint}`
    );
  }
  // Real output observed against the live API:
  //   founder@stripe.com         -> risky          risky
  //   test@gmial.com             -> undeliverable  do_not_send  (did you mean test@gmail.com?)
  //   noreply@github.com         -> undeliverable  do_not_send
}

main().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
