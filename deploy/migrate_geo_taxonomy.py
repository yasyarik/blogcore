#!/usr/bin/env python3
"""Move the approved GEO commercial pages into their canonical collections.

This migration updates Blog Core records and the GEO native published store in
one controlled operation. Source routes keep permanent redirects from the old
``/use-cases/<slug>/`` paths after the renderer release is deployed.
"""

import argparse
import json
import sqlite3
from pathlib import Path


TAXONOMY = {
    "ai-crawler-checker-test-whether-search-and-answer-engines-can-access-your-site": "tool",
    "llmstxt-checker-review-an-experimental-ai-discovery-file-in-context": "tool",
    "ai-search-roi-connect-visibility-evidence-to-traffic-and-conversion-measurement": "use_case",
    "ai-search-tracking-measure-mentions-citations-and-visibility-by-question": "use_case",
    "ai-visibility-audit-and-remediation-turn-evidence-into-an-ordered-fix-plan": "use_case",
    "ai-search-traffic-loss-audit-diagnose-zero-click-risk-and-recovery-options": "solution",
    "ai-seo-services-build-an-evidence-led-ai-search-visibility-program": "solution",
    "chatgpt-seo-how-to-make-your-website-easier-to-find-understand-and-cite": "solution",
    "generative-engine-optimization-build-evidence-ai-search-can-use": "solution",
    "geo-vs-seo-vs-aeo-what-changes-when-ai-answers-the-question": "solution",
    "google-ai-overviews-seo-diagnose-the-signals-your-website-controls": "solution",
}

PREFIX = {"solution": "solutions", "tool": "tools", "use_case": "use-cases"}


def target_path(content_type, slug):
    return f"/{PREFIX[content_type]}/{slug}/"


def update_store(store_root):
    published = store_root / "published"
    changed = 0
    for slug, content_type in TAXONOMY.items():
        old_path = published / f"use-cases--{slug}.json"
        new_path = published / f"{PREFIX[content_type]}--{slug}.json"
        if old_path == new_path:
            payload = json.loads(old_path.read_text(encoding="utf-8"))
            path = target_path(content_type, slug)
            if payload.get("contentType") != content_type or payload.get("targetPath") != path:
                payload["contentType"] = content_type
                payload["targetPath"] = path
                staged = new_path.with_suffix(".json.tmp")
                staged.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                staged.replace(new_path)
                changed += 1
            continue
        if new_path.exists():
            if old_path.exists():
                raise RuntimeError(f"both old and new published records exist for {slug}")
            continue
        if not old_path.exists():
            raise RuntimeError(f"missing published record for {slug}: {old_path}")
        payload = json.loads(old_path.read_text(encoding="utf-8"))
        payload["contentType"] = content_type
        payload["targetPath"] = target_path(content_type, slug)
        staged = new_path.with_suffix(".json.tmp")
        staged.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        staged.replace(new_path)
        old_path.unlink()
        changed += 1
    return changed


def update_database(db_path, site_id):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    changed = 0
    try:
        rows = conn.execute("select id, slug, sources_json from content_jobs where site_id=?", (site_id,)).fetchall()
        for row in rows:
            content_type = TAXONOMY.get(str(row["slug"] or ""))
            if not content_type:
                continue
            sources = json.loads(row["sources_json"] or "{}")
            path = target_path(content_type, row["slug"])
            if sources.get("contentType") == content_type and sources.get("targetPath") == path:
                continue
            sources["contentType"] = content_type
            sources["pageType"] = content_type
            sources["targetPath"] = path
            sources["canonicalGroup"] = path
            conn.execute(
                "update content_jobs set sources_json=?, updated_at=datetime('now') where id=? and site_id=?",
                (json.dumps(sources, ensure_ascii=False), row["id"], site_id),
            )
            conn.execute(
                "insert into content_job_logs(site_id, job_id, ts, level, step, message) values(?, ?, datetime('now'), ?, ?, ?)",
                (site_id, row["id"], "INFO", "taxonomy-migration", f"Canonical GEO collection changed to {content_type}: {path}"),
            )
            changed += 1
        conn.commit()
    finally:
        conn.close()
    return changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--store-root", required=True, type=Path)
    parser.add_argument("--site-id", type=int, default=16)
    args = parser.parse_args()
    store_changed = update_store(args.store_root)
    db_changed = update_database(args.db, args.site_id)
    print(json.dumps({"storeChanged": store_changed, "databaseChanged": db_changed, "taxonomy": TAXONOMY}, ensure_ascii=False))


if __name__ == "__main__":
    main()
