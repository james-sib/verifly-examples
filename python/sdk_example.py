#!/usr/bin/env python3
"""
Verifly Python SDK example — the `verifly-email` package on PyPI.

The SDK wraps the same REST API as raw_api.py but handles auth, retries,
and JSON for you. Use this in normal application code.

Setup:
    pip install verifly-email
    export VERIFLY_API_KEY=vf_...        # get one free at https://verifly.email
Run:
    python sdk_example.py

Docs: https://pypi.org/project/verifly-email/
"""
import os
import sys

from verifly_email import VeriflyClient, VeriflyError

API_KEY = os.environ.get("VERIFLY_API_KEY")
if not API_KEY:
    sys.exit("Set VERIFLY_API_KEY first (free key at https://verifly.email).")

client = VeriflyClient(api_key=API_KEY)


def gate_signup(email: str) -> bool:
    """Return True only if it is safe to create an account for this address."""
    res = client.verify(email)
    return res["recommendation"] == "safe_to_send"


if __name__ == "__main__":
    try:
        # --- Single verify ----------------------------------------------
        res = client.verify("founder@stripe.com")
        print(f"single : {res['email']} -> {res['result']} "
              f"({res['reason']}, confidence {res['confidence']})")

        # --- Batch verify (synchronous, good for a few hundred) ---------
        batch = client.verify_batch(
            ["james@sibscientific.com", "fake@gmial.com", "noreply@github.com"]
        )
        print(f"batch  : {batch['valid_count']} valid / "
              f"{batch['invalid_count']} invalid of {batch['total']}")
        for row in batch["results"]:
            print(f"         {row['result']:>14}  {row['email']}")

        # --- Use it as a signup gate ------------------------------------
        for candidate in ("james@sibscientific.com", "asdf@nonexistent-xyz123.com"):
            ok = gate_signup(candidate)
            print(f"signup : {candidate} -> {'ACCEPT' if ok else 'REJECT'}")

        # --- Credits left -----------------------------------------------
        print(f"credits: {client.credits()['credits']} remaining")

    except VeriflyError as e:
        sys.exit(f"Verifly API error: {e}")

    # Real output observed against the live API:
    #   single : founder@stripe.com -> risky (Catch-all server - cannot confirm individual address, confidence 40)
    #   batch  : 1 valid / 2 invalid of 3
    #   signup : james@sibscientific.com -> ACCEPT
    #   signup : asdf@nonexistent-xyz123.com -> REJECT
