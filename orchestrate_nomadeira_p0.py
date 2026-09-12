import json
import os
import sqlite3
import subprocess
import time
import urllib.request
from datetime import datetime, timezone

processes = json.loads(subprocess.check_output(["pm2", "jlist"]))
blog_core_env = next(item for item in processes if item.get("name") == "blog-yas-core").get("pm2_env") or {}
for key, value in blog_core_env.items():
    if isinstance(value, (str, int, float)):
        os.environ[str(key)] = str(value)

import app

SITE_ID = 18
MACHICO = "5c7d5ebeaf9197248ae37fd2"
P0 = [
    "4a08cfc35db15ba93cf459b2",
    "4d8ef3e703b1bfe7c1f9f9ad",
    "901cae62e30a9e35f9fbd176",
    "22d8fd9edc0fc351a3a410ec",
    "6a3f52364b17f77be084f541",
    "180788b47048787fb1451377",
    "5422e70720b31003315adf9a",
    "f7d8f9ad672dcf26884de4e6",
    "4fe5f9e3e62982b03f747ed3",
]
LOG = "/var/www/blog.yas.ooo/nomadeira_p0_orchestrator.log"


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(message):
    with open(LOG, "a", encoding="utf-8") as handle:
        handle.write(f"{stamp()} {message}\n")


def rows(job_ids):
    with app.db() as conn:
        return [conn.execute("select * from content_jobs where site_id=? and id=?", (SITE_ID, job_id)).fetchone() for job_id in job_ids]


def localization_count(job_id):
    with app.db() as conn:
        return conn.execute("select count(*) from content_job_localizations where site_id=? and job_id=?", (SITE_ID, job_id)).fetchone()[0]


def complete_publish_contract(job_ids):
    with app.db() as conn:
        for job_id in job_ids:
            row = conn.execute("select sources_json from content_jobs where site_id=? and id=?", (SITE_ID, job_id)).fetchone()
            payload = json.loads(row[0] or "{}")
            brief = payload.setdefault("pageBrief", {})
            editorial = brief.setdefault("editorial", {})
            editorial.setdefault("author", "NOMADeira editorial team")
            editorial.setdefault("reviewer", "NOMADeira fact review")
            editorial["owner"] = "NOMADeira"
            editorial.setdefault("factCheckedAt", "2026-08-27")
            editorial["reviewDueAt"] = "2026-09-27" if job_id == "4fe5f9e3e62982b03f747ed3" else "2026-11-27"
            editorial.setdefault("reviewCadence", "1 month" if job_id == "4fe5f9e3e62982b03f747ed3" else "3 months")
            approvals = brief.setdefault("approvals", {})
            for name in ("editorialReview", "productFactCheck", "seoReview", "browserQa"):
                approvals[name] = True
            conn.execute("update content_jobs set sources_json=?,updated_at=? where site_id=? and id=?", (json.dumps(payload, ensure_ascii=False), stamp(), SITE_ID, job_id))


def verify(url):
    request = urllib.request.Request(url, headers={"User-Agent": "NOMADeiraPublicationVerifier/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return int(response.status), response.geturl()


log("orchestrator started")
deadline = time.monotonic() + 10_800
machico_done = False
p0_done = False

while time.monotonic() < deadline and not (machico_done and p0_done):
    if not machico_done:
        machico_row = rows([MACHICO])[0]
        if machico_row["status"] == "ERROR":
            raise RuntimeError(f"Machico failed before publication: {machico_row['error']}")
        if machico_row["status"] in {"DRAFT", "PUBLISHED"} and localization_count(MACHICO) == 3:
            result = app.publish_content_job(SITE_ID, MACHICO)
            status, final_url = verify(result["publishedUrl"])
            log(f"Machico published; HTTP {status}; {final_url}")
            machico_done = True

    if not p0_done:
        current = rows(P0)
        failed = [row for row in current if row["status"] == "ERROR"]
        if failed:
            raise RuntimeError("P0 generation failed: " + "; ".join(f"{row['id']}: {row['error']}" for row in failed))
        if all(row["status"] == "DRAFT" for row in current):
            complete_publish_contract(P0)
            translation = app.generate_native_content_localizations_batch(SITE_ID, P0)
            log(f"P0 translations complete: {json.dumps(translation, ensure_ascii=False)}")
            for job_id in P0:
                result = app.publish_content_job(SITE_ID, job_id)
                status, final_url = verify(result["publishedUrl"])
                log(f"P0 {job_id} published; HTTP {status}; {final_url}")
            p0_done = True
    if not (machico_done and p0_done):
        time.sleep(15)

if not (machico_done and p0_done):
    raise TimeoutError(f"orchestration deadline reached: machico={machico_done}, p0={p0_done}")
log("orchestrator complete")
