import json
import os
import re
import sqlite3
import subprocess
from datetime import datetime, timezone

# One-shot factory workers must inherit the same provider configuration as the
# long-running Blog Core process. Loading it before importing app prevents a
# manual or orchestrated batch from silently using a different environment.
processes = json.loads(subprocess.check_output(["pm2", "jlist"]))
blog_core_env = next(item for item in processes if item.get("name") == "blog-yas-core").get("pm2_env") or {}
for key, value in blog_core_env.items():
    if isinstance(value, (str, int, float)):
        os.environ[str(key)] = str(value)

import app

SITE_ID = 18
JOB_IDS = [
    "4a08cfc35db15ba93cf459b2",
    "4d8ef3e703b1bfe7c1f9f9ad",
    "901cae62e30a9e35f9fbd176",
    "22d8fd9edc0fc351a3a410ec",
    "6a3f52364b17f77be084f541",
    "180788b47048787fb1451377",
    "5422e70720b31003315adf9a",
    "f7d8f9ad672dcf26884de4e6",
    "4fe5f9e3e62982b03f747ed3",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


with app.db() as conn:
    site = conn.execute("select * from sites where id=?", (SITE_ID,)).fetchone()
    jobs = [conn.execute("select * from content_jobs where site_id=? and id=?", (SITE_ID, job_id)).fetchone() for job_id in JOB_IDS]
if not site or any(job is None for job in jobs):
    raise SystemExit("site or P0 job missing")

verified_jobs = []
for job in jobs:
    verified_sources = app.validate_public_source_references(job)
    with app.db() as conn:
        conn.execute(
            "update content_jobs set status='GENERATING',sources_json=?,error=NULL,updated_at=? where site_id=? and id=?",
            (json.dumps(verified_sources, ensure_ascii=False), now_iso(), SITE_ID, job["id"]),
        )
        conn.execute(
            "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
            (SITE_ID, job["id"], now_iso(), "INFO", "generate-batch", "P0 English batch generation started after source verification"),
        )
        verified_jobs.append(conn.execute("select * from content_jobs where site_id=? and id=?", (SITE_ID, job["id"])).fetchone())

requests = {job["id"]: app.build_universal_article_prompt(site, job) for job in verified_jobs}
results, batch_name = app._gemini_batch_text_json(
    requests,
    response_schema=app.ARTICLE_DRAFT_SCHEMA,
    temperature=0.1,
    timeout=int(os.environ.get("GEMINI_ARTICLE_BATCH_TIMEOUT", "7200")),
)

prepared = []
for job in verified_jobs:
    draft = results[job["id"]]
    draft = app.apply_approved_page_brief(draft, job, language=app.parse_languages(site["languages"])[0])
    draft = app.enforce_required_terminology(draft, job)
    draft = app.normalize_evidence_plan_source_ids(draft, job)
    draft = app.normalize_internal_link_section_indices(draft)
    draft = app.deduplicate_structured_article_copy(draft)
    draft = app.sanitize_typed_image_copy(draft)
    validation = app.validate_structured_article_draft(draft, job=job, language="en")
    slug = str(job["slug"] or "").strip() or app.simple_slug(draft.get("slug") or draft.get("title") or job["topic"])
    prepared.append((job, draft, validation, slug))

completed = []
for job, draft, validation, slug in prepared:
    try:
        hero_image_url, asset_prefix = app.generate_article_image_assets(SITE_ID, job["id"], site, job, draft, slug)
        html = app.render_structured_article_html(draft, slug, asset_prefix=asset_prefix, language="en")
        sources = app.content_job_sources(job)
        sources["generatedContentContract"] = {
            "structuredDraft": draft,
            "evidencePlan": draft.get("evidencePlan") if isinstance(draft.get("evidencePlan"), list) else [],
            "internalLinks": draft.get("internalLinks") if isinstance(draft.get("internalLinks"), list) else [],
            "recommendedNext": draft.get("recommendedNext") if isinstance(draft.get("recommendedNext"), list) else [],
            "validation": validation,
            "generatedAt": now_iso(),
            "batchName": batch_name,
            "batchModel": app.GEMINI_TRANSLATION_BATCH_MODEL,
        }
        faq = draft.get("faq") if isinstance(draft.get("faq"), list) else []
        with app.db() as conn:
            conn.execute(
                """update content_jobs set status='DRAFT',slug=?,title=?,description=?,category=?,hero_image=?,draft_html=?,faq_json=?,sources_json=?,error=NULL,scheduled_for=NULL,updated_at=? where site_id=? and id=?""",
                (
                    slug,
                    draft.get("title") or job["topic"],
                    draft.get("description") or "",
                    draft.get("category") or job["category"] or "Article",
                    hero_image_url,
                    html,
                    json.dumps(faq, ensure_ascii=False),
                    json.dumps(sources, ensure_ascii=False),
                    now_iso(),
                    SITE_ID,
                    job["id"],
                ),
            )
            current = conn.execute("select * from content_jobs where site_id=? and id=?", (SITE_ID, job["id"])).fetchone()
            conn.execute(
                "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
                (SITE_ID, job["id"], now_iso(), "INFO", "generate-batch-complete", f"English draft generated in Gemini Batch {batch_name}: {validation['word_count']} words"),
            )
        app.write_native_content_store(site, current, "drafts")
        completed.append(job["id"])
    except Exception as error:
        with app.db() as conn:
            conn.execute("update content_jobs set status='ERROR',error=?,updated_at=? where site_id=? and id=?", (str(error), now_iso(), SITE_ID, job["id"]))
        raise

print(json.dumps({"ok": True, "batch": batch_name, "model": app.GEMINI_TRANSLATION_BATCH_MODEL, "drafts": completed}, ensure_ascii=False))
