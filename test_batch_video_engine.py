import sqlite3
import unittest

from batch_video_engine import (
    ensure_video_batch_schema,
    estimate_voiceover_seconds,
    minimum_voiceover_clip_count,
    narrative_contract_issues,
    optimal_omni_clip_duration,
    plan_video_batch,
    queue_video_assembly_for_publication,
    validate_batch,
    voiceover_boundary_coverage,
    voiceover_fits_window,
)
from content_engine import ensure_schema as ensure_content_engine_schema


class VideoBatchPlannerTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        ensure_content_engine_schema(self.conn)
        ensure_video_batch_schema(self.conn)
        now = "2026-08-30T00:00:00+00:00"
        self.conn.execute(
            "insert into content_engine_contracts(site_id,contract_url,contract_version,schema_version,payload_json,payload_hash,fetched_at,active) values(1,'https://example.test/contract','v1',1,'{}','hash',?,1)",
            (now,),
        )
        self.conn.execute(
            "insert into knowledge_sources(id,site_id,owner,url,source_class,retrieval_adapter,poll_cadence_hours,robots_terms_state,media_rights_policy,created_at,updated_at) values('source',1,'Official authority','https://example.test/source','official_government_or_municipality','official_api',24,'allowed','citation_only',?,?)",
            (now, now),
        )
        for ordinal in range(1, 103):
            entity_id, claim_id, edge_id, candidate_id = f"entity-{ordinal}", f"claim-{ordinal}", f"edge-{ordinal}", f"candidate-{ordinal}"
            self.conn.execute(
                "insert into knowledge_entities(id,site_id,entity_type,canonical_name,first_verified_at,last_verified_at) values(?,1,'place',?,?,?)",
                (entity_id, f"Madeira place {ordinal}", now, now),
            )
            fact = f"The official record establishes a durable Madeira fact number {ordinal} with enough specific context for an explanatory video sequence."
            self.conn.execute(
                "insert into knowledge_claims(id,site_id,entity_id,source_id,document_id,source_url,claim_text,claim_fingerprint,supporting_excerpt,checked_at,confidence,freshness_class,risk_class,visual_rights_state,created_at,updated_at) values(?,1,?,'source','document','https://example.test/source',?,?,?, ?,0.95,'durable','low','generated_explanatory_media',?,?)",
                (claim_id, entity_id, fact, f"fingerprint-{ordinal}", fact, now, now, now),
            )
            self.conn.execute(
                "insert into knowledge_edges(id,site_id,source_entity_id,target_entity_id,relationship_type,supporting_claim_ids_json,verification_state,confidence,created_at,updated_at) values(?,1,?,?,'connected_to','[]','VERIFIED',0.9,?,?)",
                (edge_id, entity_id, entity_id, now, now),
            )
            self.conn.execute(
                "insert into content_candidates(id,site_id,entity_id,claim_id,relationship_id,native_angle,audience_state,native_format,locale,proposed_payoff,score,score_breakdown_json,novelty_fingerprint,workflow_state,created_at,updated_at) values(?,1,?,?,?,'hidden_mechanism','curious about Madeira','reel','en','Explain the verified mechanism',90,'{}',?,'CANDIDATE',?,?)",
                (candidate_id, entity_id, claim_id, edge_id, f"candidate-fingerprint-{ordinal}", now, now),
            )

    def tearDown(self):
        self.conn.close()

    def test_plans_shared_boundaries_reuse_and_is_idempotent(self):
        plans = {
            "claim-1": {"clipCount": 1, "durationRationale": "One reveal is enough."},
            "claim-2": {"clipCount": 3, "durationRationale": "Setup, mechanism and payoff are distinct."},
        }
        first = plan_video_batch(self.conn, 1, "test", target_ideas=2, clips_per_idea=3, config={"ideaPlans": plans})
        second = plan_video_batch(self.conn, 1, "test", target_ideas=2, clips_per_idea=3, config={"ideaPlans": plans})
        validation = validate_batch(self.conn, 1, first["batchId"])
        self.assertTrue(first["created"])
        self.assertFalse(second["created"])
        self.assertEqual((2, 4, 6, 10), (validation["ideas"], validation["clips"], validation["keyframes"], validation["reuseUses"]))
        self.assertEqual([6, 18], [row[0] for row in self.conn.execute("select duration_seconds from content_video_ideas order by ordinal")])
        self.assertTrue(validation["ok"], validation["errors"])
        self.assertEqual(1, self.conn.execute("select count(*) from content_video_batches").fetchone()[0])

    def test_planning_never_creates_generated_assets(self):
        result = plan_video_batch(self.conn, 1, "no-media", target_ideas=1, clips_per_idea=2)
        self.assertEqual(0, self.conn.execute("select count(*) from content_video_clips where generation_state!='PLANNED' or asset_path is not null or remote_job_id is not null").fetchone()[0])
        self.assertEqual(0, self.conn.execute("select count(*) from content_keyframes where generation_state!='PLANNED' or asset_path is not null").fetchone()[0])
        self.assertTrue(validate_batch(self.conn, 1, result["batchId"])["ok"])

    def test_supplied_plan_can_use_claim_beyond_top_100(self):
        result = plan_video_batch(
            self.conn,
            1,
            "beyond-top-100",
            target_ideas=1,
            clips_per_idea=2,
            config={"ideaPlans": {"claim-102": {"primaryClaimId": "claim-102", "clipCount": 1}}},
        )
        claim_id = self.conn.execute(
            "select claim_id from content_video_ideas where batch_id=?", (result["batchId"],)
        ).fetchone()[0]
        self.assertEqual("claim-102", claim_id)

    def test_voiceover_duration_sets_a_physical_clip_floor(self):
        hook = "This tourist cable car was not built for visitors."
        script = hook + " It was created to carry food and give farmers access to fertile land."
        self.assertGreater(estimate_voiceover_seconds(script, hook), 8.8)
        self.assertEqual(2, minimum_voiceover_clip_count(script, 10, hook))
        fits, estimated, available = voiceover_fits_window(script, 0.4, 9.2, hook)
        self.assertFalse(fits, (estimated, available))

    def test_omni_duration_uses_shortest_supported_clip_that_fits(self):
        self.assertEqual(6, optimal_omni_clip_duration("A short visual statement fits this compact beat."))
        self.assertEqual(8, optimal_omni_clip_duration("This slightly longer spoken sentence needs enough room to sound completely natural."))
        self.assertEqual(10, optimal_omni_clip_duration("This longer spoken sentence needs a wider timing window so the narrator can deliver every word without rushing."))
        self.assertIsNone(optimal_omni_clip_duration("This tourist cable car was not built for visitors. It was created to carry food and give farmers access to fertile land.", "This tourist cable car was not built for visitors."))

    def test_batch_rejects_supplied_clip_count_below_speech_floor(self):
        hook = "This tourist cable car was not built for visitors."
        script = hook + " It was created to carry food and give farmers access to fertile land."
        plan = {
            "primaryClaimId": "claim-1",
            "clipCount": 1,
            "hook": hook,
            "narration": {"fullScript": script},
            "clips": [{
                "voiceoverText": script,
                "voiceoverStartSeconds": 0.4,
                "voiceoverEndSeconds": 9.2,
            }],
        }
        with self.assertRaisesRegex(ValueError, "at least 2 clips are required"):
            plan_video_batch(
                self.conn,
                1,
                "speech-floor",
                target_ideas=1,
                clips_per_idea=3,
                config={"ideaPlans": {"claim-1": plan}},
            )

    def test_per_clip_timing_keeps_native_voiceover_at_the_boundary(self):
        hook = "Cable cars moved harvests instead of tourists, never made for visitors."
        payoff = "It gave farmers access to fields on Atlantic cliffs far below."
        plan = {
            "primaryClaimId": "claim-1",
            "clipCount": 2,
            "hook": hook,
            "narration": {"fullScript": hook + " " + payoff},
            "clips": [
                {
                    "durationSeconds": 6,
                    "voiceoverText": hook,
                    "voiceoverStartSeconds": 0.0,
                    "voiceoverEndSeconds": 5.65,
                },
                {
                    "durationSeconds": 6,
                    "voiceoverText": payoff,
                    "voiceoverStartSeconds": 0.0,
                    "voiceoverEndSeconds": 5.65,
                    "characterDirection": {
                        "required": True,
                        "action": "A farmer unloads produce crates.",
                        "speechMode": "voiceover",
                    },
                },
            ],
        }
        result = plan_video_batch(
            self.conn,
            1,
            "mixed-duration-validation",
            target_ideas=1,
            clips_per_idea=3,
            config={"ideaPlans": {"claim-1": plan}},
        )
        validation = validate_batch(self.conn, 1, result["batchId"])
        self.assertTrue(validation["ok"], validation["errors"])
        second_prompt = self.conn.execute(
            "select video_prompt from content_video_clips where idea_id=(select id from content_video_ideas where batch_id=?) order by ordinal limit 1 offset 1",
            (result["batchId"],),
        ).fetchone()[0]
        self.assertIn("off-screen narrator", second_prompt)
        self.assertIn("never lip-syncs or speaks", second_prompt)
        self.assertNotIn("visible character speaks", second_prompt)
        self.assertIn("intimate, magnetic storyteller", second_prompt)
        self.assertIn("never merely read it", second_prompt)

    def test_rejects_a_short_line_that_leaves_a_dead_boundary_hold(self):
        plan = {
            "primaryClaimId": "claim-1",
            "clipCount": 1,
            "hook": "A short line.",
            "narration": {"fullScript": "A short line."},
            "clips": [{
                "durationSeconds": 6,
                "voiceoverText": "A short line.",
                "voiceoverStartSeconds": 0.2,
                "voiceoverEndSeconds": 5.65,
            }],
        }
        with self.assertRaisesRegex(ValueError, "does not cover its visual duration"):
            plan_video_batch(
                self.conn, 1, "dead-air", target_ideas=1, clips_per_idea=3,
                config={"ideaPlans": {"claim-1": plan}},
            )
        coverage = voiceover_boundary_coverage("A short line.", 6, 0.2, 5.7)
        self.assertGreater(coverage["estimatedTailSeconds"], 1.00)

    def test_queues_only_an_assembled_video_without_legacy_social_state(self):
        result = plan_video_batch(self.conn, 1, "publication-queue", target_ideas=1, clips_per_idea=2)
        assembly = self.conn.execute(
            "select id from content_video_assemblies where idea_id=(select id from content_video_ideas where batch_id=?)",
            (result["batchId"],),
        ).fetchone()[0]
        with self.assertRaisesRegex(ValueError, "assembled video asset"):
            queue_video_assembly_for_publication(self.conn, 1, assembly, "instagram_reel")
        self.conn.execute("update content_video_assemblies set asset_path='/tmp/approved.mp4' where id=?", (assembly,))
        queued = queue_video_assembly_for_publication(self.conn, 1, assembly, "instagram_reel", {"caption": "Draft"})
        self.assertEqual("QUEUED", queued["status"])
        self.assertEqual(1, self.conn.execute("select count(*) from content_video_publication_queue").fetchone()[0])

    def test_rejects_payoff_leak_and_metadata_only_reaction(self):
        plan = {
            "clips": [
                {"voiceoverText": "The answer arrives immediately.", "onScreenText": []},
                {"voiceoverText": "Nothing new happens here.", "onScreenText": []},
            ],
            "narrativeArc": {
                "payoffClipOrdinal": 1,
                "beats": [
                    {"clipOrdinal": 1, "role": "hook", "newInformation": "the answer", "withheldUntilLater": "", "visualProof": "a detail", "whyNextBeatNecessary": "none"},
                    {"clipOrdinal": 2, "role": "payoff", "newInformation": "nothing", "withheldUntilLater": "", "visualProof": "a view", "whyNextBeatNecessary": "none"},
                ],
            },
            "viewerReactionBeat": {
                "clipOrdinal": 2, "responseMode": "comment", "inReelExpression": "Tell us below", "placement": "caption", "whyEarned": "generic",
            },
        }
        errors = narrative_contract_issues(plan)
        self.assertTrue(any("reveals its payoff" in error for error in errors), errors)
        self.assertTrue(any("metadata" in error or "caption" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
