"""Read-only content checks and isolated migration regression tests."""

import json
import sqlite3
import tempfile
import unittest
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from deploy.seed_personal_brand_media_plans import BRANDS, build_items
from deploy.update_personal_brand_launch_plan import update, identity, SCHEDULE_KEYS
from deploy.update_personal_brand_reels import FIELDS
from deploy.personal_brand_growth import FOLLOW_TOPICS, growth_brief
from media_plan_growth import render_growth_strategy, render_growth_brief


class LaunchPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "plan.sqlite3"
        self.conn = sqlite3.connect(self.db)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
          create table sites(id integer primary key,domain text);
          create table agent_media_plan_items(id integer primary key,site_id integer,strategy_version integer,
            week integer,channel text,format text,title text,objective text,funnel_stage text,cta text,
            generator text,execution_mode text,repurpose_group text,rationale text,status text,details_json text,
            created_at text,updated_at text,kpi text);
          create table agent_media_plan_reminder_events(id integer primary key,media_plan_item_id integer,sent_at text);
        """)
        for site_id, (domain, config) in zip((17, 19), BRANDS.items()):
            self.conn.execute("insert into sites values(?,?)", (site_id, domain))
            items = build_items(config)
            for item in items:
                detail = item["details"]
                detail["customUnrelatedField"] = "retain"
                for key in SCHEDULE_KEYS:
                    if key in detail:
                        detail[key] = (datetime.fromisoformat(detail[key]) + timedelta(days=37)).isoformat()
                if item["execution_mode"] == "human-owner":
                    for key in ("briefStyle", "briefRevision", "rubricKey", "focusPoints", "contentPhase"):
                        detail.pop(key, None)
                    detail.update(scriptRevision="old", spokenText="old literal speech", shootingPair="old", hook="old hook")
                else:
                    slot = int(detail.pop("planSlotId").rsplit(":", 1)[1])
                    item["repurpose_group"] = f"oct-{slot}"
                self.insert(site_id, item)
            base = next(item for item in items if item["channel"] == "Telegram")
            for slot in range(2, 15, 2):
                extra = json.loads(json.dumps(base))
                extra["repurpose_group"] = f"oct-{slot}"
                self.insert(site_id, extra)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def insert(self, site_id, item):
        self.conn.execute(
            f"insert into agent_media_plan_items(site_id,strategy_version,{','.join(FIELDS)},status,details_json,created_at,updated_at,kpi) values({','.join('?' for _ in range(len(FIELDS)+7))})",
            (site_id, 1, *(item[key] for key in FIELDS), item["status"], json.dumps(item["details"], ensure_ascii=False), "created", "updated", "retain KPI"),
        )

    def snapshot(self):
        return {row["id"]: dict(row) for row in self.conn.execute("select * from agent_media_plan_items order by id")}

    def test_content_contract(self):
        for config in BRANDS.values():
            items = build_items(config)
            reels = sorted((x for x in items if x["execution_mode"] == "human-owner"), key=lambda x: x["details"]["publishAt"])
            self.assertEqual(Counter(x["details"]["rubricKey"] for x in reels),
                             {"lifestyle": 10, "review": 12, "developer": 8, "lifehack": 8, "attention": 8, "comparison": 8, "backstage": 6})
            self.assertTrue(all(a["details"]["rubricKey"] != b["details"]["rubricKey"] for a, b in zip(reels, reels[1:])))
            self.assertTrue(all("stories" not in x["channel"].lower() for x in items))
            self.assertEqual(len({identity(x) for x in items}), 113)
            days = [datetime.fromisoformat(x["details"]["publishAt"]).day for x in items if x["channel"] == "Telegram"]
            self.assertEqual(days, [1, 5, 9, 13, 17, 21, 25, 29])

    def test_growth_contract_and_natural_briefs(self):
        for config in BRANDS.values():
            items = build_items(config)
            self.assertEqual(sum("growthPlan" in item["details"] for item in items), 1)
            reels = [item for item in items if item["execution_mode"] == "human-owner"]
            self.assertEqual(len({item["details"]["attentionAngle"] for item in reels}), 60)
            for item in items:
                detail = item["details"]
                growth = detail["growth"]
                self.assertEqual(growth["measurementState"], "awaiting_actual_publication_data")
                self.assertEqual(item["kpi"], growth["primarySignal"])
                self.assertNotIn("spokenText", detail)
                if item in reels:
                    self.assertGreater(len(detail["attentionAngle"]), 110)
                    self.assertNotIn("Начать с приятного живого момента", detail["attentionAngle"])
                    if item["title"] in FOLLOW_TOPICS:
                        self.assertIn("Предложить подписаться", detail["engagementDirection"])
                    if detail.get("leadMagnet"):
                        self.assertIn("написать в комментариях слово", detail["engagementDirection"])
                if item["channel"] == "Instagram + TikTok":
                    self.assertIn("?", detail["storyboard"][0]["onScreenText"])

    def test_commercial_topics_stay_distinct(self):
        for title in ("Коммерция", "Рабочий разбор коммерческого запроса", "Локация коммерческого помещения глазами клиента"):
            self.assertEqual(growth_brief("Вероника", title, "review")["audienceKey"], "commercial")
        self.assertEqual(growth_brief("Вероника", "Вилла для отпуска", "review")["audienceKey"], "villa")
        self.assertEqual(growth_brief("Алексей", "Покупка для аренды", "attention")["audienceKey"], "investment")

    def test_strategy_dates_follow_actual_start_and_html_is_escaped(self):
        items = build_items(next(iter(BRANDS.values())))
        strategy = next(x["details"]["growthPlan"] for x in items if "growthPlan" in x["details"])
        initial = datetime(2026, 10, 1).date()
        html = render_growth_strategy(strategy, initial, set())
        self.assertIn("07.10.2026", html)
        self.assertIn("30.10.2026", html)
        self.assertIn("ещё не подключены", html)
        shifted = render_growth_strategy(strategy, initial + timedelta(days=37), {"instagram"})
        self.assertIn("13.11.2026", shifted)
        self.assertIn("06.12.2026", shifted)
        self.assertNotIn("ещё не подключены", shifted)
        self.assertIn("не автоматически запущенные отчёты", shifted)
        self.assertEqual(render_growth_strategy(None, initial, set()), "")
        self.assertEqual(render_growth_brief(None), "")
        self.assertNotIn("<script>", render_growth_brief({"revision": "test", "audience": "<script>alert(1)</script>"}))

    def test_generated_factory_content_is_protected(self):
        first = self.conn.execute("select id,details_json from agent_media_plan_items where channel='Threads' limit 1").fetchone()
        detail = json.loads(first["details_json"])
        detail["publicationPostIds"] = {"threads": 123}
        self.conn.execute("update agent_media_plan_items set details_json=? where id=?", (json.dumps(detail), first["id"]))
        self.conn.commit()
        before = self.snapshot()
        with self.assertRaises(ValueError):
            update(self.db, apply=True, backup_dir=self.temp.name)
        self.assertEqual(before, self.snapshot())

    def test_dry_run_and_safe_idempotent_migration(self):
        before = self.snapshot()
        dry = update(self.db)
        self.assertEqual(before, self.snapshot())
        self.assertTrue(all(len(x["removedPendingTelegramIds"]) == 7 for x in dry["sites"]))
        applied = update(self.db, apply=True, backup_dir=self.temp.name)
        after = self.snapshot()
        self.assertEqual(len(after), 226)
        with sqlite3.connect(applied["backup"]) as backup:
            self.assertEqual(backup.execute("select count(*) from agent_media_plan_items").fetchone()[0], 240)
        for row_id, row in after.items():
            old_detail, new_detail = json.loads(before[row_id]["details_json"]), json.loads(row["details_json"])
            self.assertEqual(row["status"], before[row_id]["status"])
            self.assertEqual(row["created_at"], before[row_id]["created_at"])
            self.assertEqual(new_detail["customUnrelatedField"], "retain")
            for key in SCHEDULE_KEYS:
                self.assertEqual(old_detail.get(key), new_detail.get(key))
            if row["execution_mode"] == "human-owner":
                self.assertNotIn("spokenText", new_detail)
                self.assertNotIn("shootingPair", new_detail)
        second = update(self.db, apply=True, backup_dir=self.temp.name)
        self.assertTrue(all(x["updated"] == 0 and not x["removedPendingTelegramIds"] for x in second["sites"]))
        self.assertEqual(after, self.snapshot())

    def test_completed_and_other_month_rows_are_preserved(self):
        first = self.conn.execute("select id from agent_media_plan_items where execution_mode='human-owner' limit 1").fetchone()[0]
        self.conn.execute("update agent_media_plan_items set status='READY' where id=?", (first,))
        extra = build_items(next(iter(BRANDS.values())), month="2026-11")[0]
        self.insert(17, extra)
        self.insert(999, extra)
        self.conn.commit()
        before = self.snapshot()
        update(self.db, apply=True, backup_dir=self.temp.name)
        after = self.snapshot()
        for row_id, row in before.items():
            if row_id == first or row["site_id"] == 999 or json.loads(row["details_json"])["planMonth"] == "2026-11":
                self.assertEqual(row, after[row_id])

    def test_do_not_remove_published_telegram(self):
        self.conn.execute("update agent_media_plan_items set status='PUBLISHED' where channel='Telegram' and repurpose_group='oct-2'")
        self.conn.commit()
        before = self.snapshot()
        with self.assertRaises(ValueError):
            update(self.db, apply=True, backup_dir=self.temp.name)
        self.assertEqual(before, self.snapshot())

    def test_missing_slot_does_not_create_or_delete_anything(self):
        self.conn.execute("delete from agent_media_plan_items where id=(select min(id) from agent_media_plan_items)")
        self.conn.commit()
        before = self.snapshot()
        with self.assertRaises(ValueError):
            update(self.db, apply=True, backup_dir=self.temp.name)
        self.assertEqual(before, self.snapshot())


if __name__ == "__main__":
    unittest.main()
