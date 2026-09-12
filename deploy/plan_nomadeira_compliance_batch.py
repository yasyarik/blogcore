#!/usr/bin/env python3
"""Generate English evidence drafts and exact image prompts in one Gemini batch.

This does not generate image bytes.  It persists a reviewable hero + three
paragraph-bound image prompts for every draft, so a later image batch receives
the complete approved set at once.
"""
from __future__ import annotations

import argparse
import json
import sys

sys.path.insert(0, ".")
import app

SITE_ID = 18

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", action="append", default=[])
    args = parser.parse_args()
    with app.db() as conn:
        site = conn.execute("select * from sites where id=?", (SITE_ID,)).fetchone()
        rows = conn.execute("select * from content_jobs where site_id=? and status='QUEUED'", (SITE_ID,)).fetchall()
    jobs = [row for row in rows if (app.compliance_cluster_for_job(row) or {}).get("phase") == "A" and (not args.slug or row["slug"] in set(args.slug))]
    if not jobs:
        raise SystemExit("No eligible compliance jobs")
    requests = {}
    for job in jobs:
        app.validate_compliance_generation_gate(job)
        verified = app.validate_public_source_references(job)
        if verified != app.content_job_sources(job):
            with app.db() as conn:
                conn.execute("update content_jobs set sources_json=?,updated_at=? where id=?", (json.dumps(verified, ensure_ascii=False), app.now_iso(), job["id"]))
                job = conn.execute("select * from content_jobs where id=?", (job["id"],)).fetchone()
        requests[job["id"]] = app.build_universal_article_prompt(site, job)
    results, batch_name = app._gemini_batch_text_json(requests, response_schema=app.ARTICLE_DRAFT_SCHEMA, temperature=0.1)
    saved = []
    for job in jobs:
        draft = results[job["id"]]
        draft = app.apply_approved_page_brief(draft, job, language="en")
        draft = app.enforce_required_terminology(draft, job)
        draft = app.normalize_evidence_plan_source_ids(draft, job)
        draft = app.normalize_internal_link_section_indices(draft)
        draft = app.deduplicate_structured_article_copy(draft)
        draft = app.sanitize_typed_image_copy(draft)
        validation = app.validate_structured_article_draft(draft, job=job, language="en")
        slug = str(job["slug"] or "").strip()
        hero_plan = app.plan_article_hero_visual(site, job, draft)
        image_plan = [{"role":"hero", "filename":f"{slug}-hero.webp", "prompt":app.build_article_image_prompt(site, job, draft, {"alt":draft.get("title") or job["topic"],"caption":draft.get("description") or ""}, "hero", visual_plan=hero_plan)}]
        for index, image in enumerate(draft.get("images") or []):
            visual_plan = app.paragraph_bound_body_visual_plan(draft, image)
            image_plan.append({"role":f"body-{index+1}", "filename":f"{slug}-image-{index+1}.webp", "prompt":app.build_article_image_prompt(site, job, draft, image, f"body image {index+1}", visual_plan=visual_plan), "sectionIndex":image.get("sectionIndex"), "paragraphIndex":image.get("paragraphIndex")})
        sources = app.content_job_sources(job)
        sources["generatedContentContract"] = {"structuredDraft":draft, "evidencePlan":draft.get("evidencePlan") or [], "validation":validation, "generatedAt":app.now_iso(), "batch":batch_name}
        sources["mediaBatchPlan"] = {"status":"READY_FOR_SINGLE_BATCH", "model":"gemini-3.1-flash-image", "items":image_plan, "createdAt":app.now_iso(), "batchText":batch_name}
        html = app.render_structured_article_html(draft, slug, language="en", include_images=False)
        with app.db() as conn:
            conn.execute("update content_jobs set status='DRAFT',title=?,description=?,draft_html=?,faq_json=?,hero_image='',sources_json=?,error=?,updated_at=? where id=?", (draft.get("title") or job["topic"], draft.get("description") or "", html, json.dumps(draft.get("faq") or [],ensure_ascii=False), json.dumps(sources,ensure_ascii=False), "Visual plan ready; image batch and localization QA pending.", app.now_iso(), job["id"]))
            conn.execute("insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)", (SITE_ID,job["id"],app.now_iso(),"INFO","compliance-batch-plan",f"English evidence draft and {len(image_plan)} image prompts prepared in Gemini Batch {batch_name}; no media generated."))
        saved.append({"slug":slug,"words":validation["word_count"],"imagePrompts":len(image_plan)})
    print(json.dumps({"batch":batch_name,"jobs":saved},ensure_ascii=False,indent=2))

if __name__ == "__main__": main()
