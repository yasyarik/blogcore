#!/usr/bin/env python3
"""Apply the approved first-month revision without replacing calendars or dates."""

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

try:
    from .seed_personal_brand_media_plans import BRANDS, build_items
    from .personal_brand_factory_topics import REVISION, TELEGRAM_SLOTS
    from .update_personal_brand_reels import FIELDS as REEL_FIELDS, EDITABLE
    from .personal_brand_growth import REVISION as GROWTH_REVISION
except ImportError:
    from seed_personal_brand_media_plans import BRANDS, build_items
    from personal_brand_factory_topics import REVISION, TELEGRAM_SLOTS
    from update_personal_brand_reels import FIELDS as REEL_FIELDS, EDITABLE
    from personal_brand_growth import REVISION as GROWTH_REVISION

FIELDS = REEL_FIELDS + ("kpi",)

SCHEDULE_KEYS = ("publishAt", "productionDueAt", "recordingDueAt")
OLD_SCRIPT_KEYS = ("hook", "talkingPoints", "shotList", "spokenText", "scriptRevision",
                   "durationSeconds", "recordingNote", "shootingPair", "retentionReason", "cta", "leadMagnet")
FACTORY_BINDING_KEYS = ("sourceJobId", "contentJobId", "jobId", "publicationPostIds", "publicationUrls")


def identity(row):
    detail = row.get("details") or json.loads(row.get("details_json") or "{}")
    if row["execution_mode"] == "human-owner":
        if not detail.get("reelScriptId"):
            raise ValueError("Expected an existing authored Reel slot")
        return detail["reelScriptId"]
    if detail.get("planSlotId"):
        return detail["planSlotId"]
    group = str(row.get("repurpose_group") or "")
    if not group.startswith("oct-") or not group[4:].isdigit():
        raise ValueError("Unknown legacy factory slot; refusing to infer its identity")
    return f"{row['channel']}:{int(group[4:])}"


def prepare(conn, month):
    changes, removals, reports = [], [], []
    for domain, config in BRANDS.items():
        site = conn.execute("select id from sites where domain=?", (domain,)).fetchone()
        if not site:
            raise ValueError(f"Missing site: {domain}")
        site_id = site["id"]
        rows = [dict(row) for row in conn.execute(
            "select * from agent_media_plan_items where site_id=? and json_extract(details_json,'$.planMonth')=? order by id",
            (site_id, month),
        )]
        existing = {}
        for row in rows:
            key = identity(row)
            if key in existing:
                raise ValueError(f"Duplicate slot: {domain} {key}")
            existing[key] = row
        desired = {identity(item): item for item in build_items(config, month)}
        if desired.keys() - existing.keys():
            raise ValueError(f"Missing existing slots for {domain}; no tasks will be invented")
        allowed_removals = {f"Telegram:{number}" for number in range(1, 16) if number not in TELEGRAM_SLOTS}
        extras = existing.keys() - desired.keys()
        if extras - allowed_removals:
            raise ValueError(f"Unexpected tasks in {domain}; no writes made")
        changed = skipped = 0
        removed_ids = []
        for key in sorted(extras):
            old = existing[key]
            details = json.loads(old["details_json"] or "{}")
            if old["status"].upper() not in EDITABLE or any(details.get(field) for field in FACTORY_BINDING_KEYS):
                raise ValueError("A Telegram item selected for quota reduction is no longer an untouched plan")
            if conn.execute("select id from agent_media_plan_reminder_events where media_plan_item_id=? and sent_at is not null", (old["id"],)).fetchone():
                raise ValueError("A removed Telegram plan already has a sent reminder")
            removals.append(old)
            removed_ids.append(old["id"])
        for key, item in desired.items():
            old = existing[key]
            if old["status"].upper() not in EDITABLE:
                skipped += 1
                continue
            previous = json.loads(old["details_json"] or "{}")
            if old["execution_mode"] != "human-owner" and any(previous.get(field) for field in FACTORY_BINDING_KEYS):
                raise ValueError("A factory plan already has generated/publication bindings; review it separately")
            merged = dict(previous)
            if item["execution_mode"] == "human-owner":
                for field in OLD_SCRIPT_KEYS:
                    merged.pop(field, None)
            merged.update(item["details"])
            for field in SCHEDULE_KEYS:
                if field in previous:
                    merged[field] = previous[field]
            item["details"] = merged
            if merged != previous or any(old[field] != item[field] for field in FIELDS):
                changes.append((old, item))
                changed += 1
        reports.append({"domain": domain, "siteId": site_id, "updated": changed,
                        "protectedPreserved": skipped, "removedPendingTelegramIds": removed_ids,
                        "remainingSourceItems": len(rows) - len(extras)})
    return changes, removals, reports


def update(db_path, month="2026-10", apply=False, backup_dir="/var/backups/blog-core"):
    conn = sqlite3.connect(f"file:{Path(db_path).resolve()}?mode={'rw' if apply else 'ro'}", uri=True, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("pragma foreign_keys=on")
    try:
        changes, removals, reports = prepare(conn, month)
        backup_path = None
        if apply and (changes or removals):
            backup_root = Path(backup_dir)
            backup_root.mkdir(parents=True, exist_ok=True)
            backup_path = backup_root / ("pre-personal-brand-launch-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".sqlite3")
            with sqlite3.connect(backup_path) as backup:
                conn.backup(backup)
            conn.execute("begin immediate")
            changed_ids = {old["id"] for old, _ in changes} | {old["id"] for old in removals}
            before_other = [dict(row) for row in conn.execute("select * from agent_media_plan_items order by id") if row["id"] not in changed_ids]
            for old in [row for row, _ in changes] + removals:
                current = conn.execute("select * from agent_media_plan_items where id=?", (old["id"],)).fetchone()
                if not current or dict(current) != old:
                    raise RuntimeError("A plan changed during preparation; retry against current state")
            now = datetime.now().astimezone().isoformat(timespec="seconds")
            for old, item in changes:
                assignments = ",".join(field + "=?" for field in FIELDS)
                values = [item[field] for field in FIELDS]
                conn.execute(f"update agent_media_plan_items set {assignments},details_json=?,updated_at=? where id=?",
                             (*values, json.dumps(item["details"], ensure_ascii=False), now, old["id"]))
            for old in removals:
                if conn.execute("select id from agent_media_plan_reminder_events where media_plan_item_id=? and sent_at is not null", (old["id"],)).fetchone():
                    raise RuntimeError("A reminder was sent during preparation; review the plan again")
                conn.execute("delete from agent_media_plan_reminder_events where media_plan_item_id=? and sent_at is null", (old["id"],))
                conn.execute("delete from agent_media_plan_items where id=? and site_id=?", (old["id"], old["site_id"]))
            after_other = [dict(row) for row in conn.execute("select * from agent_media_plan_items order by id") if row["id"] not in changed_ids]
            if before_other != after_other:
                raise RuntimeError("Unrelated or completed tasks changed unexpectedly")
            for old, _ in changes:
                row = conn.execute("select status,details_json from agent_media_plan_items where id=?", (old["id"],)).fetchone()
                original, updated = json.loads(old["details_json"]), json.loads(row["details_json"])
                if row["status"] != old["status"] or any(original.get(key) != updated.get(key) for key in SCHEDULE_KEYS):
                    raise RuntimeError("Schedule or status changed unexpectedly")
            conn.commit()
        return {"applied": apply, "revision": REVISION, "growthRevision": GROWTH_REVISION, "backup": str(backup_path) if backup_path else None, "sites": reports}
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
