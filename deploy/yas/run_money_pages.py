#!/usr/bin/env python3
"""Generate pending YAS money pages sequentially through Blog Core."""

import argparse
import concurrent.futures
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


def run_one(db_path, site_id, base_url, job):
    current = state(db_path, job["id"])
    if current["status"] in {"DRAFT", "PUBLISHED", "GENERATING"}:
        print(f"SKIP {job['target_path']} {current['status']}", flush=True)
        return
    try:
        request = urllib.request.Request(
            f"{base_url}/api/sites/{site_id}/content-jobs/{job['id']}/generate",
            method="POST",
            data=b"",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"START {job['target_path']} {response.status}", flush=True)
        deadline = time.time() + 2700
        while time.time() < deadline:
            current = state(db_path, job["id"])
            print(f"POLL {job['target_path']} {json.dumps(current)}", flush=True)
            if current["status"] != "GENERATING":
                break
            time.sleep(15)
        if current["status"] != "DRAFT" or current["locales"] != 2:
            raise SystemExit(f"Generation failed for {job['target_path']}: {current}")
    except Exception as error:
        raise RuntimeError(f"{job['target_path']}: {error}") from error


def run(db_path, site_id, base_url, workers):
    pending = jobs(db_path, site_id)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(run_one, db_path, site_id, base_url, job) for job in pending]
        for future in concurrent.futures.as_completed(futures):
            future.result()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="/var/www/blog.yas.ooo/data/blog_core.sqlite3")
    parser.add_argument("--site-id", type=int, default=12)
    parser.add_argument("--base-url", default="http://127.0.0.1:3299")
    parser.add_argument("--workers", type=int, default=2, choices=(1, 2, 3))
    args = parser.parse_args()
    run(Path(args.db), args.site_id, args.base_url.rstrip("/"), args.workers)
