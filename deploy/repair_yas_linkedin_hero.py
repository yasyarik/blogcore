#!/usr/bin/env python3
"""Generate a dedicated reviewed hero for the deleted YAS LinkedIn post."""
from __future__ import annotations

import argparse
import json

from app import (
    db,
    generate_linkedin_hero_image,
    get_site,
    now_iso,
    parse_json_object,
    social_asset_key,
)


SITE_ID = 12
SOCIAL_POST_ID = 209
JOB_ID = "1e5f336e36e3cdff96c3a4d0"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    site = get_site(SITE_ID)
    with db() as conn:
        post = conn.execute("select * from social_posts where id=? and site_id=?", (SOCIAL_POST_ID, SITE_ID)).fetchone()
        job = conn.execute("select * from content_jobs where id=? and site_id=?", (JOB_ID, SITE_ID)).fetchone()
    if not site or not post or not job or post["job_id"] != JOB_ID or post["channel"] != "linkedin":
        raise SystemExit("The exact YAS LinkedIn repair target is missing or changed")
    payload = parse_json_object(post["content_json"])
    existing = payload.get("linkedin") if isinstance(payload.get("linkedin"), dict) else {}
    plan = {
        "apply": args.apply,
        "socialPostId": SOCIAL_POST_ID,
        "jobId": JOB_ID,
        "title": job["title"],
        "fromStatus": post["status"],
        "hadDedicatedHero": bool(existing.get("mediaUrl")),
    }
    if not args.apply:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return

    asset_key = social_asset_key(f"{JOB_ID}-linkedin-repair")
    linkedin = generate_linkedin_hero_image(
        SITE_ID,
        JOB_ID,
        site,
        job,
        post["content_text"] or "",
        asset_key=asset_key,
    )
    payload["assetKey"] = asset_key
    payload["linkedin"] = linkedin
    payload["returnedToDraftAt"] = now_iso()
    payload["repairReason"] = "Replaced the legacy article-hero fallback with a dedicated LinkedIn magazine cover after the external post was deleted by the owner."
    timestamp = now_iso()
    with db() as conn:
        conn.execute(
            """update social_posts set content_json=?,remote_url='',status='DRAFT',scheduled_for=null,updated_at=?
               where id=? and site_id=?""",
            (json.dumps(payload, ensure_ascii=False), timestamp, SOCIAL_POST_ID, SITE_ID),
        )
        conn.execute(
            """update content_jobs set linkedin_status='drafted',linkedin_post_url='',linkedin_posted_at=null,updated_at=?
               where id=? and site_id=?""",
            (timestamp, JOB_ID, SITE_ID),
        )
        conn.execute(
            "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
            (SITE_ID, JOB_ID, timestamp, "INFO", "linkedin-hero-repair", f"Generated a dedicated unpublished LinkedIn hero for deleted social post {SOCIAL_POST_ID}; article-hero fallback removed."),
        )
    print(json.dumps({**plan, "status": "DRAFT", "linkedin": linkedin}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
