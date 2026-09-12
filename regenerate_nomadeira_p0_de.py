import json
import os
import subprocess
import urllib.parse

processes = json.loads(subprocess.check_output(["pm2", "jlist"]))
blog_core_env = next(item for item in processes if item.get("name") == "blog-yas-core").get("pm2_env") or {}
for key, value in blog_core_env.items():
    if isinstance(value, (str, int, float)):
        os.environ[str(key)] = str(value)

import app

SITE_ID = 18
LANGUAGE = "de"
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

with app.db() as conn:
    site = conn.execute("select * from sites where id=?", (SITE_ID,)).fetchone()
    jobs = [conn.execute("select * from content_jobs where site_id=? and id=?", (SITE_ID, job_id)).fetchone() for job_id in JOB_IDS]

drafts = {}
requests = {}
for job in jobs:
    generated = app.content_job_sources(job).get("generatedContentContract") or {}
    draft = generated.get("structuredDraft")
    if not isinstance(draft, dict):
        raise ValueError(f"job {job['id']} has no structured English draft")
    drafts[job["id"]] = draft
    requests[job["id"]] = app.build_article_translation_prompt(site, draft, LANGUAGE)

results, batch_name = app._gemini_batch_text_json(
    requests,
    response_schema=app.ARTICLE_DRAFT_SCHEMA,
    temperature=0.2,
    timeout=int(os.environ.get("GEMINI_TRANSLATION_BATCH_TIMEOUT", "7200")),
)

prepared = []
for job in jobs:
    draft = drafts[job["id"]]
    localized = app.preserve_translation_structure(draft, results[job["id"]])
    localized = app.apply_approved_category_label(localized, job, language=LANGUAGE)
    localized["slug"] = job["slug"]
    localized["heroImage"] = draft.get("heroImage") or ""
    source_images = draft.get("images") if isinstance(draft.get("images"), list) else []
    translated_images = localized.get("images") if isinstance(localized.get("images"), list) else []
    localized["images"] = [
        {
            "src": source_image.get("src") or f"{job['slug']}-image-{index + 1}.webp",
            "alt": (translated_images[index].get("alt") if index < len(translated_images) and isinstance(translated_images[index], dict) else "") or source_image.get("alt") or "",
            "caption": (translated_images[index].get("caption") if index < len(translated_images) and isinstance(translated_images[index], dict) else "") or source_image.get("caption") or "",
        }
        for index, source_image in enumerate(source_images)
    ]
    validation = app.validate_structured_article_translation(draft, localized, job, LANGUAGE)
    asset_prefix = f"/sites/{SITE_ID}/article-assets/{urllib.parse.quote(str(job['id']), safe='')}"
    html = app.render_structured_article_html(localized, job["slug"], asset_prefix=asset_prefix, language=LANGUAGE)
    prepared.append((job, localized, validation, html))

now = app.now_iso()
with app.db() as conn:
    for job, localized, validation, html in prepared:
        conn.execute("delete from content_job_localizations where site_id=? and job_id=? and language=?", (SITE_ID, job["id"], LANGUAGE))
        conn.execute(
            """insert into content_job_localizations(site_id,job_id,language,slug,title,description,category,draft_html,faq_json,created_at,updated_at) values(?,?,?,?,?,?,?,?,?,?,?)""",
            (SITE_ID, job["id"], LANGUAGE, job["slug"], localized.get("title") or job["topic"], localized.get("description") or "", localized.get("category") or job["category"] or "Article", html, json.dumps(localized.get("faq") or [], ensure_ascii=False), now, now),
        )
        conn.execute(
            "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
            (SITE_ID, job["id"], now, "INFO", "localize", f"DE localization regenerated with native Unicode orthography by {app.GEMINI_TRANSLATION_BATCH_MODEL} Batch {batch_name}: {validation['word_count']} words."),
        )

for job in jobs:
    app.publish_content_job(SITE_ID, job["id"])

print(json.dumps({"ok": True, "batch": batch_name, "jobs": len(jobs), "language": LANGUAGE}))
