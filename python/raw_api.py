#!/usr/bin/env python3
"""
Verifly raw HTTP example — single + bulk verification with nothing but `requests`.

No SDK, no framework. This is the lowest common denominator: a Bearer token and
two HTTP calls. Read it to understand exactly what every other example does
under the hood.

Setup:
    pip install requests
    export VERIFLY_API_KEY=vf_...        # get one free at https://verifly.email
Run:
    python raw_api.py
"""
import os
import sys
import time

import requests

BASE = "https://verifly.email"
API_KEY = os.environ.get("VERIFLY_API_KEY")

if not API_KEY:
    sys.exit(
        "Set VERIFLY_API_KEY first. Get a free key (100 credits, no card) with:\n"
        "  curl -X POST https://verifly.email/api/v1/autonomous/register \\\n"
        "    -H 'Content-Type: application/json' \\\n"
        "    -d '{\"email\":\"you@example.com\",\"password\":\"a-strong-password\"}'"
    )

HEADERS = {"Authorization": f"Bearer {API_KEY}"}


def verify_one(email: str) -> dict:
    """Verify a single address in real time (1 credit)."""
    r = requests.get(
        f"{BASE}/api/v1/verify",
        params={"email": email},
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def verify_bulk(emails: list[str]) -> dict:
    """Submit a list as an async job, then fetch the per-address results."""
    submit = requests.post(
        f"{BASE}/api/v1/verify/bulk",
        json={"emails": emails},
        headers=HEADERS,
        timeout=60,
    )
    submit.raise_for_status()
    job = submit.json()
    job_id = job["job_id"]

    # Small lists finish instantly; poll for larger ones.
    while job.get("status") not in ("completed", "failed"):
        time.sleep(1)
        status = requests.get(f"{BASE}/api/v1/jobs/{job_id}", headers=HEADERS, timeout=30)
        status.raise_for_status()
        job = status.json()

    results = requests.get(
        f"{BASE}/api/v1/jobs/{job_id}/results", headers=HEADERS, timeout=30
    )
    results.raise_for_status()
    return results.json()


if __name__ == "__main__":
    # --- Single verify --------------------------------------------------
    res = verify_one("founder@stripe.com")
    print("SINGLE VERIFY")
    print(f"  email          : {res['email']}")
    print(f"  result         : {res['result']}")        # deliverable | undeliverable | risky | unknown
    print(f"  reason         : {res['reason']}")
    print(f"  confidence     : {res['confidence']}")
    print(f"  recommendation : {res['recommendation']}")  # safe_to_send | do_not_send | risky
    if res.get("did_you_mean"):
        print(f"  did_you_mean   : {res['did_you_mean']}")

    # Real output observed against the live API:
    #   result         : risky
    #   reason         : Catch-all server - cannot confirm individual address
    #   recommendation : risky

    # A typo gets caught and corrected:
    typo = verify_one("test@gmial.com")
    print(f"\n  typo check     : {typo['email']} -> {typo['result']} "
          f"(did_you_mean: {typo['did_you_mean']})")
    # -> test@gmial.com -> undeliverable (did_you_mean: test@gmail.com)

    # --- Bulk verify ----------------------------------------------------
    print("\nBULK VERIFY")
    bulk = verify_bulk(
        ["james@sibscientific.com", "fake@gmial.com", "noreply@github.com"]
    )
    print(f"  summary        : {bulk['summary']}")
    for row in bulk["results"]:
        print(f"  {row['result']:>14}  {row['email']}")
    # Real output:
    #   summary        : {'valid': 1, 'invalid': 2, 'risky': 0}
    #      deliverable  james@sibscientific.com
    #    undeliverable  fake@gmial.com
    #    undeliverable  noreply@github.com
