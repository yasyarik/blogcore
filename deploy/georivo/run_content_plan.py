#!/usr/bin/env python3
"""Generate pending Georivo typed-content jobs sequentially through Blog Core."""

import argparse
import concurrent.futures
import json
import sqlite3
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_jobs(db_path, site_id):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        select id,topic,status,json_extract(sources_json,'$.targetPath') target_path
        from content_jobs
        where site_id=?
          and json_extract(sources_json,'$.contentType') in
              ('guide','template','example','integration_guide')
        order by created_at,id
        """,
        (site_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def status(db_path, job_id):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "select status,error,updated_at from content_jobs where id=?",
        (job_id,),
    ).fetchone()
    locale_count = conn.execute(
        "select count(*) from content_job_localizations where job_id=?",
        (job_id,),
    ).fetchone()[0]
    conn.close()
    return dict(row) | {"localeCount": locale_count}


def start(base_url, site_id, job_id):
    request = urllib.request.Request(
        f"{base_url}/api/sites/{site_id}/content-jobs/{job_id}/generate",
        method="POST",
        data=b"",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def run_one(db_path, site_id, base_url, timeout_minutes, job, index, total):
    print(
        f"{stamp()} START {index}/{total} {job['id']} {job['target_path']}",
        flush=True,
    )
    try:
        code, payload = start(base_url, site_id, job["id"])
        print(f"{stamp()} API {code} {json.dumps(payload)}", flush=True)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"{stamp()} API_ERROR {job['id']} {error}", flush=True)
        return
    deadline = time.time() + timeout_minutes * 60
    while time.time() < deadline:
        current = status(db_path, job["id"])
        print(
            f"{stamp()} POLL {job['id']} {current['status']} locales={current['localeCount']}",
            flush=True,
        )
        if current["status"] != "GENERATING":
            break
        time.sleep(15)
    else:
        print(f"{stamp()} TIMEOUT {job['id']}", flush=True)
        return
    if current["status"] == "DRAFT" and current["localeCount"] == 4:
        print(f"{stamp()} READY {job['id']} {job['target_path']}", flush=True)
    else:
        print(
            f"{stamp()} FAILED {job['id']} status={current['status']} error={current['error']}",
            flush=True,
        )


def run(db_path, site_id, base_url, timeout_minutes, workers):
    jobs = load_jobs(db_path, site_id)
    pending = [job for job in jobs if job["status"] not in {"DRAFT", "PUBLISHED"}]
    print(f"{stamp()} typed={len(jobs)} pending={len(pending)} workers={workers}", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                run_one,
                db_path,
                site_id,
                base_url,
                timeout_minutes,
                job,
                index,
                len(pending),
            )
            for index, job in enumerate(pending, 1)
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as error:
                print(f"{stamp()} WORKER_ERROR {error}", flush=True)
    summary = {}
    for job in load_jobs(db_path, site_id):
        summary[job["status"]] = summary.get(job["status"], 0) + 1
    print(f"{stamp()} COMPLETE {json.dumps(summary, sort_keys=True)}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="/var/www/blog.yas.ooo/data/blog_core.sqlite3")
    parser.add_argument("--site-id", type=int, default=14)
    parser.add_argument("--base-url", default="http://127.0.0.1:3299")
    parser.add_argument("--timeout-minutes", type=int, default=45)
    parser.add_argument("--workers", type=int, default=1, choices=(1, 2, 3))
    args = parser.parse_args()
    run(Path(args.db), args.site_id, args.base_url.rstrip("/"), args.timeout_minutes, args.workers)
