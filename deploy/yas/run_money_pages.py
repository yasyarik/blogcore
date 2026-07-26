#!/usr/bin/env python3
"""Generate pending YAS money pages sequentially through Blog Core."""

import argparse
import json
import sqlite3
import time
import urllib.request
from pathlib import Path


def jobs(db_path, site_id):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """select id,topic,status,json_extract(sources_json,'$.targetPath') target_path
           from content_jobs where site_id=? and
           json_extract(sources_json,'$.contentType')='seo_money_page'
           order by json_extract(sources_json,'$.targetPath')""",
        (site_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def state(db_path, job_id):
    conn = sqlite3.connect(db_path)
    row = conn.execute("select status,error from content_jobs where id=?", (job_id,)).fetchone()
    locales = conn.execute("select count(*) from content_job_localizations where job_id=?", (job_id,)).fetchone()[0]
    conn.close()
    return {"status": row[0], "error": row[1], "locales": locales}


def run(db_path, site_id, base_url):
    for index, job in enumerate(jobs(db_path, site_id), 1):
        if job["status"] in {"DRAFT", "PUBLISHED"}:
            print(f"SKIP {index} {job['target_path']} {job['status']}", flush=True)
            continue
        request = urllib.request.Request(
            f"{base_url}/api/sites/{site_id}/content-jobs/{job['id']}/generate",
            method="POST",
            data=b"",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"START {index} {job['target_path']} {response.status}", flush=True)
        deadline = time.time() + 2700
        while time.time() < deadline:
            current = state(db_path, job["id"])
            print(f"POLL {job['target_path']} {json.dumps(current)}", flush=True)
            if current["status"] != "GENERATING":
                break
            time.sleep(15)
        if current["status"] != "DRAFT" or current["locales"] != 2:
            raise SystemExit(f"Generation failed for {job['target_path']}: {current}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="/var/www/blog.yas.ooo/data/blog_core.sqlite3")
    parser.add_argument("--site-id", type=int, default=12)
    parser.add_argument("--base-url", default="http://127.0.0.1:3299")
    args = parser.parse_args()
    run(Path(args.db), args.site_id, args.base_url.rstrip("/"))
