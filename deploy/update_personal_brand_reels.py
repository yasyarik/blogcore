#!/usr/bin/env python3
"""Replace only pending owner Reels; retain factory work, row IDs and shifted dates."""

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path

try:
    from .personal_brand_reels import REVISION, WARSAW, build_owner_reels
    from .seed_personal_brand_media_plans import BRANDS
except ImportError:
    from personal_brand_reels import REVISION, WARSAW, build_owner_reels
    from seed_personal_brand_media_plans import BRANDS

FIELDS = ("week", "channel", "format", "title", "objective", "funnel_stage", "cta",
          "generator", "execution_mode", "repurpose_group", "rationale")
EDITABLE = {"AWAITING_RECORDING", "PLANNED", "PROPOSED", "PROPOSED_NEW"}


def factory_fingerprint(conn, site_id):
    rows = conn.execute(
        "select * from agent_media_plan_items where site_id=? and execution_mode!='human-owner' order by id",
        (site_id,),
    ).fetchall()
    return hashlib.sha256(json.dumps([dict(row) for row in rows], sort_keys=True).encode()).hexdigest()


def update(db_path, month="2026-10", apply=False, backup_dir="/var/backups/blog-core"):
    conn = sqlite3.connect(f"file:{Path(db_path).resolve()}?mode={'rw' if apply else 'ro'}", uri=True, timeout=30)
    conn.row_factory = sqlite3.Row
    now = datetime.now(WARSAW).isoformat(timespec="seconds")
    changes, report = [], []
    try:
        for domain, config in BRANDS.items():
            site = conn.execute("select id from sites where domain=?", (domain,)).fetchone()
            if not site:
                raise ValueError(f"Site missing: {domain}")
            site_id = site["id"]
            rows = conn.execute(
                """select * from agent_media_plan_items where site_id=? and execution_mode='human-owner'
                   and json_extract(details_json,'$.planMonth')=? order by json_extract(details_json,'$.publishAt'),id""",
                (site_id, month),
            ).fetchall()
            existing, legacy = {}, []
            for row in rows:
                detail = json.loads(row["details_json"] or "{}")
                script_id = detail.get("reelScriptId")
                if script_id:
                    if script_id in existing:
                        raise ValueError(f"Duplicate script ID: {script_id}")
                    existing[script_id] = row
                else:
                    legacy.append(row)
            if legacy and (len(legacy) != 30 or existing):
                raise ValueError(f"Unexpected legacy owner batch for {domain}; no writes made")
            authored = build_owner_reels(config["owner"], config["campaigns"], month)
            if legacy:
                for item, row in zip([item for item in authored if item["details"]["reelLane"] == "main"], legacy):
                    existing[item["details"]["reelScriptId"]] = row
            if not rows:
                raise ValueError("Expected existing 30-day owner calendar; no schedule inferred")
            mains = {}
            for item in authored:
                detail = item["details"]
                if detail["reelLane"] == "main":
                    source = existing.get(detail["reelScriptId"])
                    if not source:
                        raise ValueError("Missing anchor main Reel; no schedule inferred")
                    mains[detail["reelScriptId"].rsplit("-", 1)[-1]] = json.loads(source["details_json"])
            creates = edits = skipped = 0
            before = factory_fingerprint(conn, site_id)
            for item in authored:
                detail = item["details"]
                old = existing.get(detail["reelScriptId"])
                if old and old["status"].upper() not in EDITABLE:
                    skipped += 1
                    continue
                anchor = mains[detail["reelScriptId"].rsplit("-", 1)[-1]]
                if old:
                    previous = json.loads(old["details_json"] or "{}")
                    if detail.get("briefStyle") == "topic-direction":
                        for key in ("hook", "talkingPoints", "shotList", "spokenText", "scriptRevision",
                                    "durationSeconds", "recordingNote", "shootingPair", "retentionReason", "cta", "leadMagnet"):
                            previous.pop(key, None)
                    merged = {**previous, **detail}
                    for key in ("publishAt", "recordingDueAt", "productionDueAt"):
                        if previous.get(key):
                            merged[key] = previous[key]
                    item["details"] = merged
                    edits += 1
                else:
                    scheduled = datetime.fromisoformat(anchor["publishAt"]).astimezone(WARSAW)
                    detail["publishAt"] = scheduled.replace(hour=12, minute=30).isoformat(timespec="minutes")
                    for key in ("recordingDueAt", "productionDueAt"):
                        if anchor.get(key):
                            detail[key] = anchor[key]
                    creates += 1
                changes.append((site_id, item, old))
            report.append({"domain": domain, "siteId": site_id, "updated": edits, "added": creates,
                           "completedPreserved": skipped, "factoryFingerprint": before})
        if apply:
            # A SQLite online backup is safe while the app is running.
            backup_root = Path(backup_dir)
            backup_root.mkdir(parents=True, exist_ok=True)
            backup_path = backup_root / ("pre-owner-reels-" + datetime.now(WARSAW).strftime("%Y%m%d-%H%M%S-%f") + ".sqlite3")
            backup = sqlite3.connect(backup_path)
            try:
                conn.backup(backup)
            finally:
                backup.close()
            conn.execute("begin immediate")
            for site_id, item, old in changes:
                values = [item[field] for field in FIELDS]
                encoded = json.dumps(item["details"], ensure_ascii=False)
                if old:
                    current = conn.execute("select status,updated_at from agent_media_plan_items where id=?", (old["id"],)).fetchone()
                    if not current or current["status"] != old["status"] or current["updated_at"] != old["updated_at"]:
                        raise RuntimeError("An owner task changed during preparation; retry against its current state")
                    assignments = ",".join(field + "=?" for field in FIELDS)
                    conn.execute(f"update agent_media_plan_items set {assignments},details_json=?,updated_at=? where id=? and site_id=?",
                                 (*values, encoded, now, old["id"], site_id))
                else:
                    version = conn.execute("select strategy_version from agent_strategy_profiles where site_id=?", (site_id,)).fetchone()
                    conn.execute(
                        f"insert into agent_media_plan_items(site_id,strategy_version,{','.join(FIELDS)},status,details_json,created_at,updated_at,kpi) values({','.join('?' for _ in range(len(FIELDS)+7))})",
                        (site_id, version[0] if version else 0, *values, item["status"], encoded, now, now,
                         "Удержание, пересылки, содержательные комментарии и запросы материала"),
                    )
            for item in report:
                if factory_fingerprint(conn, item["siteId"]) != item["factoryFingerprint"]:
                    raise RuntimeError("Factory tasks changed unexpectedly; rolling back")
            conn.commit()
        return {"applied": apply, "revision": REVISION, "sites": report}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--month", default="2026-10")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--backup-dir", default="/var/backups/blog-core")
    args = parser.parse_args()
    print(json.dumps(update(args.db, args.month, args.apply, args.backup_dir), ensure_ascii=False, indent=2))
