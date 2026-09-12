#!/usr/bin/env python3
"""Seed NOMADeira's Phase-A compliance briefs without drafting or publishing.

The records intentionally remain BLOCKED_EVIDENCE.  They create durable work in
the existing Blog Core content_jobs queue, but no article generator is allowed to
pick them up until a primary-source map and high-risk review data are complete.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


SITE_ID = 18
SPEC_VERSION = "2026-08-31"
DB_PATH = Path("data/blog_core.sqlite3")
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")


def article(slug, title, intent, core, authorities, content_type="supporting_guide"):
    return {
        "slug": slug,
        "title": title,
        "intent": intent,
        "parentCoreGuide": core,
        "authorities": authorities,
        "contentType": content_type,
    }


PHASE_A = [
    article("madeira-nif-bank-account-order", "NIF, bank account and address proof: the practical order", "Establish the practical order for NIF, bank account and address proof without claiming a universal order where providers differ.", "/relocation-paperwork", ["Autoridade Tributária", "gov.pt", "bank official onboarding terms"]),
    article("nif-portugal-through-representative", "Getting a Portuguese NIF through a representative: authority, documents and limitations", "Explain the authority, documents, scope and limitations of obtaining a Portuguese NIF through representation.", "/nif-madeira", ["Autoridade Tributária", "gov.pt", "Portuguese consular/MNE material where applicable"]),
    article("change-fiscal-address-portugal", "How to change a Portuguese fiscal address online or through Finanças", "Explain verified channels and boundaries for changing a Portuguese fiscal address, without conflating it with residence or tax residence.", "/relocation/fiscal-address", ["Autoridade Tributária", "gov.pt"]),
    article("madeira-crue-eu-residence-certificate", "CRUE in Madeira after three months: eligibility, documents and municipality", "Explain CRUE eligibility, documents and responsible Madeira municipality after three months.", "/relocation/eu-residence", ["AIMA", "gov.pt", "responsible Madeira Câmara Municipal"]),
    article("eu-citizen-non-eu-family-madeira", "Residence route for a non-EU family member of an EU citizen in Madeira", "Explain the evidence and route boundaries for a non-EU family member of an EU citizen in Madeira.", "/relocation/eu-residence", ["AIMA", "gov.pt", "Portuguese/EU legal primary material"]),
    article("portugal-d7-visa-madeira", "D7-style own-income route: evidence, sequence and what it does not cover", "Explain the source-backed own-income residence route without inferring eligibility from a visa nickname.", "/relocation/non-eu-residence", ["AIMA", "Portuguese Ministry of Foreign Affairs/consular material", "gov.pt"]),
    article("portugal-d8-visa-remote-employee", "D8-style route for a remote employee working for an employer outside Portugal", "Explain the evidence and sequence for a remote employee, preserving all eligibility boundaries and exceptions.", "/relocation/non-eu-residence", ["AIMA", "Portuguese Ministry of Foreign Affairs/consular material", "gov.pt"]),
    article("portugal-d8-visa-freelancer", "D8-style route for a freelancer with foreign clients", "Explain the evidence and sequence for a freelancer with foreign clients, without treating a nickname as proof of eligibility.", "/relocation/non-eu-residence", ["AIMA", "Portuguese Ministry of Foreign Affairs/consular material", "gov.pt"]),
    article("portugal-d2-visa-freelancer-entrepreneur", "D2-style route for independent professionals and entrepreneurs", "Explain the evidence and sequence for independent professionals and entrepreneurs, including what the route does not establish.", "/relocation/non-eu-residence", ["AIMA", "Portuguese Ministry of Foreign Affairs/consular material", "gov.pt"]),
    article("aima-after-arrival-portugal", "What happens at AIMA after entering Portugal on a residence visa", "Explain the post-arrival sequence only from current official AIMA and consular evidence.", "/relocation/non-eu-residence", ["AIMA", "Portuguese Ministry of Foreign Affairs/consular material", "gov.pt"]),
    article("open-activity-portugal-freelancer", "Opening atividade before the first recurring freelance job", "Explain when and how to open atividade before recurring freelance work, without providing individual tax advice.", "/work/self-employment", ["Autoridade Tributária", "Segurança Social", "gov.pt"]),
    article("recibos-verdes-first-invoice", "Recibos verdes: issuing the first invoice/receipt without confusing tax stages", "Explain the official invoice/receipt sequence and distinguish the tax stages that the document does not settle.", "/work/self-employment", ["Autoridade Tributária", "Segurança Social", "gov.pt"]),
]


def stable_id(slug: str) -> str:
    return "cmp_" + hashlib.sha256(f"nomadeira-compliance-phase-a|{slug}".encode()).hexdigest()[:20]


def payload(item):
    return {
        "contentType": "blog",
        "complianceCluster": {
            "specVersion": SPEC_VERSION,
            "phase": "A",
            "workflowState": "CANONICAL_CHECKED",
            "nextState": "SOURCES_COLLECTED",
            "riskClass": "high_risk",
            "contentType": item["contentType"],
            "targetPath": f"/{item['slug']}",
            "parentCoreGuide": item["parentCoreGuide"],
            "parentCoreRelationship": "Narrow supporting answer; it must not replace, duplicate or contradict the curated core guide.",
            "exactIntent": item["intent"],
            "requiredAuthorities": item["authorities"],
            "claimIds": [],
            "requiredClaimFields": ["sourceUrl", "owner", "supportingExcerpt", "accessedAt", "effectiveDateOrYear", "scope", "conditions", "exceptions", "freshness", "expiry", "approvalState"],
            "requiredLocales": ["en", "de", "uk", "ru"],
            "publicationPolicy": "Tier B human approval is mandatory. All four locales publish atomically only after evidence, localization and visual QA pass.",
            "canonicalDecision": {"status": "PASSED_QUEUE_CHECK", "checkedAt": NOW, "note": "No existing Blog Core job uses this exact target slug. Recheck the live canonical inventory before drafting."},
            "factsMustNotImply": ["eligibility or approval", "processing-time averages without official evidence", "that fiscal address, immigration residence and tax residence are interchangeable", "that an authority's missing listed fee means the service is free"],
        },
        "generationBlockedUntilSourceReview": True,
        "publicationBlocked": True,
    }


def main():
    if not DB_PATH.exists():
        raise SystemExit(f"Blog Core database not found: {DB_PATH}")
    created, adopted, existing = [], [], []
    with sqlite3.connect(DB_PATH) as conn:
        for item in PHASE_A:
            target_path = f"/{item['slug']}"
            collision = conn.execute(
                "select id, status, slug, draft_html, sources_json from content_jobs where site_id=? and slug=?",
                (SITE_ID, item["slug"]),
            ).fetchone()
            if collision:
                existing_payload = json.loads(collision[4] or "{}")
                if (existing_payload.get("complianceCluster") or {}).get("specVersion") == SPEC_VERSION:
                    existing.append({"slug": item["slug"], "existingJobId": collision[0], "status": collision[1]})
                    continue
                # A pre-existing unpublished job for the exact same URL is the
                # canonical record.  Protect it with the compliance gate rather
                # than creating a competing article task.  Published/drafted
                # content is deliberately not mutated by this seed.
                if collision[1] not in {"PUBLISHED", "DRAFT", "GENERATING"} and not (collision[3] or "").strip():
                    old_payload = existing_payload
                    old_payload.update(payload(item))
                    old_payload["complianceCluster"]["canonicalDecision"] = {
                        "status": "ADOPTED_EXISTING_QUEUE_RECORD",
                        "checkedAt": NOW,
                        "note": "Existing unpublished Blog Core job with the exact target slug was adopted; no duplicate was created.",
                    }
                    conn.execute(
                        """update content_jobs set status='BLOCKED_EVIDENCE', title=?, description=?, category=?, sources_json=?, visibility='private',
                           error=?, scheduled_for=null, updated_at=? where site_id=? and id=?""",
                        (item["title"], item["intent"], "Relocation & administration", json.dumps(old_payload, ensure_ascii=False),
                         "Compliance brief awaits current primary-source map and Tier B review.", NOW, SITE_ID, collision[0]),
                    )
                    conn.execute(
                        "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
                        (SITE_ID, collision[0], NOW, "info", "compliance_seed", "Existing Phase-A job adopted as a compliance brief; generation and publication are blocked pending primary evidence."),
                    )
                    adopted.append({"id": collision[0], "slug": item["slug"]})
                else:
                    existing.append({"slug": item["slug"], "existingJobId": collision[0], "status": collision[1]})
                continue
            job_id = stable_id(item["slug"])
            brief = payload(item)
            conn.execute(
                """insert into content_jobs(id,site_id,topic,slug,status,title,description,category,sources_json,visibility,error,created_at,updated_at)
                   values(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (job_id, SITE_ID, item["intent"], item["slug"], "BLOCKED_EVIDENCE", item["title"],
                 item["intent"], "Relocation & administration", json.dumps(brief, ensure_ascii=False), "private",
                 "Compliance brief awaits current primary-source map and Tier B review.", NOW, NOW),
            )
            conn.execute(
                "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
                (SITE_ID, job_id, NOW, "info", "compliance_seed", "Phase-A compliance brief seeded; generation and publication are blocked pending primary evidence."),
            )
            created.append({"id": job_id, "slug": item["slug"], "targetPath": target_path})
        # Earlier seed revisions could append an identical technical log on a
        # retry.  Keep the first audit event only; the canonical task record is
        # the authoritative state and no editorial/audit evidence is removed.
        placeholders = ",".join("?" for _ in PHASE_A)
        job_rows = conn.execute(
            f"select id from content_jobs where site_id=? and slug in ({placeholders})",
            (SITE_ID, *(item["slug"] for item in PHASE_A)),
        ).fetchall()
        job_ids = [row[0] for row in job_rows]
        if job_ids:
            id_marks = ",".join("?" for _ in job_ids)
            conn.execute(
                f"""delete from content_job_logs
                    where step=? and job_id in ({id_marks})
                      and id not in (
                          select min(id) from content_job_logs
                          where step=? and job_id in ({id_marks})
                          group by job_id
                      )""",
                ("compliance_seed", *job_ids, "compliance_seed", *job_ids),
            )
    print(json.dumps({"created": created, "adopted": adopted, "alreadyPresent": existing, "totalPhaseA": len(PHASE_A)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
