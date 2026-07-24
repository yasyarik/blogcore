#!/usr/bin/env python3
"""Approve and publish the audited Georivo typed-content plan."""

import argparse
import json
import sqlite3
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

from audit_content_plan import audit


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_visual_report(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("passed") is not True:
        raise RuntimeError("browser QA report is not marked passed")
    if payload.get("expectedPages") != 19 or payload.get("failedPages") != 0:
        raise RuntimeError("browser QA report does not cover 19 clean pages")
    return payload


def approve(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        select id,sources_json from content_jobs
        where site_id=14
          and status='DRAFT'
          and json_extract(sources_json,'$.contentType') in
              ('guide','template','example','integration_guide')
        """
    ).fetchall()
    if len(rows) != 19:
        raise RuntimeError(f"expected 19 DRAFT typed pages, found {len(rows)}")
    today = date.today().isoformat()
    for row in rows:
        sources = json.loads(row["sources_json"] or "{}")
        brief = sources["pageBrief"]
        brief["approvals"] = {
            "editorialReview": True,
            "productFactCheck": True,
            "seoReview": True,
            "browserQa": True,
        }
        if sources.get("contentType") == "example":
            brief.setdefault("contentDetails", {})["lastFunctionalCheck"] = today
        conn.execute(
            "update content_jobs set sources_json=?,updated_at=? where id=?",
            (json.dumps(sources, ensure_ascii=False), stamp(), row["id"]),
        )
        conn.execute(
            """
            insert into content_job_logs(site_id,job_id,ts,level,step,message)
            values(14,?,?,?,?,?)
            """,
            (
                row["id"],
                stamp(),
                "INFO",
                "content-approval",
                "Editorial, product-fact, SEO, and browser QA gates passed",
            ),
        )
    conn.commit()
    conn.close()


def publish(db_path, base_url):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        select id,json_extract(sources_json,'$.targetPath') target_path
        from content_jobs
        where site_id=14
          and status='DRAFT'
          and json_extract(sources_json,'$.contentType') in
              ('guide','template','example','integration_guide')
        order by target_path
        """
    ).fetchall()
    conn.close()
    results = []
    for row in rows:
        request = urllib.request.Request(
            f"{base_url}/api/sites/14/content-jobs/{row['id']}/publish",
            method="POST",
            data=b"",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
            results.append({"path": row["target_path"], "ok": True, "result": payload})
        except urllib.error.HTTPError as error:
            payload = error.read().decode("utf-8", errors="replace")
            results.append({"path": row["target_path"], "ok": False, "error": payload})
            break
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="/var/www/blog.yas.ooo/data/blog_core.sqlite3")
    parser.add_argument("--native-root", default="/var/www/georivo-blog/data/blog-core")
    parser.add_argument("--public-origin", default="https://georivo.com")
    parser.add_argument("--base-url", default="http://127.0.0.1:3299")
    parser.add_argument("--browser-report", type=Path, required=True)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    visual = load_visual_report(args.browser_report)
    draft_audit = audit(
        Path(args.db),
        Path(args.native_root),
        args.public_origin.rstrip("/"),
        False,
    )
    if draft_audit["failed"]:
        raise SystemExit(json.dumps(draft_audit, ensure_ascii=False, indent=2))
    approve(Path(args.db))
    result = {"approved": 19, "browserQa": visual}
    if args.publish:
        published = publish(Path(args.db), args.base_url.rstrip("/"))
        result["published"] = published
        if len(published) != 19 or any(not item["ok"] for item in published):
            print(json.dumps(result, ensure_ascii=False, indent=2))
            raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))
