#!/usr/bin/env python3
"""Persist one approved Gemini image batch into native Blog Core article assets."""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, ".")
import app

SITE_ID = 18


def load_batch(batch_name: str) -> dict:
    api_key = os.environ.get("GEMINI_IMAGE_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_IMAGE_API_KEY is not configured")
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/{urllib.parse.quote(batch_name, safe='/')}",
        headers={"x-goog-api-key": api_key},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def first_image_bytes(response: dict) -> bytes:
    for candidate in response.get("candidates") or []:
        for part in ((candidate.get("content") or {}).get("parts") or []):
            inline = part.get("inlineData") or part.get("inline_data") or {}
            if inline.get("data"):
                return base64.b64decode(inline["data"])
    raise RuntimeError("batch response has no image data")


def main() -> None:
    with app.db() as conn:
        site = conn.execute("select * from sites where id=?", (SITE_ID,)).fetchone()
        rows = conn.execute("select * from content_jobs where site_id=? order by created_at", (SITE_ID,)).fetchall()
    jobs = [row for row in rows if (app.compliance_cluster_for_job(row) or {}).get("phase") == "A"]
    if len(jobs) != 12:
        raise RuntimeError(f"Expected 12 Phase-A jobs, got {len(jobs)}")
    batch_names = {str((app.content_job_sources(job).get("mediaBatchPlan") or {}).get("batchName") or "") for job in jobs}
    if len(batch_names) != 1 or not next(iter(batch_names)):
        raise RuntimeError("Phase-A jobs do not share one submitted image batch")
    batch_name = next(iter(batch_names))
    batch = load_batch(batch_name)
    metadata = batch.get("metadata") or {}
    if metadata.get("state") != "BATCH_STATE_SUCCEEDED":
        raise RuntimeError(f"Image batch is not complete: {metadata.get('state')}")
    container = (metadata.get("output") or {}).get("inlinedResponses") or {}
    responses = container.get("inlinedResponses") if isinstance(container, dict) else container
    response_by_key = {}
    provider_image_parts = 0
    for item in responses or []:
        key = str((item.get("metadata") or {}).get("key") or "")
        if key:
            response_by_key[key] = item.get("response") or {}
        for candidate in ((item.get("response") or {}).get("candidates") or []):
            provider_image_parts += sum(1 for part in ((candidate.get("content") or {}).get("parts") or []) if (part.get("inlineData") or part.get("inline_data") or {}).get("data"))
    expected = {f"{job['id']}:{item.get('role')}" for job in jobs for item in ((app.content_job_sources(job).get("mediaBatchPlan") or {}).get("items") or [])}
    missing = sorted(expected - set(response_by_key))
    if missing:
        raise RuntimeError(f"Image batch omitted {len(missing)} approved prompts")
    now = app.now_iso()
    for job in jobs:
        sources = app.content_job_sources(job)
        plan = sources.get("mediaBatchPlan") or {}
        generated = sources.get("generatedContentContract") or {}
        draft = generated.get("structuredDraft") or {}
        target_dir = app.article_asset_job_dir(SITE_ID, job["id"])
        target_dir.mkdir(parents=True, exist_ok=True)
        role_items = {item.get("role"): item for item in plan.get("items") or []}
        for role, item in role_items.items():
            raw = first_image_bytes(response_by_key[f"{job['id']}:{role}"])
            (target_dir / item["filename"]).write_bytes(app.optimize_article_image_to_webp(raw))
        hero = role_items["hero"]["filename"]
        draft["heroImage"] = hero
        images = draft.get("images") if isinstance(draft.get("images"), list) else []
        for index, image in enumerate(images[:3]):
            image["src"] = role_items[f"body-{index + 1}"]["filename"]
        generated["structuredDraft"] = draft
        sources["generatedContentContract"] = generated
        plan.update({"status": "IMAGES_COLLECTED", "collectedAt": now, "selectedImages": len(role_items), "extraProviderImagePartsIgnored": max(0, provider_image_parts - len(expected))})
        sources["mediaBatchPlan"] = plan
        asset_prefix = f"/sites/{SITE_ID}/article-assets/{urllib.parse.quote(str(job['id']), safe='')}"
        html = app.render_structured_article_html(draft, job["slug"], asset_prefix=asset_prefix, language="en", include_images=True)
        hero_url = app.article_asset_url(SITE_ID, job["id"], hero)
        with app.db() as conn:
            conn.execute("update content_jobs set status=?,hero_image=?,draft_html=?,sources_json=?,error=?,updated_at=? where id=?", ("DRAFT", hero_url, html, json.dumps(sources, ensure_ascii=False), "Images collected; visual QA and localization remain required before publication.", now, job["id"]))
            conn.execute("insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)", (SITE_ID, job["id"], now, "INFO", "image-batch-collect", f"Collected 4 selected image assets from Gemini batch {batch_name}; no publication."))
    print(json.dumps({"batch": batch_name, "articles": len(jobs), "selectedImages": len(expected), "providerResponses": len(response_by_key)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
