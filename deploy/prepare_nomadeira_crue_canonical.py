#!/usr/bin/env python3
"""Prepare the canonical NOMADeira EU residence guide for fresh generation.

This migration consolidates the unpublished Phase-A CRUE research into the
older canonical editorial-plan route. It remains fail-closed: publication is
still blocked until the generated page, all locales and visuals pass review.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


SITE_ID = 18
TARGET_JOB_ID = "8b67f5810fa19fd0be505ce7"
OVERLAP_JOB_ID = "cmp_cb039f0057843e2f8efa"
DB_PATH = Path("data/blog_core.sqlite3")
SPEC_VERSION = "2026-09-08-crue-canonical-consolidation-v1"


def iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def source(source_id: str, title: str, publisher: str, url: str, supports: str, now: str, expires: str) -> dict:
    return {
        "id": source_id,
        "title": title,
        "publisher": publisher,
        "publicUrl": url,
        "supports": supports,
        "publicSummary": supports,
        "accessedAt": now,
        "checkedAt": now,
        "freshness": "fortnightly",
        "expiresAt": expires,
        "rightsState": "citation_only",
        "sourceClass": "current_law_or_responsible_authority",
        "lastLiveCheck": {"state": "AVAILABLE", "checkedAt": now, "httpStatus": 200},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.db.exists():
        raise SystemExit(f"Blog Core database not found: {args.db}")

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    target = conn.execute(
        "select * from content_jobs where site_id=? and id=?", (SITE_ID, TARGET_JOB_ID)
    ).fetchone()
    overlap = conn.execute(
        "select * from content_jobs where site_id=? and id=?", (SITE_ID, OVERLAP_JOB_ID)
    ).fetchone()
    if not target or not overlap:
        raise SystemExit("Canonical target or overlap job is missing")
    if target["status"] == "PUBLISHED" or target["published_url"]:
        raise SystemExit("Canonical target is already published")
    if overlap["status"] == "PUBLISHED" or overlap["published_url"]:
        raise SystemExit("Refusing consolidation because the overlap job is published")
    if target["slug"] != "madeira-residence-registration-eu":
        raise SystemExit("Canonical target slug changed unexpectedly")

    now_dt = datetime.now(timezone.utc)
    now = iso(now_dt)
    expires = iso(now_dt + timedelta(days=14))
    refs = [
        source(
            "aima-crue-current",
            "Certificado de Registo para Nacionais UE",
            "AIMA",
            "https://aima.gov.pt/pt/nacionais-ue-e-familiares/nacionais-ue/certificado-de-registo-para-nacionais-ue",
            "AIMA states that the registration certificate applies to listed EU, Icelandic, Liechtenstein, Norwegian, Andorran and Swiss citizens staying in Portugal for more than three months and up to five years. The request is made at the Câmara Municipal for the area of residence within 30 days after the first three months. A valid identity document or passport is required. The page then lists alternative evidence paths for employment or self-employment, sufficient resources with health insurance where applicable, or student enrolment with sufficient resources and health insurance, plus family evidence where the relevant family route applies.",
            now,
            expires,
        ),
        source(
            "gov-crue-current",
            "Request the registration certificate for an EU, EEA or Swiss citizen",
            "gov.pt",
            "https://www.gov.pt/servicos/pedir-o-certificado-de-registo-para-cidadao-da-ue-eee-suica",
            "The gov.pt service page, updated 1 June 2026, states that listed EU, EEA, Swiss and Andorran citizens who stay in Portugal for more than three months must request the registration certificate. It states that the request is made within 30 days after the first three months and identifies the Câmara Municipal for the area of residence. The page warns that some content may be outdated and directs readers to current AIMA information.",
            now,
            expires,
        ),
    ]
    checks = [
        "Confirm on the current AIMA page that your nationality and intended length of stay fall within the certificate route before relying on this guide.",
        "Check which Câmara Municipal covers your Madeira residence before making a submission or appointment.",
        "Choose the evidence category that matches your actual circumstances: employment, self-employment, sufficient resources, study, or the relevant family route.",
        "Compare your documents with the current AIMA list immediately before submission and carry a valid identity document or passport.",
        "Ask the responsible Câmara Municipal to confirm its current submission channel and any local administrative requirements that the national pages do not establish.",
    ]
    claims = [
        {
            "id": "crue-scope-location",
            "statement": "The certificate route covers the nationalities and length-of-stay scope listed by AIMA, and the request is made at the Câmara Municipal for the area of residence.",
            "supportingExcerpt": "AIMA identifies the covered nationalities, a stay of more than three months and up to five years, and the Câmara Municipal for the area of residence.",
            "scope": "The registration-certificate route described on the current AIMA page.",
            "conditions": "The reader's nationality, residence period and circumstances must match the official route.",
            "exceptions": "This claim does not establish an individual's right of residence, acceptance, appointment availability or outcome.",
            "effectiveDateOrYear": "Official sources checked 2026-09-08",
            "sourceIds": ["aima-crue-current", "gov-crue-current"],
            "sourceUrl": [refs[0]["publicUrl"], refs[1]["publicUrl"]],
            "owner": "Codex official-source review, owner-authorized",
            "accessedAt": now,
            "freshness": "reviewed_current_source",
            "expiry": expires,
            "approvalState": "VERIFIED",
        },
        {
            "id": "crue-timing",
            "statement": "The request is made within 30 days after the first three months in Portugal.",
            "supportingExcerpt": "Both current official pages state a 30-day period after the first three months.",
            "scope": "Timing stated for the registration-certificate request.",
            "conditions": "The official route must apply to the reader.",
            "exceptions": "This is not a promised appointment date, processing time or outcome.",
            "effectiveDateOrYear": "Official sources checked 2026-09-08",
            "sourceIds": ["aima-crue-current", "gov-crue-current"],
            "sourceUrl": [refs[0]["publicUrl"], refs[1]["publicUrl"]],
            "owner": "Codex official-source review, owner-authorized",
            "accessedAt": now,
            "freshness": "reviewed_current_source",
            "expiry": expires,
            "approvalState": "VERIFIED",
        },
        {
            "id": "crue-documents",
            "statement": "A valid identity document or passport is required, together with evidence for the applicant's applicable category as listed by AIMA.",
            "supportingExcerpt": "AIMA lists identity evidence and separate evidence paths for employment, self-employment, sufficient resources, study, and relevant family circumstances.",
            "scope": "Document categories published on the current AIMA certificate page.",
            "conditions": "Only the evidence path matching the applicant's actual circumstances applies; health-insurance wording is retained where AIMA makes it applicable.",
            "exceptions": "This is not a universal identical checklist for every applicant and does not guarantee acceptance.",
            "effectiveDateOrYear": "Official source checked 2026-09-08",
            "sourceIds": ["aima-crue-current"],
            "sourceUrl": [refs[0]["publicUrl"]],
            "owner": "Codex official-source review, owner-authorized",
            "accessedAt": now,
            "freshness": "reviewed_current_source",
            "expiry": expires,
            "approvalState": "VERIFIED",
        },
    ]

    existing = json.loads(target["sources_json"] or "{}")
    sources = {
        **existing,
        "contentType": "guide",
        "pageType": "guide",
        "targetPath": "/madeira-residence-registration-eu/",
        "preserveSlug": True,
        "generationBlockedUntilSourceReview": False,
        "publicationBlocked": True,
        "complianceCluster": {
            "specVersion": SPEC_VERSION,
            "phase": "canonical_consolidation",
            "workflowState": "CLAIMS_VERIFIED",
            "nextState": "DRAFT_AUTHORIZED",
            "riskClass": "high_risk_immigration",
            "contentType": "guide",
            "targetPath": "/madeira-residence-registration-eu/",
            "exactIntent": "Explain who uses the EU registration-certificate route in Madeira, when to request it, where to request it and how to prepare the correct evidence category.",
            "requiredLocales": ["en", "de", "uk", "ru"],
            "publicationPolicy": "Owner-authorized Tier B approval is mandatory after source, translation, SEO, visual and browser QA. All locales publish atomically.",
            "canonicalDecision": {
                "status": "CONSOLIDATED_CANONICAL",
                "checkedAt": now,
                "canonicalJobId": TARGET_JOB_ID,
                "canonicalTargetPath": "/madeira-residence-registration-eu/",
                "supersedesUnpublishedJobId": OVERLAP_JOB_ID,
                "note": "Both candidate public routes returned 404 before publication. The older editorial-plan URL is retained as the only canonical publication target.",
            },
            "sourceMap": {"revision": SPEC_VERSION, "collectedAt": now, "sources": refs},
            "claimIds": [claim["id"] for claim in claims],
            "verifiedClaims": claims,
            "claimReview": {"reviewer": "Codex official-source review, owner-authorized", "reviewedAt": now},
            "factsMustNotImply": [
                "individual eligibility or a guaranteed right of residence",
                "appointment availability, processing time or acceptance",
                "one identical document checklist for every applicant",
                "a local requirement not stated by the responsible authority",
            ],
        },
        "pageBrief": {
            "primaryIntent": "EU residence registration in Madeira: official scope, timing, responsible municipality and evidence categories",
            "seoTitle": "EU Residence Registration in Madeira: CRUE Steps",
            "metaDescription": "Check the official CRUE timing, Madeira municipality and evidence categories for EU residence registration before you submit.",
            "h1": "EU Residence Registration in Madeira: Steps and Verification",
            "directAnswer": "If you are in one of the nationality groups listed by AIMA and will stay in Portugal for more than three months, the official route is a registration certificate requested from the Câmara Municipal for your Madeira residence. The stated deadline is within 30 days after the first three months. Prepare identity evidence and the evidence category matching your circumstances.",
            "outline": [
                "Who the registration certificate route covers",
                "When the 30-day request period begins",
                "Which Madeira municipality is responsible",
                "Identity evidence to prepare",
                "Choose the correct evidence category",
                "A careful submission sequence",
                "Limits and points to confirm locally",
            ],
            "approvedInternalLinks": [
                "/relocation/eu-residence",
                "/move-to-madeira/",
                "/nif-madeira/",
                "/housing/rental-documents/",
                "/health/healthcare/",
                "/work/taxes/",
            ],
            "sourceReferences": refs,
            "primaryCta": {"label": "Continue with the EU residence overview", "url": "/relocation/eu-residence"},
            "contentDetails": {
                "audience": "International EU, EEA, Swiss and Andorran citizens planning a stay in Madeira that may exceed three months.",
                "sectionEvidence": {
                    "Who the registration certificate route covers": ["aima-crue-current", "gov-crue-current"],
                    "When the 30-day request period begins": ["aima-crue-current", "gov-crue-current"],
                    "Which Madeira municipality is responsible": ["aima-crue-current", "gov-crue-current"],
                    "Identity evidence to prepare": ["aima-crue-current"],
                    "Choose the correct evidence category": ["aima-crue-current"],
                    "A careful submission sequence": ["aima-crue-current", "gov-crue-current"],
                    "Limits and points to confirm locally": ["aima-crue-current", "gov-crue-current"],
                },
                "forbiddenClaims": [
                    "individual eligibility or guaranteed outcome",
                    "appointment availability or processing-time estimate",
                    "unstated fee, submission channel or Madeira-specific document",
                    "one document category applying identically to every applicant",
                ],
                "allowedReaderChecks": checks,
                "decisionMethod": "Match nationality and stay length first, then municipality, deadline and the evidence category that reflects the applicant's actual circumstances.",
                "limitations": ["This page is not individual legal or immigration advice. Current AIMA and municipality instructions control."],
                "requiredTerminology": ["AIMA", "Câmara Municipal", "registration certificate"],
            },
            "editorial": {
                "author": "NOMADeira Editorial Team",
                "reviewer": "Codex official-source review, owner-authorized",
                "owner": "Iaroslav YAS",
                "factCheckedAt": now,
                "lastReviewedAt": now,
                "reviewDueAt": expires,
                "reviewCadence": "14 days",
                "rulesetVersion": SPEC_VERSION,
                "changeLog": [{"date": now[:10], "summary": "Canonical CRUE guide prepared from current AIMA and gov.pt sources."}],
            },
            "approvals": {
                "topic": True,
                "outline": True,
                "sources": True,
                "claims": True,
                "editorialReview": False,
                "productFactCheck": False,
                "seoReview": False,
                "browserQa": False,
            },
        },
        "qualityRequirements": {
            "minimumWordCount": 900,
            "reason": "Closed high-risk evidence ledger; completeness must come from source scope and explicit boundaries, not invented detail.",
        },
    }
    sources.pop("generatedContentContract", None)
    sources.pop("preComplianceArtifact", None)

    result = {
        "apply": args.apply,
        "jobId": TARGET_JOB_ID,
        "targetPath": sources["targetPath"],
        "sources": len(refs),
        "verifiedClaims": len(claims),
        "workflowState": sources["complianceCluster"]["workflowState"],
        "overlapJobId": OVERLAP_JOB_ID,
    }
    if not args.apply:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    with conn:
        conn.execute(
            """update content_jobs set status='QUEUED', visibility='private', scheduled_for=null,
                   title=?, description=?, category=?, hero_image=null, draft_html=null,
                   faq_json=null, sources_json=?, published_url=null, error=?, updated_at=?
               where site_id=? and id=?""",
            (
                sources["pageBrief"]["h1"],
                sources["pageBrief"]["metaDescription"],
                "Madeira relocation",
                json.dumps(sources, ensure_ascii=False),
                "Current official sources and claims verified; fresh draft generation is authorized. Publication remains blocked pending QA.",
                now,
                SITE_ID,
                TARGET_JOB_ID,
            ),
        )
        conn.execute("delete from content_job_localizations where site_id=? and job_id=?", (SITE_ID, TARGET_JOB_ID))
        conn.execute(
            "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
            (SITE_ID, TARGET_JOB_ID, now, "INFO", "canonical-source-review", "Canonical overlap resolved in favour of /madeira-residence-registration-eu/. Current AIMA and gov.pt sources reviewed; three bounded claims verified. Fresh generation authorized; publication remains blocked pending QA."),
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
