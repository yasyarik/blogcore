#!/usr/bin/env python3
"""Sync reviewed CRUE media metadata and record the final publication QA."""
from __future__ import annotations

import argparse
import html
import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app import (
    content_job_sources,
    db,
    native_content_store_filename,
    native_content_store_root,
    now_iso,
    validate_native_publish_contract,
    write_native_content_store,
)


SITE_ID = 18
JOB_ID = "8b67f5810fa19fd0be505ce7"
OVERLAP_JOB_ID = "cmp_cb039f0057843e2f8efa"
SPEC_VERSION = "2026-09-08-crue-canonical-consolidation-v1"

MEDIA_COPY = {
    "en": {
        "https-nomadeira.com-images-camara-municipal-entrance.webp": ("An applicant hands a closed document folder to a clerk at a municipal reception counter.", "The certificate request goes to the Câmara Municipal covering the applicant's area of residence."),
        "https-nomadeira.com-images-identity-passport-desk.webp": ("An applicant places a closed passport and face-down identity card beside an unmarked folder.", "A valid identity document or passport is the core identity evidence listed for the certificate request."),
        "https-nomadeira.com-images-evidence-category-folders.webp": ("An applicant separates one blank evidence bundle from several unmarked folders.", "The evidence bundle needs to match the applicant's employment, study, resources, or applicable family circumstances."),
    },
    "de": {
        "https-nomadeira.com-images-camara-municipal-entrance.webp": ("Eine antragstellende Person uebergibt am Empfangsschalter der Gemeinde eine geschlossene Dokumentenmappe.", "Der Antrag wird bei der fuer den Wohnsitz zustaendigen Câmara Municipal gestellt."),
        "https-nomadeira.com-images-identity-passport-desk.webp": ("Eine antragstellende Person legt einen geschlossenen Reisepass und einen verdeckten Ausweis neben eine unbeschriftete Mappe.", "Ein gueltiges Identitaetsdokument oder ein Reisepass ist der aufgefuehrte grundlegende Identitaetsnachweis."),
        "https-nomadeira.com-images-evidence-category-folders.webp": ("Eine antragstellende Person trennt ein leeres Nachweisbuendel von mehreren unbeschrifteten Mappen.", "Das Nachweisbuendel muss zu Beschaeftigung, Studium, Mitteln oder den einschlaegigen Familienumstaenden passen."),
    },
    "ru": {
        "https-nomadeira.com-images-camara-municipal-entrance.webp": ("Заявитель передает закрытую папку сотруднику муниципальной приемной.", "Заявление подают в Câmara Municipal, отвечающую за район проживания заявителя."),
        "https-nomadeira.com-images-identity-passport-desk.webp": ("Заявитель кладет закрытый паспорт и перевернутое удостоверение личности рядом с папкой без надписей.", "Действующее удостоверение личности или паспорт является основным указанным документом для запроса сертификата."),
        "https-nomadeira.com-images-evidence-category-folders.webp": ("Заявитель отделяет один комплект чистых документов от нескольких папок без надписей.", "Комплект документов должен соответствовать занятости, учебе, наличию средств или применимым семейным обстоятельствам заявителя."),
    },
    "uk": {
        "https-nomadeira.com-images-camara-municipal-entrance.webp": ("Заявник передає закриту папку працівнику муніципальної приймальні.", "Заяву подають до Câmara Municipal, що відповідає за район проживання заявника."),
        "https-nomadeira.com-images-identity-passport-desk.webp": ("Заявник кладе закритий паспорт і перевернуте посвідчення особи поруч із папкою без написів.", "Дійсне посвідчення особи або паспорт є основним зазначеним документом для запиту сертифіката."),
        "https-nomadeira.com-images-evidence-category-folders.webp": ("Заявник відокремлює один комплект чистих документів від кількох папок без написів.", "Комплект документів має відповідати зайнятості, навчанню, наявності коштів або застосовним сімейним обставинам заявника."),
    },
}


def replace_figure_copy(document: str, filename: str, alt: str, caption: str) -> str:
    pattern = re.compile(
        rf'(<figure class="article-figure"><img src="[^"]*{re.escape(filename)}" alt=")[^"]*("[^>]*><figcaption>).*?(</figcaption></figure>)',
        re.S,
    )
    replacement = rf"\g<1>{html.escape(alt, quote=True)}\g<2>{html.escape(caption)}\g<3>"
    updated, count = pattern.subn(replacement, document)
    if count != 1:
        raise ValueError(f"Expected one figure for {filename}, found {count}")
    return updated


def load_job(conn: sqlite3.Connection):
    row = conn.execute("select * from content_jobs where site_id=? and id=?", (SITE_ID, JOB_ID)).fetchone()
    if not row or row["status"] != "DRAFT":
        raise ValueError("CRUE target must be an unpublished DRAFT")
    return row


def remove_duplicate_payload_links(path: Path) -> None:
    """NOMADeira draftHtml already contains these links in reading context."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["internalLinks"] = []
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def sync_media() -> None:
    timestamp = now_iso()
    with db() as conn:
        job = load_job(conn)
        sources = content_job_sources(job)
        generated = sources.get("generatedContentContract") or {}
        draft = generated.get("structuredDraft") or {}
        by_name = {item.get("src"): item for item in draft.get("images") or [] if isinstance(item, dict)}
        for filename, (alt, caption) in MEDIA_COPY["en"].items():
            if filename not in by_name:
                raise ValueError(f"Generated image spec missing: {filename}")
            by_name[filename]["alt"] = alt
            by_name[filename]["caption"] = caption
            by_name[filename]["visualBrief"] = "A reviewed photorealistic editorial scene showing the exact physical preparation or municipal handoff described by the anchored paragraph, with all documents unmarked and no readable text."
        generated["structuredDraft"] = draft
        sources["generatedContentContract"] = generated
        english = job["draft_html"]
        for filename, (alt, caption) in MEDIA_COPY["en"].items():
            english = replace_figure_copy(english, filename, alt, caption)
        conn.execute(
            "update content_jobs set draft_html=?,sources_json=?,updated_at=? where site_id=? and id=?",
            (english, json.dumps(sources, ensure_ascii=False), timestamp, SITE_ID, JOB_ID),
        )
        for language in ("de", "ru", "uk"):
            row = conn.execute(
                "select draft_html from content_job_localizations where site_id=? and job_id=? and language=?",
                (SITE_ID, JOB_ID, language),
            ).fetchone()
            if not row:
                raise ValueError(f"Missing {language} localization")
            localized = row["draft_html"]
            for filename, (alt, caption) in MEDIA_COPY[language].items():
                localized = replace_figure_copy(localized, filename, alt, caption)
            conn.execute(
                "update content_job_localizations set draft_html=?,updated_at=? where site_id=? and job_id=? and language=?",
                (localized, timestamp, SITE_ID, JOB_ID, language),
            )
        conn.execute(
            "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
            (SITE_ID, JOB_ID, timestamp, "INFO", "visual-qa-correction", "Three body images were replaced after visual QA removed generated readable document and signage text. Alt text and captions were synchronized in EN, DE, RU and UK."),
        )
        refreshed = conn.execute("select * from content_jobs where site_id=? and id=?", (SITE_ID, JOB_ID)).fetchone()
    with db() as conn:
        site = conn.execute("select * from sites where id=?", (SITE_ID,)).fetchone()
    draft_path = write_native_content_store(site, refreshed, "drafts")
    remove_duplicate_payload_links(draft_path)
    print(json.dumps({"ok": True, "stage": "media-synced", "jobId": JOB_ID}, ensure_ascii=False))


def approve() -> None:
    timestamp = now_iso()
    review_due = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat(timespec="seconds")
    with db() as conn:
        job = load_job(conn)
        sources = content_job_sources(job)
        cluster = sources.get("complianceCluster") or {}
        if cluster.get("specVersion") != SPEC_VERSION:
            raise ValueError("Unexpected compliance contract version")
        brief = sources.get("pageBrief") or {}
        editorial = brief.get("editorial") or {}
        editorial.update({"lastReviewedAt": timestamp, "factCheckedAt": timestamp, "reviewDueAt": review_due})
        brief["editorial"] = editorial
        approvals = brief.get("approvals") or {}
        approvals.update({"editorialReview": True, "productFactCheck": True, "seoReview": True, "browserQa": True})
        brief["approvals"] = approvals
        sources["pageBrief"] = brief
        cluster["tierBApproval"] = {
            "status": "APPROVED",
            "approvedBy": "Iaroslav YAS",
            "approvedAt": timestamp,
            "allLocalesReviewed": True,
            "visualQaPassed": True,
        }
        cluster["workflowState"] = "APPROVED_FOR_SCHEDULING"
        cluster["nextState"] = "PUBLISHED"
        sources["complianceCluster"] = cluster
        sources["publicationBlocked"] = False
        conn.execute(
            "update content_jobs set sources_json=?,error=null,updated_at=? where site_id=? and id=?",
            (json.dumps(sources, ensure_ascii=False), timestamp, SITE_ID, JOB_ID),
        )
        conn.execute(
            "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
            (SITE_ID, JOB_ID, timestamp, "INFO", "publication-qa", "Official-source, editorial, SEO, localization, visual and browser QA passed; owner-requested Tier B approval recorded for immediate publication."),
        )
        approved_job = conn.execute("select * from content_jobs where site_id=? and id=?", (SITE_ID, JOB_ID)).fetchone()
        site = conn.execute("select * from sites where id=?", (SITE_ID,)).fetchone()
        contract = validate_native_publish_contract(site, approved_job)
    draft_path = write_native_content_store(site, approved_job, "drafts")
    remove_duplicate_payload_links(draft_path)
    print(json.dumps({"ok": True, "stage": "approved", "jobId": JOB_ID, "contract": contract}, ensure_ascii=False))


def supersede() -> None:
    timestamp = now_iso()
    with db() as conn:
        target = conn.execute("select * from content_jobs where site_id=? and id=?", (SITE_ID, JOB_ID)).fetchone()
        overlap = conn.execute("select * from content_jobs where site_id=? and id=?", (SITE_ID, OVERLAP_JOB_ID)).fetchone()
        if not target or target["status"] != "PUBLISHED" or not target["published_url"]:
            raise ValueError("Canonical target must be published before superseding overlap")
        if not overlap or overlap["status"] == "PUBLISHED" or overlap["published_url"]:
            raise ValueError("Overlap job is missing or already published")
        sources = content_job_sources(overlap)
        sources["supersededBy"] = {"jobId": JOB_ID, "targetPath": "/madeira-residence-registration-eu/", "at": timestamp}
        sources["publicationBlocked"] = True
        conn.execute(
            "update content_jobs set status='CANCELED',visibility='private',scheduled_for=null,sources_json=?,error=?,updated_at=? where site_id=? and id=?",
            (json.dumps(sources, ensure_ascii=False), "Superseded by the published canonical EU residence registration guide.", timestamp, SITE_ID, OVERLAP_JOB_ID),
        )
        conn.execute(
            "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
            (SITE_ID, OVERLAP_JOB_ID, timestamp, "INFO", "canonical-superseded", f"Unpublished overlap canceled after canonical job {JOB_ID} was published."),
        )
        site = conn.execute("select * from sites where id=?", (SITE_ID,)).fetchone()
    published_path = native_content_store_root(site, target) / "published" / native_content_store_filename(target, "published")
    remove_duplicate_payload_links(published_path)
    print(json.dumps({"ok": True, "stage": "overlap-superseded", "jobId": OVERLAP_JOB_ID}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("sync-media", "approve", "supersede"))
    args = parser.parse_args()
    {"sync-media": sync_media, "approve": approve, "supersede": supersede}[args.stage]()


if __name__ == "__main__":
    main()
