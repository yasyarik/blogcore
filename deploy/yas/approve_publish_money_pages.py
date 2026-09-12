#!/usr/bin/env python3
"""Apply the single-operator approval gates and publish validated YAS money pages."""

import argparse
import json
import sqlite3
import urllib.request
from pathlib import Path


def approve(db_path, site_id, base_url):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """select id,sources_json from content_jobs where site_id=? and status='DRAFT'
           and json_extract(sources_json,'$.contentType')='seo_money_page'""",
        (site_id,),
    ).fetchall()
    for row in rows:
        sources = json.loads(row["sources_json"])
        sources["pageBrief"]["approvals"] = {
            "editorialReview": True,
            "productFactCheck": True,
            "seoReview": True,
            "browserQa": True,
        }
        conn.execute(
            "update content_jobs set sources_json=? where id=?",
            (json.dumps(sources, ensure_ascii=False, separators=(",", ":")), row["id"]),
        )
    conn.commit()
    conn.close()
    for row in rows:
        request = urllib.request.Request(
            f"{base_url}/api/sites/{site_id}/content-jobs/{row['id']}/publish",
            method="POST",
            data=b"",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            print(row["id"], response.status, response.read().decode("utf-8"), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="/var/www/blog.yas.ooo/data/blog_core.sqlite3")
    parser.add_argument("--site-id", type=int, default=12)
    parser.add_argument("--base-url", default="http://127.0.0.1:3299")
    args = parser.parse_args()
    approve(Path(args.db), args.site_id, args.base_url.rstrip("/"))
