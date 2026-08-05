#!/usr/bin/env python3
"""Publish the reviewed GEO collection-completion drafts with explicit approval."""

import argparse
import json
import sys
from pathlib import Path


SITE_ID = 16
JOB_IDS = (
    "aa4b9ceb1afff62bfa57acc4",
    "de4933fe0b023e5f50b9cb97",
    "529d17b82c89e67792d3c795",
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-root", default="/var/www/blog.yas.ooo", type=Path)
    parser.add_argument("--approve", action="store_true", help="record review gates and publish the three approved drafts")
    args = parser.parse_args()
    if not args.approve:
        raise SystemExit("Refusing to publish without --approve")

    sys.path.insert(0, str(args.app_root))
    import app  # pylint: disable=import-outside-toplevel

    with app.db() as conn:
        rows = conn.execute(
            f"select * from content_jobs where site_id=? and id in ({','.join('?' for _ in JOB_IDS)})",
            (SITE_ID, *JOB_IDS),
        ).fetchall()
        if len(rows) != len(JOB_IDS):
            raise SystemExit("The approved GEO collection jobs are incomplete")
        by_id = {row["id"]: row for row in rows}
        for job_id in JOB_IDS:
            row = by_id[job_id]
            if row["status"] != "DRAFT":
                raise SystemExit(f"{job_id} must be DRAFT before approval, got {row['status']}")
            sources = app.content_job_sources(row)
            generated = sources.get("generatedContentContract")
            if not isinstance(generated, dict):
                raise SystemExit(f"{job_id} has no generated content contract")
            brief = sources.get("pageBrief") if isinstance(sources.get("pageBrief"), dict) else {}
            approvals = brief.get("approvals") if isinstance(brief.get("approvals"), dict) else {}
            approvals.update({
                "editorialReview": True,
                "productFactCheck": True,
                "seoReview": True,
                "browserQa": True,
            })
            brief["approvals"] = approvals
            sources["pageBrief"] = brief
            conn.execute(
                "update content_jobs set sources_json=?, updated_at=? where site_id=? and id=?",
                (json.dumps(sources, ensure_ascii=False), app.now_iso(), SITE_ID, job_id),
            )
            conn.execute(
                "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
                (SITE_ID, job_id, app.now_iso(), "INFO", "approval", "Editorial, product, SEO, and browser QA gates recorded after draft review"),
            )

    results = [app.publish_content_job(SITE_ID, job_id) for job_id in JOB_IDS]
    print(json.dumps({"published": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
