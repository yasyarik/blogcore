#!/usr/bin/env python3
"""Build every Phase-A visual prompt, then submit one Gemini image batch.

English drafts are generated synchronously only when missing.  No image request
is made until the complete 12 x 4 prompt ledger is persisted.  The Gemini batch
name is written to every affected job immediately after submission, so a later
collector can resume from that exact provider job without resubmitting.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, ".")
import app

SITE_ID = 18
IMAGE_MODEL = "gemini-3.1-flash-image"


def phase_a_jobs():
    with app.db() as conn:
        rows = conn.execute("select * from content_jobs where site_id=? order by created_at, id", (SITE_ID,)).fetchall()
    return [row for row in rows if (app.compliance_cluster_for_job(row) or {}).get("phase") == "A"]


def build_visual_items(site, job):
    sources = app.content_job_sources(job)
    generated = sources.get("generatedContentContract") or {}
    draft = generated.get("structuredDraft")
    if not isinstance(draft, dict):
        raise RuntimeError(f"{job['slug']}: missing generated English draft")
    slug = str(job["slug"] or "").strip()
    hero_filename = f"{slug}-hero.webp"
    hero_plan = app.plan_article_hero_visual(site, job, draft)
    draft["heroVisualPlan"] = hero_plan
    draft["heroImage"] = hero_filename
    items = [{
        "key": f"{job['id']}:hero",
        "jobId": job["id"],
        "role": "hero",
        "filename": hero_filename,
        "prompt": app.build_article_image_prompt(
            site, job, draft,
            {"alt": draft.get("title") or job["topic"], "caption": draft.get("description") or ""},
            "hero", visual_plan=hero_plan,
        ),
    }]
    normalized_images = []
    for index, image in enumerate((draft.get("images") or [])[:3]):
        if not isinstance(image, dict):
            continue
        normalized = dict(image)
        normalized["src"] = f"{slug}-image-{index + 1}.webp"
        normalized_images.append(normalized)
        visual_plan = app.paragraph_bound_body_visual_plan(draft, normalized)
        items.append({
            "key": f"{job['id']}:body-{index + 1}",
            "jobId": job["id"],
            "role": f"body-{index + 1}",
            "filename": normalized["src"],
            "sectionIndex": normalized.get("sectionIndex"),
            "paragraphIndex": normalized.get("paragraphIndex"),
            "prompt": app.build_article_image_prompt(site, job, draft, normalized, f"body image {index + 1}", visual_plan=visual_plan),
        })
    if len(items) != 4:
        raise RuntimeError(f"{slug}: expected hero + 3 body prompts, got {len(items)}")
    draft["images"] = normalized_images
    generated["structuredDraft"] = draft
    sources["generatedContentContract"] = generated
    sources["mediaBatchPlan"] = {
        "status": "READY_FOR_SINGLE_BATCH",
        "model": IMAGE_MODEL,
        "items": items,
        "createdAt": app.now_iso(),
        "note": "Complete prompt ledger exists before the single image batch is submitted.",
    }
    with app.db() as conn:
        conn.execute(
            "update content_jobs set hero_image='', sources_json=?, error=?, updated_at=? where id=?",
            (json.dumps(sources, ensure_ascii=False), "All four unique visual prompts are ready; image batch is pending submission.", app.now_iso(), job["id"]),
        )
    return items


def submit_batch(items):
    api_key = os.environ.get("GEMINI_IMAGE_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_IMAGE_API_KEY is not configured")
    requests = []
    for item in items:
        requests.append({
            "request": {
                "contents": [{"role": "user", "parts": [{"text": item["prompt"]}]}],
                "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": "16:9"}},
            },
            "metadata": {"key": item["key"]},
        })
    payload = {"batch": {"display_name": f"nomadeira-phase-a-images-{app.datetime.now(app.timezone.utc).strftime('%Y%m%d-%H%M%S')}", "input_config": {"requests": {"requests": requests}}}}
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{urllib.parse.quote(IMAGE_MODEL, safe='.-')}:batchGenerateContent"
    request = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers={"content-type": "application/json", "x-goog-api-key": api_key}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read(2200).decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini image batch create HTTP {error.code}: {detail}") from error
    name = str(data.get("name") or "").strip()
    if not name:
        raise RuntimeError(f"Gemini image batch did not return a name: {data}")
    return name


def main():
    jobs = phase_a_jobs()
    if len(jobs) != 12:
        raise RuntimeError(f"Expected exactly 12 Phase-A jobs, found {len(jobs)}")
    # Complete every English content contract first. Image generation remains deferred.
    for job in jobs:
        sources = app.content_job_sources(job)
        draft = (sources.get("generatedContentContract") or {}).get("structuredDraft")
        if not isinstance(draft, dict):
            print(json.dumps({"stage": "draft", "slug": job["slug"]}, ensure_ascii=False), flush=True)
            app.generate_content_job(SITE_ID, job["id"], localize=False)
    jobs = phase_a_jobs()
    with app.db() as conn:
        site = conn.execute("select * from sites where id=?", (SITE_ID,)).fetchone()
    all_items = []
    for job in jobs:
        plan = (app.content_job_sources(job).get("mediaBatchPlan") or {})
        if plan.get("status") == "IMAGE_BATCH_SUBMITTED":
            raise RuntimeError(f"{job['slug']}: image batch already submitted ({plan.get('batchName')})")
        all_items.extend(build_visual_items(site, job))
    if len(all_items) != 48:
        raise RuntimeError(f"Expected 48 unique image prompts, got {len(all_items)}")
    print(json.dumps({"stage": "ledger-ready", "images": len(all_items), "articles": len(jobs)}, ensure_ascii=False), flush=True)
    batch_name = submit_batch(all_items)
    now = app.now_iso()
    by_job = {}
    for item in all_items:
        by_job.setdefault(item["jobId"], []).append(item)
    with app.db() as conn:
        for job in jobs:
            sources = app.content_job_sources(job)
            plan = sources.get("mediaBatchPlan") or {}
            plan.update({"status": "IMAGE_BATCH_SUBMITTED", "batchName": batch_name, "submittedAt": now})
            sources["mediaBatchPlan"] = plan
            conn.execute("update content_jobs set sources_json=?, error=?, updated_at=? where id=?", (json.dumps(sources, ensure_ascii=False), f"Gemini image batch submitted: {batch_name}", now, job["id"]))
            conn.execute("insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)", (SITE_ID, job["id"], now, "INFO", "image-batch-submit", f"One 48-image Gemini batch submitted: {batch_name}"))
    print(json.dumps({"stage": "submitted", "batch": batch_name, "images": len(all_items)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
