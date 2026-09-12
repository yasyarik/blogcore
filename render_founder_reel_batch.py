#!/usr/bin/env python3
"""Render all prepared founder-Reel plans and place completed videos in the IG queue."""
from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import app

SITE_ID = 12
ROOT = Path("/var/www/blog.yas.ooo")
PLAN_DIR = ROOT / "data/founder_reel_scenarios"
PUBLIC_ROOT = ROOT / "data/social_assets/12"
PORTRAIT = ROOT / "yas-portrait-poster.webp"
GENERATOR = ROOT / "generate_yas_founder_reel_omni.py"


def existing_for_source(source_post_id: int) -> bool:
    with app.db() as conn:
        rows = conn.execute(
            """select content_json from social_posts
               where site_id=? and channel='instagram' and asset_type='instagram_reel'
                 and status not in ('ERROR','SUPERSEDED','CANCELLED')""",
            (SITE_ID,),
        ).fetchall()
    for row in rows:
        payload = app.parse_json_object(row["content_json"])
        if int(payload.get("sourceVacancyPostId") or 0) == source_post_id:
            return True
    return False


def queue_rendered(plan: dict, output: Path) -> int:
    source_id = int(plan["sourcePostId"])
    asset_key = f"yas-founder-vacancy-{source_id}"
    target_dir = PUBLIC_ROOT / asset_key / "instagram"
    target_dir.mkdir(parents=True, exist_ok=True)
    video_name = f"{asset_key}.mp4"
    cover_name = f"{asset_key}-start.jpg"
    shutil.copy2(output, target_dir / video_name)
    shutil.copy2(output.with_name(f"{output.stem}-start.jpg"), target_dir / cover_name)
    video_url = f"/sites/12/social-assets/{asset_key}/instagram/{video_name}"
    cover_url = f"/sites/12/social-assets/{asset_key}/instagram/{cover_name}"
    payload = {
        "source": "yas-founder-reel-batch",
        "sourceVacancyPostId": source_id,
        "channel": "instagram",
        "assetType": "instagram_reel",
        "language": "en",
        "assetKey": asset_key,
        "instagramReel": {
            "version": "founder-omni-batch-v1",
            "videoUrl": video_url,
            "coverUrl": cover_url,
            "durationSeconds": 30,
            "sourcePortraitMode": "portrait_used_only_for_boundary_frame_generation",
            "omniInputMode": "generated_boundary_frames_only",
            "nativeComposition": True,
            "engagementAction": plan["engagementAction"],
            "scenarioTitle": plan["title"],
            "progress": {"phase": "render_complete", "scene": 3, "totalScenes": 3, "message": "Founder-led Omni Reel ready for Instagram publication queue"},
        },
        "validation": {"ok": True, "renderVerified": True, "publicationState": "queued"},
    }
    caption = str(plan["caption"] or "").strip()
    now = app.now_iso()
    with app.db() as conn:
        cursor = conn.execute(
            """insert into social_posts(site_id,job_id,channel,content_text,content_json,remote_url,status,asset_type,language,max_chars,char_count,include_link,validation_json,created_at,updated_at)
               values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (SITE_ID, plan["jobId"], "instagram", caption, json.dumps(payload, ensure_ascii=False), "", "DRAFT", "instagram_reel", "en", 2200, len(caption), 0, json.dumps(payload["validation"]), now, now),
        )
    return int(cursor.lastrowid)


def main() -> None:
    plans = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(PLAN_DIR.glob("*.json"), key=lambda p: int(p.stem))]
    results = []
    for position, plan in enumerate(plans, 1):
        source_id = int(plan["sourcePostId"])
        if existing_for_source(source_id):
            results.append({"sourcePostId": source_id, "status": "skipped_existing"})
            continue
        output = ROOT / "output" / f"yas-founder-vacancy-{source_id}-v1.mp4"
        environment = os.environ.copy()
        environment.update({
            "FOUNDER_PORTRAIT": str(PORTRAIT),
            "FOUNDER_REEL_PLAN": str(PLAN_DIR / f"{source_id}.json"),
            "FOUNDER_REEL_OUT": str(output),
        })
        try:
            subprocess.run([sys.executable, str(GENERATOR)], cwd=ROOT, env=environment, check=True, timeout=5400)
            post_id = queue_rendered(plan, output)
            results.append({"sourcePostId": source_id, "postId": post_id, "status": "queued"})
        except Exception as error:
            results.append({"sourcePostId": source_id, "status": "error", "error": str(error)[:1000]})
        print(json.dumps({"position": position, "total": len(plans), "latest": results[-1]}, ensure_ascii=False), flush=True)
    print(json.dumps({"ok": True, "results": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
