#!/usr/bin/env python3
"""Materialize the reviewed SoloCruz short-form queue without publishing it."""

from __future__ import annotations

import argparse
import json
import urllib.parse
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from app import INSTAGRAM_REEL_ASSET_TYPE, db, init_db, now_iso

SITE_ID = 7
QUEUE_PREFIX = "solocruz-short-form:"
ASSET_CHANNEL = "facebook"
EXPERT_DIR = Path("/var/www/blog.yas.ooo/data/social_assets/7/solocruz-short-form-expert") / ASSET_CHANNEL
SOLO_DIR = Path("/var/www/blog.yas.ooo/data/social_assets/7/solocruz-short-form-solo") / ASSET_CHANNEL


def asset_url(asset_key: str, filename: str) -> str:
    return "/sites/7/social-assets/{}/{}/{}".format(
        urllib.parse.quote(asset_key, safe=""),
        ASSET_CHANNEL,
        urllib.parse.quote(filename, safe=""),
    )


def schedule_at(day: date, hour: int) -> str:
    """Return a UTC scheduler timestamp for a U.S. Eastern publication slot."""
    return datetime.combine(day, time(hour), tzinfo=ZoneInfo("America/New_York")).astimezone(timezone.utc).isoformat(timespec="seconds")


def caption(sequence: int, source: str) -> str:
    if source == "expert":
        return (
            f"Cruise tip {sequence}: a little planning can make solo sailing feel simpler, safer and more social. "
            "Save this for your next cruise. 🚢\n\n#SoloCruise #CruiseTips #SoloCruz"
        )
    return (
        f"Solo cruise idea {sequence}: find the right cabin mate before booking and keep more of your cruise budget. "
        "🚢\n\n#SoloCruise #Cabinmate #SoloCruz"
    )


def insert_row(conn, *, job_id: str, channel: str, asset_type: str, text: str, payload: dict, scheduled_for: str) -> None:
    now = now_iso()
    conn.execute(
        """insert into social_posts(site_id,job_id,channel,content_text,content_json,remote_url,status,
           asset_type,language,max_chars,char_count,include_link,validation_json,created_at,updated_at,scheduled_for)
           values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            SITE_ID, job_id, channel, text, json.dumps(payload, ensure_ascii=False), "", "DRAFT", asset_type,
            "en", 2200, len(text), 0, json.dumps({"queue": "solocruz-short-form", "reviewedHistory": True}), now, now, scheduled_for,
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", default="2026-09-10", type=date.fromisoformat)
    args = parser.parse_args()
    expert = sorted(EXPERT_DIR.glob("*.mp4"))
    solo = sorted(SOLO_DIR.glob("*.mp4"))
    days = len(expert)
    required_solo = days * 3
    if len(expert) != 38 or len(solo) < required_solo:
        raise SystemExit(f"Need exactly 38 expert and at least {required_solo} SoloCruz videos; found expert={len(expert)}, solo={len(solo)}")
    init_db()
    with db() as conn:
        existing = conn.execute("select count(*) as n from social_posts where site_id=? and job_id like ?", (SITE_ID, f"{QUEUE_PREFIX}%")).fetchone()["n"]
        if existing:
            raise SystemExit(f"Queue already exists ({existing} rows); no changes made.")
        for day_index, expert_video in enumerate(expert):
            day = args.start_date + timedelta(days=day_index)
            # Four operator-approved Eastern-Time slots: three SoloCruz videos and
            # one expert video. Facebook and YouTube receive the same source at
            # the same local slot. The existing Instagram daily carousel cadence
            # is deliberately not altered; the expert Reel is the second daily
            # Instagram creative at 07:00 ET.
            day_items = [
                ("solo", solo[day_index * 3], 7),
                ("expert", expert_video, 12),
                ("solo", solo[day_index * 3 + 1], 19),
                ("solo", solo[day_index * 3 + 2], 22),
            ]
            for source, video, slot in day_items:
                sequence = day_index * 4 + slot
                asset_key = "solocruz-short-form-expert" if source == "expert" else "solocruz-short-form-solo"
                video_url = asset_url(asset_key, video.name)
                text = caption(sequence, source)
                title = (f"Cruise smarter · SoloCruz tip {day_index + 1}" if source == "expert" else f"Find your cruise companion · {sequence}")
                payload = {"sourceLibrary": "woman expert" if source == "expert" else "solocruz-videos", "shortFormVideo": {"videoUrl": video_url, "title": title, "sourceFile": video.name}}
                job_id = f"{QUEUE_PREFIX}{day.isoformat()}:{source}:{sequence}"
                for channel, asset_type in (("facebook", "facebook_reel"), ("youtube", "youtube_short")):
                    insert_row(conn, job_id=job_id, channel=channel, asset_type=asset_type, text=text, payload=payload, scheduled_for=schedule_at(day, slot))
                if source == "expert":
                    instagram_payload = {**payload, "instagramReel": {"videoUrl": video_url}}
                    insert_row(conn, job_id=job_id, channel="instagram", asset_type=INSTAGRAM_REEL_ASSET_TYPE, text=text, payload=instagram_payload, scheduled_for=schedule_at(day, 7))
    print(json.dumps({"days": days, "facebookReels": days * 4, "youtubeShorts": days * 4, "instagramReels": days, "soloCruzVideosQueued": required_solo, "soloCruzVideosHeld": len(solo) - required_solo, "expertVideos": len(expert), "timezone": "America/New_York", "startDate": args.start_date.isoformat()}))


if __name__ == "__main__":
    main()
