#!/usr/bin/env python3
"""Migrate eight scheduled legacy NOMADeira briefs into the current gate.

The migration is deliberately fail-closed. It removes publication schedules
and active pre-review generated artifacts, but never invents sources, verified
claims, reviews, approvals, or QA results. The original database must be backed
up before ``--apply`` is used in production.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


SITE_ID = 18
DB_PATH = Path("data/blog_core.sqlite3")
SPEC_VERSION = "2026-09-08-editorial-plan-migration-v1"
TARGET_SLUGS = (
    "madeira-residence-registration-eu",
    "remote-work-in-madeira-internet-checklist",
    "moving-to-madeira-with-children",
    "madeira-car-or-no-car",
    "things-to-do-canyoning",
    "things-to-do-surfing",
    "madeira-month-by-month",
    "buy-or-rent-madeira",
)
RISK_CLASSES = {
    "madeira-residence-registration-eu": "high_risk_immigration",
    "remote-work-in-madeira-internet-checklist": "source_sensitive_provider_claims",
    "moving-to-madeira-with-children": "high_risk_health_and_education",
    "madeira-car-or-no-car": "source_sensitive_transport_and_commercial",
    "things-to-do-canyoning": "high_risk_activity_safety",
    "things-to-do-surfing": "high_risk_activity_safety",
    "madeira-month-by-month": "volatile_weather_and_events",
    "buy-or-rent-madeira": "high_risk_property_and_tax",
}
CRUE_OVERLAP_JOB_ID = "cmp_cb039f0057843e2f8efa"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_object(value) -> dict:
    try:
        parsed = json.loads(value or "{}")
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def migrated_sources(row, timestamp: str) -> dict:
    sources = parse_object(row["sources_json"])
    if sources.get("source") != "nomadeira_editorial_plan":
        raise ValueError(f"{row['slug']}: source is not nomadeira_editorial_plan")
    existing_cluster = sources.get("complianceCluster")
    if isinstance(existing_cluster, dict):
        if existing_cluster.get("specVersion") == SPEC_VERSION:
            return sources
        raise ValueError(f"{row['slug']}: an unrelated complianceCluster already exists")

    generated = sources.pop("generatedContentContract", None)
    sources.pop("pageBrief", None)
    target_path = str(sources.get("targetPath") or f"/{row['slug']}").strip()
    exact_intent = str(sources.get("brief") or sources.get("angle") or row["topic"] or "").strip()
    required_authorities = [
        str(value).strip()
        for value in (sources.get("requiredSourceTypes") or [])
        if str(value).strip()
    ]
    canonical_decision = {
        "status": "MIGRATED_EXISTING_QUEUE_RECORD",
        "checkedAt": timestamp,
        "note": "Existing unpublished editorial-plan record retained as the sole task for its exact target path; live canonical inventory must be rechecked before claim review.",
    }
    if row["slug"] == "madeira-residence-registration-eu":
        canonical_decision = {
            "status": "REQUIRES_INTENT_OVERLAP_REVIEW",
            "checkedAt": timestamp,
            "possibleOverlapJobId": CRUE_OVERLAP_JOB_ID,
            "note": "Review overlap with the existing CRUE guide before evidence collection. Do not publish two pages that satisfy the same canonical intent.",
        }

    sources["complianceCluster"] = {
        "specVersion": SPEC_VERSION,
        "phase": "legacy_editorial_plan_migration",
        "workflowState": "CANONICAL_REVIEW_REQUIRED" if row["slug"] == "madeira-residence-registration-eu" else "CANONICAL_CHECKED",
        "nextState": "SOURCES_COLLECTED",
        "riskClass": RISK_CLASSES[row["slug"]],
        "contentType": str(sources.get("contentType") or "guide"),
        "targetPath": target_path,
        "exactIntent": exact_intent,
        "requiredAuthorities": required_authorities,
        "claimIds": [],
        "requiredClaimFields": [
            "sourceUrl", "owner", "supportingExcerpt", "accessedAt",
            "effectiveDateOrYear", "scope", "conditions", "exceptions",
            "freshness", "expiry", "approvalState",
        ],
        "requiredLocales": list(sources.get("requiredLocales") or ["en", "de", "uk", "ru"]),
        "publicationPolicy": "Tier B human approval is mandatory. All configured locales publish atomically only after evidence, localization and visual QA pass.",
        "canonicalDecision": canonical_decision,
        "factsMustNotImply": [
            "individual eligibility or guaranteed outcome",
            "stable prices, schedules, availability or conditions without current evidence",
            "that generated media or generated prose is evidence",
            "that missing official detail proves a service is free or unrestricted",
        ],
    }
    sources["generationBlockedUntilSourceReview"] = True
    sources["publicationBlocked"] = True
    sources["preComplianceArtifact"] = {
        "discardedAt": timestamp,
        "reason": "Generated before the required source and claim review; removed from the active draft contract.",
        "hadDraftHtml": bool(str(row["draft_html"] or "").strip()),
        "hadHeroImage": bool(str(row["hero_image"] or "").strip()),
        "hadGeneratedContentContract": isinstance(generated, dict),
        "generatedAt": str((generated or {}).get("generatedAt") or "") if isinstance(generated, dict) else "",
    }
    return sources


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.db.exists():
        raise SystemExit(f"Blog Core database not found: {args.db}")

    marks = ",".join("?" for _ in TARGET_SLUGS)
    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        f"""select * from content_jobs where site_id=? and slug in ({marks})
            order by scheduled_for,created_at,id""",
        (SITE_ID, *TARGET_SLUGS),
    ).fetchall()
    found = {row["slug"] for row in rows}
    missing = sorted(set(TARGET_SLUGS) - found)
    if missing:
        raise SystemExit("Missing migration targets: " + ", ".join(missing))
    invalid = [row["slug"] for row in rows if row["status"] == "PUBLISHED" or row["published_url"]]
    if invalid:
        raise SystemExit("Refusing to migrate published targets: " + ", ".join(invalid))

    timestamp = now_iso()
    plan = []
    for row in rows:
        current_sources = parse_object(row["sources_json"])
        already_migrated = (current_sources.get("complianceCluster") or {}).get("specVersion") == SPEC_VERSION
        sources = migrated_sources(row, timestamp)
        cluster = sources["complianceCluster"]
        plan.append({
            "id": row["id"],
            "slug": row["slug"],
            "fromStatus": row["status"],
            "fromSchedule": row["scheduled_for"],
            "toStatus": "BLOCKED_EVIDENCE",
            "workflowState": cluster["workflowState"],
            "riskClass": cluster["riskClass"],
            "removedDraft": bool(str(row["draft_html"] or "").strip()),
            "alreadyMigrated": already_migrated,
        })
    if not args.apply:
        print(json.dumps({"apply": False, "count": len(plan), "plan": plan}, ensure_ascii=False, indent=2))
        return

    migrated_count = 0
    with conn:
        for row in rows:
            current_sources = parse_object(row["sources_json"])
            if (current_sources.get("complianceCluster") or {}).get("specVersion") == SPEC_VERSION:
                continue
            sources = migrated_sources(row, timestamp)
            conn.execute(
                """update content_jobs set status='BLOCKED_EVIDENCE',visibility='private',scheduled_for=null,
                       hero_image=null,draft_html=null,faq_json=null,sources_json=?,error=?,updated_at=?
                   where site_id=? and id=?""",
                (
                    json.dumps(sources, ensure_ascii=False),
                    "Current-contract migration complete; primary sources, verified claims and Tier B approval are required before generation or publication.",
                    timestamp, SITE_ID, row["id"],
                ),
            )
            conn.execute("delete from content_job_localizations where site_id=? and job_id=?", (SITE_ID, row["id"]))
            conn.execute(
                "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
                (
                    SITE_ID, row["id"], timestamp, "INFO", "compliance-contract-migration",
                    "Legacy editorial-plan task moved to the current evidence contract; schedule and pre-review active draft artifacts cleared. No source, claim, review, approval or QA state was inferred.",
                ),
            )
            migrated_count += 1
    print(json.dumps({"apply": True, "count": migrated_count, "migrated": plan}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
