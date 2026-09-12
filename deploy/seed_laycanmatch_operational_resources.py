#!/usr/bin/env python3
"""Queue LaycanMatch operational resource pages and optionally release the first.

All output remains source-authoritative: Blog Core delegates each record to
content-factory-laycanmatch, which owns the native /resources/ renderer.
"""

import argparse
import json
import time
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen


SITE_ID = 8
FOLLOWING_FIRST_PUBLICATION = datetime(2026, 8, 22, 10, 0, tzinfo=timezone.utc)
CADENCE = timedelta(days=3)


def idea(title, slug, angle):
    return {
        "title": title,
        "targetPath": f"/resources/{slug}/",
        "contentType": "blog",
        "source": "approved_laycanmatch_operational_demand_research",
        "angle": angle,
    }


IDEAS = [
    idea("How Cargo-Vessel Match Scores Work: Laycan, DWT, Route, Confidence and Recency", "cargo-vessel-match-scores", "Explain match ranking as a review aid: how compatible route zones, laycan overlap, DWT, cargo quantity, extraction confidence and offer recency shape a shortlist. The broker still reviews the source email and makes the commercial decision. Link to /cargo-vessel-matching-software/ and /laycan-extraction-from-broker-emails/."),
    idea("Port Normalization for Shipbroker Emails: Why Port Names Break Search and Matching", "port-normalization-shipbroker-emails", "Show why spelling variants, aliases, regions and ambiguous port references make inbox search unreliable, and how structured normalization improves reviewable cargo-vessel matching. Do not claim a global port-data guarantee. Link to /ai-email-parser-for-shipbrokers/ and /cargo-vessel-matching-software/."),
    idea("How to Handle Duplicate Broker Circulars Without Losing the Original Source", "duplicate-broker-circulars", "Give an operational workflow for recognising repeats, preserving source provenance, avoiding duplicate work and keeping the original broker email available for audit. Link to /ai-email-parser-security-broker-mailboxes/ and /broker-productivity-tools/."),
    idea("How to Review Low-Confidence AI Email Extraction Before You Act on an Offer", "review-low-confidence-email-extraction", "Explain practical quality control for uncertain fields such as laycan, ports, DWT, quantity and counterparty details. Emphasise source-email review and broker judgement rather than automatic execution. Link to /ai-email-parser-for-shipbrokers/ and /laycan-extraction-from-broker-emails/."),
    idea("How to Search Historical Broker Emails for Cargo and Vessel Opportunities", "search-historical-broker-emails", "Cover how a searchable structured archive helps brokers revisit past cargo and vessel signals, while keeping recency and original context visible. Link to /broker-productivity-tools/ and /maritime-data-management/."),
    idea("How to Set Up a Vessel Position for Faster Cargo Matching", "set-up-vessel-position-cargo-matching", "Describe the reviewable inputs behind a useful vessel position: location or route zone, open date/laycan, DWT, vessel characteristics and constraints. Do not claim instant fixtures. Link to /cargo-vessel-matching-software/ and /ai-in-shipping/."),
    idea("How to Set Up a Cargo Requirement and Review Vessel Matches", "set-up-cargo-requirement-vessel-matches", "Explain capturing cargo type, quantity, load/discharge geography, laycan and commercial constraints before reviewing candidate vessels. Match suggestions support a broker decision, not a booking. Link to /cargo-vessel-matching-software/ and /laycan-extraction-from-broker-emails/."),
    idea("Broker Email Alerts: How to Surface New Matching Offers Without Inbox Noise", "broker-email-alerts-matching-offers", "Explain alerts as a controlled triage layer: use fit and recency to surface candidates, retain source context, and avoid treating every circular as an actionable match. Link to /broker-productivity-tools/ and /ai-email-parser-for-shipbrokers/."),
    idea("Laycan Overlap in Shipbroking: What It Means for Cargo-Vessel Matching", "laycan-overlap-cargo-vessel-matching", "Explain laycan overlap as one necessary match condition alongside route, vessel capacity and commercial detail. Avoid claiming that overlap alone creates a viable fixture. Link to /laycan-extraction-from-broker-emails/ and /cargo-vessel-matching-software/."),
    idea("From Broker Circular to Structured Offer: What Data Should Be Captured", "broker-circular-to-structured-offer", "Lay out the practical fields worth extracting from a broker circular, including cargo/vessel details, dates, ports, quantity, source and confidence. Link to /ai-email-parser-for-shipbrokers/ and /maritime-data-management/."),
    idea("Shared Shipbroker Inbox: How Teams Keep Cargo and Vessel Context Searchable", "shared-shipbroker-inbox-searchable-context", "Explain how shared teams preserve searchable context across broker emails without losing the original source or turning access into outbound email automation. Link to /ai-email-parser-security-broker-mailboxes/ and /broker-productivity-tools/."),
    idea("Why Source Email Review Still Matters After AI Parsing", "source-email-review-ai-parsing", "Explain why structured extraction speeds review but does not replace it: ambiguous terms, missing context, commercial nuance and confidence signals all require broker judgement. Link to /ai-email-parser-security-broker-mailboxes/ and /ai-email-parser-for-shipbrokers/."),
]


def request_json(url, method="GET", payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request(url, data=data, headers={"Content-Type": "application/json"}, method=method)
    with urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode())


def wait_for_draft(base_url, job_id, timeout_seconds):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        detail = request_json(f"{base_url}/api/sites/{SITE_ID}/content-jobs/{job_id}")
        job = detail["job"]
        status = str(job.get("status") or "").upper()
        if status == "DRAFT":
            return job
        if status in {"ERROR", "PUBLISHED"}:
            raise RuntimeError(f"first resource reached {status}: {job.get('error') or job.get('published_url')}")
        time.sleep(12)
    raise TimeoutError("first resource did not reach DRAFT before timeout")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:3299")
    parser.add_argument("--publish-first", action="store_true")
    parser.add_argument("--generation-timeout", type=int, default=1800)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    result = request_json(
        f"{base_url}/api/sites/{SITE_ID}/article-ideas/queue",
        method="POST",
        payload={"range": "approved-laycanmatch-operational-resources", "signals": [], "ideas": IDEAS},
    )
    jobs = result.get("jobs", [])
    if len(jobs) != len(IDEAS):
        raise RuntimeError(f"expected {len(IDEAS)} queued jobs, received {len(jobs)}: {result}")

    scheduled = []
    for index, job in enumerate(jobs[1:]):
        when = (FOLLOWING_FIRST_PUBLICATION + index * CADENCE).astimezone(timezone.utc).isoformat(timespec="seconds")
        scheduled_job = request_json(
            f"{base_url}/api/sites/{SITE_ID}/content-jobs/{job['id']}/schedule",
            method="POST",
            payload={"scheduledFor": when},
        )
        scheduled.append({"id": job["id"], "title": job["title"], "scheduledFor": scheduled_job["scheduledFor"]})

    first = jobs[0]
    published = None
    if args.publish_first:
        request_json(
            f"{base_url}/api/sites/{SITE_ID}/content-jobs/{first['id']}/generate",
            method="POST",
            payload={},
        )
        wait_for_draft(base_url, first["id"], args.generation_timeout)
        published = request_json(
            f"{base_url}/api/sites/{SITE_ID}/content-jobs/{first['id']}/publish",
            method="POST",
            payload={},
        )
    print(json.dumps({"queued": len(jobs), "first": first, "scheduled": scheduled, "published": published}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
