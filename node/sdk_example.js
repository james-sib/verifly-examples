#!/usr/bin/env node
/**
 * Verifly Node SDK example — the `verifly-email` package on npm.
 *
 * Handles auth, retries and JSON for you. Works in CommonJS and ESM.
 *
 * Setup:
 *   npm install verifly-email
 *   export VERIFLY_API_KEY=vf_...        # get one free at https://verifly.email
 * Run:
 *   node sdk_example.js
 *
 * Docs: https://www.npmjs.com/package/verifly-email
 */
const { VeriflyClient, VeriflyError } = require("verifly-email");

const API_KEY = process.env.VERIFLY_API_KEY;
if (!API_KEY) {
  console.error("Set VERIFLY_API_KEY first (free key at https://verifly.email).");
  process.exit(1);
}

// The API key is the first positional argument; options are second.
const client = new VeriflyClient(API_KEY);

async function main() {
  try {
    // --- Single verify ------------------------------------------------
    const r = await client.verify("founder@stripe.com");
    console.log(`single : ${r.email} -> ${r.result} (${r.reason})`);

    // --- Batch verify (synchronous, good for a few hundred) -----------
    const batch = await client.verifyBatch([
      "james@sibscientific.com",
      "fake@gmial.com",
      "noreply@github.com",
    ]);
    console.log(`batch  : ${batch.valid_count} valid / ${batch.invalid_count} invalid of ${batch.total}`);
    for (const row of batch.results) {
      console.log(`         ${row.result.padStart(14)}  ${row.email}`);
    }

    // --- Stop a fake signup in one line -------------------------------
    const candidate = "asdf@nonexistent-xyz123.com";
    const ok = (await client.verify(candidate)).recommendation === "safe_to_send";
    console.log(`signup : ${candidate} -> ${ok ? "ACCEPT" : "REJECT"}`);

    console.log(`credits: ${(await client.credits()).credits} remaining`);
  } catch (e) {
    if (e instanceof VeriflyError) {
      console.error("Verifly API error:", e.message);
      process.exit(1);
    }
    throw e;
  }

  // Real output observed against the live API:
  //   single : founder@stripe.com -> risky (Catch-all server - cannot confirm individual address)
  //   batch  : 1 valid / 2 invalid of 3
  //   signup : asdf@nonexistent-xyz123.com -> REJECT
}

main();
