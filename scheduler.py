#!/usr/bin/env python3
"""Run due Blog Core article, research, and social publications."""

import time

from app import (
    capture_publication_failure_email_alerts,
    init_db,
    run_queued_reel_music_generations,
    run_queued_instagram_reel_generations,
    run_scheduled_agent_audits,
    run_scheduled_evidence_pipeline,
    run_scheduled_evidence_x_publications,
    run_scheduled_threads_publications,
    run_scheduled_facebook_publications,
    run_scheduled_short_form_publications,
    run_scheduled_media_plan_reminders,
    run_queued_evidence_draft_generations,
    run_scheduled_social_operation_discovery,
    run_scheduled_agent_telegram_reports,
    run_scheduled_strategy_analyses,
    run_scheduled_gsc_collection,
    run_scheduled_gsc_weekly_content_planning,
    run_scheduled_content_publications,
    run_scheduled_instagram_reel_publications,
    run_scheduled_shared_carousel_publications,
    run_scheduled_social_publications,
    run_scheduled_tiktok_carousel_publications,
    run_publication_failure_email_notifications,
)


def run_publication_worker(queue_name, worker):
    """Run one publication queue and always persist its failures for email."""
    try:
        result = worker()
    except Exception as error:
        result = {"due": 1, "results": [{"action": "error", "error": str(error)}]}
    capture_publication_failure_email_alerts(queue_name, result)
    return result


def main():
    init_db()
    while True:
        try:
            result = run_publication_worker("content", run_scheduled_content_publications)
            if result["due"]:
                print(f"scheduled-publications {result}", flush=True)
            music_result = run_queued_reel_music_generations(limit=1)
            if music_result["due"]:
                print(f"reel-brand-music {music_result}", flush=True)
            reel_render_result = run_queued_instagram_reel_generations(limit=1)
            if reel_render_result["due"]:
                print(f"instagram-reel-render {reel_render_result}", flush=True)
            shared_carousel_result = run_publication_worker("shared-carousel", run_scheduled_shared_carousel_publications)
            if shared_carousel_result["due"]:
                print(f"scheduled-shared-carousels {shared_carousel_result}", flush=True)
            social_result = run_publication_worker("social", run_scheduled_social_publications)
            if social_result["due"]:
                print(f"scheduled-social-publications {social_result}", flush=True)
            reel_result = run_publication_worker("instagram-reel", run_scheduled_instagram_reel_publications)
            if reel_result["due"]:
                print(f"scheduled-instagram-reels {reel_result}", flush=True)
            tiktok_result = run_publication_worker("tiktok-carousel", run_scheduled_tiktok_carousel_publications)
            if tiktok_result["due"]:
                print(f"scheduled-tiktok-carousels {tiktok_result}", flush=True)
            agent_result = run_scheduled_agent_audits()
            if agent_result["due"]:
                print(f"seo-agent-audit {agent_result}", flush=True)
            evidence_result = run_scheduled_evidence_pipeline()
            if evidence_result["due"]:
                print(f"evidence-research {evidence_result}", flush=True)
            evidence_draft_result = run_queued_evidence_draft_generations(limit=1)
            if evidence_draft_result["due"]:
                print(f"evidence-blog-draft {evidence_draft_result}", flush=True)
            evidence_x_result = run_publication_worker("evidence-x", run_scheduled_evidence_x_publications)
            if evidence_x_result["due"]:
                print(f"evidence-x-publications {evidence_x_result}", flush=True)
            threads_result = run_publication_worker("threads", run_scheduled_threads_publications)
            if threads_result["due"]:
                print(f"threads-publications {threads_result}", flush=True)
            facebook_result = run_publication_worker("facebook", run_scheduled_facebook_publications)
            if facebook_result["due"]:
                print(f"facebook-publications {facebook_result}", flush=True)
            short_form_result = run_publication_worker("short-form", run_scheduled_short_form_publications)
            if short_form_result["due"]:
                print(f"short-form-publications {short_form_result}", flush=True)
            media_plan_reminders = run_scheduled_media_plan_reminders()
            if media_plan_reminders["due"]:
                print(f"media-plan-reminders {media_plan_reminders}", flush=True)
            email_alert_result = run_publication_failure_email_notifications()
            if email_alert_result["sent"] or email_alert_result["failed"]:
                print(f"publication-failure-email {email_alert_result}", flush=True)
            social_discovery_result = run_scheduled_social_operation_discovery()
            if social_discovery_result["due"]:
                print(f"social-operator-discovery {social_discovery_result}", flush=True)
            telegram_result = run_scheduled_agent_telegram_reports()
            if telegram_result["due"]:
                print(f"agent-telegram-report {telegram_result}", flush=True)
            strategy_result = run_scheduled_strategy_analyses()
            if strategy_result["due"]:
                print(f"growth-strategy-analysis {strategy_result}", flush=True)
            gsc_result = run_scheduled_gsc_collection()
            if gsc_result["due"]:
                print(f"gsc-finalized-data {gsc_result}", flush=True)
            gsc_planning_result = run_scheduled_gsc_weekly_content_planning()
            if gsc_planning_result["due"]:
                print(f"gsc-weekly-content-planning {gsc_planning_result}", flush=True)
        except Exception as error:
            print(f"scheduled-publications worker error: {error}", flush=True)
        time.sleep(60)


if __name__ == "__main__":
    main()
