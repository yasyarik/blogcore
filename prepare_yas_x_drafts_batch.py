"""Build reviewable YAS X drafts with batch-planned and batch-rendered visuals.

This is intentionally an offline production worker: it never talks to Zernio.
It turns existing X work items into normal Blog Core social_posts only after
Gemini has returned every required visual asset.
"""

import json
import os
import time
import urllib.parse
import urllib.request
from base64 import b64decode
from datetime import datetime, timezone
from io import BytesIO

from PIL import Image, ImageOps

from app import (
    _gemini_batch_text_json,
    _x_weighted_length,
    agent_log,
    db,
    now_iso,
    social_asset_job_dir,
    social_asset_url,
    site_logo_reference,
)

SITE_ID = 12
# A running batch can materialize the ready portion while queue discovery finishes
# the final item.  The production default remains 30.
TARGET_COUNT = int(os.environ.get("YAS_X_DRAFT_TARGET", "30"))


def active_work_items():
    with db() as conn:
        return conn.execute(
            """select wi.*, cj.title as article_title, cj.description as article_description
               from social_work_items wi
               join content_jobs cj on cj.id=wi.source_job_id and cj.site_id=wi.site_id
               where wi.site_id=? and wi.channel='twitter'
                 and wi.status in ('DRAFT','AWAITING_APPROVAL')
               order by wi.created_at, wi.id""",
            (SITE_ID,),
        ).fetchall()


def wait_for_target():
    deadline = time.monotonic() + 7200
    while True:
        rows = active_work_items()
        if len(rows) >= TARGET_COUNT:
            return rows[:TARGET_COUNT]
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Only {len(rows)} of {TARGET_COUNT} X work items were available")
        time.sleep(30)


def visual_plan_prompt(row):
    return f"""You are the visual editor for a native X post from YAS, a company that builds bespoke business systems from scratch.

POST TITLE: {row['title']}
POST COPY: {row['body']}
SOURCE ARTICLE: {row['article_title']}
SOURCE CONTEXT: {row['article_description'] or ''}

Return JSON only with hookText, visualBrief, altText, and avoid.
- hookText: exactly 2-5 ordinary English words that make the concrete operational problem immediately understandable.
- visualBrief: one specific, striking 16:9 editorial-illustration scene. It must visibly show the business bottleneck, the custom system doing a concrete part of the work, and the human retaining a final judgment. Do not use generic laptops, dashboards, flowcharts, meetings, robots, blue glowing nodes, or a before/after split screen.
- The official YAS logo will be supplied separately. Describe one natural, prominent placement for it in the scene.
- Do not claim unverified savings, revenue, speed or outcomes. Do not create a caption, fake interface copy, labels, small text or a stock-photo concept.
- avoid: at least five visual clichés or repetitions specific to this post.
""".strip()


def batch_images(specs, reference):
    api_key = os.environ.get("GEMINI_IMAGE_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    model = os.environ.get("GEMINI_IMAGE_MODEL") or "gemini-3.1-flash-image"
    if not api_key:
        raise RuntimeError("Gemini image API key is not configured")
    requests = []
    for key, spec in specs.items():
        parts = [{"text": spec["prompt"]}]
        if reference:
            parts.append({"inlineData": {"mimeType": reference["mime_type"], "data": reference["data"]}})
        requests.append({
            "request": {
                "contents": [{"role": "user", "parts": parts}],
                "generationConfig": {
                    "responseModalities": ["IMAGE"],
                    "imageConfig": {"aspectRatio": "16:9"},
                },
            },
            "metadata": {"key": key},
        })
    payload = {"batch": {"display_name": f"yas-x-visuals-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}", "input_config": {"requests": {"requests": requests}}}}
    url = "https://generativelanguage.googleapis.com/v1beta/models/" + urllib.parse.quote(model, safe=".-") + ":batchGenerateContent"
    request = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"content-type": "application/json", "x-goog-api-key": api_key}, method="POST")
    with urllib.request.urlopen(request, timeout=180) as response:
        batch = json.loads(response.read().decode())
    batch_name = str(batch.get("name") or "")
    if not batch_name:
        raise RuntimeError(f"Image batch did not return a name: {batch}")
    print(json.dumps({"stage": "image-batch-created", "batch": batch_name, "requests": len(requests)}, ensure_ascii=False), flush=True)
    deadline = time.monotonic() + 7200
    while True:
        status_request = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/" + urllib.parse.quote(batch_name, safe="/"), headers={"x-goog-api-key": api_key})
        with urllib.request.urlopen(status_request, timeout=120) as response:
            batch = json.loads(response.read().decode())
        state = str(batch.get("state") or (batch.get("metadata") or {}).get("state") or "")
        stats = (batch.get("metadata") or {}).get("batchStats") or {}
        print(json.dumps({"stage": "image-batch-status", "batch": batch_name, "state": state, "stats": stats}, ensure_ascii=False), flush=True)
        if state in {"BATCH_STATE_SUCCEEDED", "JOB_STATE_SUCCEEDED"}:
            break
        if state in {"BATCH_STATE_FAILED", "BATCH_STATE_CANCELLED", "BATCH_STATE_EXPIRED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}:
            raise RuntimeError(f"Image batch {batch_name} ended in {state}: {batch.get('error')}")
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Image batch {batch_name} did not finish within two hours")
        time.sleep(20)
    # Gemini returns inline batch results under `response` on the current
    # Developer API, while older variants used `output`.
    container = (
        (batch.get("output") or {}).get("inlinedResponses")
        or (batch.get("response") or {}).get("inlinedResponses")
        or []
    )
    entries = container.get("inlinedResponses", []) if isinstance(container, dict) else container
    images = {}
    keys = list(specs)
    for index, entry in enumerate(entries):
        key = str((entry.get("metadata") or {}).get("key") or keys[index])
        if entry.get("error"):
            raise RuntimeError(f"Image batch item {key} failed: {entry['error']}")
        parts = (((entry.get("response") or {}).get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
        data = next((part.get("inlineData", {}).get("data") for part in parts if isinstance(part, dict) and part.get("inlineData", {}).get("data")), "")
        if not data:
            raise RuntimeError(f"Image batch item {key} returned no image")
        image = ImageOps.fit(Image.open(BytesIO(b64decode(data))).convert("RGB"), (1200, 675), method=Image.Resampling.LANCZOS)
        output = BytesIO(); image.save(output, format="JPEG", quality=91, optimize=True, progressive=True)
        images[key] = output.getvalue()
    if set(images) != set(specs):
        raise RuntimeError("Image batch omitted one or more X visuals")
    return images, batch_name, model


def render_prompt(row, plan):
    hook = str(plan["hookText"]).strip()
    return f"""Create one finished 16:9 native-X editorial illustration for YAS.

POST COPY:
{row['body']}

BINDING VISUAL BRIEF:
{plan['visualBrief']}

RENDERING CONTRACT:
- The supplied reference is the real YAS logo. Use its exact geometry and colour once, naturally and prominently in the scene. Never redraw, approximate or replace it.
- Make the bespoke operational system the visual subject: show what it does, not an employee suffering from the problem.
- Keep a human visibly responsible for the final approval, exception or judgement.
- Put this exact hook once, large and high-contrast: {hook}
- That hook and the lettering already inside the logo are the only readable text allowed. No pseudo-text, labels, cards, UI, dashboards, captions, documents, statistics, numbers or tiny copy.
- The hook must stay readable at 355 px feed width. Simplify the scene rather than shrinking it.
- Build a singular, case-specific visual metaphor. No generic office photo, laptop, meeting, robot, flowchart, dashboard, three cards, before/after, blue tech glow, watermark or border.
- Premium editorial illustration, edge-to-edge 16:9 landscape.
""".strip()


def main():
    rows = wait_for_target()
    pending = [row for row in rows if not row["published_post_id"]]
    if not pending:
        print("All requested X drafts already have previews")
        return
    reference = site_logo_reference(SITE_ID)
    if not reference:
        raise RuntimeError("YAS real logo reference is required before X assets can be produced")
    planning_requests = {str(row["id"]): visual_plan_prompt(row) for row in pending}
    plans, planning_batch = _gemini_batch_text_json(planning_requests, temperature=0.25, timeout=7200)
    missing = [key for key in planning_requests if not isinstance(plans.get(key), dict) or not all(str(plans[key].get(field) or "").strip() for field in ("hookText", "visualBrief", "altText"))]
    if missing:
        raise RuntimeError(f"Visual-plan batch returned incomplete items: {', '.join(missing)}")
    specs = {str(row["id"]): {"prompt": render_prompt(row, plans[str(row["id"])])} for row in pending}
    images, image_batch, model = batch_images(specs, reference)
    created = []
    with db() as conn:
        for row in pending:
            key = str(row["id"])
            asset_key = f"x-work-{key}"
            directory = social_asset_job_dir(SITE_ID, asset_key, "twitter")
            directory.mkdir(parents=True, exist_ok=True)
            filename = "image-01.jpg"
            (directory / filename).write_bytes(images[key])
            thread_items = [part.strip() for part in str(row["body"] or "").split("\n\n") if part.strip()] if row["task_type"] == "x_thread" else [str(row["body"] or "").strip()]
            if not thread_items or any(_x_weighted_length(item) > 280 for item in thread_items):
                raise RuntimeError(f"X copy length invalid for work item {key}")
            media_url = social_asset_url(SITE_ID, asset_key, "twitter", filename)
            payload = {"source": "yas-x-batch", "twitter": {"format": "thread" if len(thread_items) > 1 else "post", "threadItems": thread_items, "mediaUrls": [media_url], "mediaMimeType": "image/jpeg", "visualHook": plans[key]["hookText"], "visualBrief": plans[key]["visualBrief"], "altText": plans[key]["altText"], "planningBatch": planning_batch, "imageBatch": image_batch, "generator": model}}
            validation = {"ok": True, "posts": [{"charCount": _x_weighted_length(item), "maxChars": 280} for item in thread_items], "batch": True}
            post_id = conn.execute("""insert into social_posts(site_id,job_id,channel,content_text,content_json,remote_url,status,asset_type,language,max_chars,char_count,include_link,validation_json,created_at,updated_at)
                values(?,?,?,?,?,'','DRAFT','x_batch_visual','en',280,?,0,?,?,?)""", (SITE_ID, row["source_job_id"], "twitter", row["body"], json.dumps(payload, ensure_ascii=False), max(item["charCount"] for item in validation["posts"]), json.dumps(validation), now_iso(), now_iso())).lastrowid
            conn.execute("update social_work_items set published_post_id=?, updated_at=? where id=?", (post_id, now_iso(), row["id"]))
            created.append(post_id)
    agent_log(SITE_ID, "INFO", "x-batch-visuals", f"Prepared {len(created)} reviewable X drafts with batch-created visuals", {"planningBatch": planning_batch, "imageBatch": image_batch, "postIds": created})
    print(json.dumps({"created": created, "planningBatch": planning_batch, "imageBatch": image_batch}, ensure_ascii=False))


if __name__ == "__main__":
    main()
