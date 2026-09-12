"""Re-render the SoloCruz Reel baseline from preserved visual assets only."""

import copy
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from reel_renderer import render_vertical_reel


DB = "data/blog_core.sqlite3"
SITE_ID = 7
SOURCE_POST_ID = 33
SOURCE_KEY = "b75f54afeba87c75eb45c0a2-8e0f142c6f4bf5d9-focused-20260814163031"
SOURCE_DIR = Path("data/social_assets/7") / SOURCE_KEY / "instagram"
COPY = [
    ("A solo cabin isn't enough", "A solo-friendly cruise is more than a cabin for one."),
    ("Check the single supplement", "Compare the single supplement before choosing a sailing."),
    ("Choose a cabin priced for one", "Dedicated solo cabins can make pricing clearer for one guest."),
    ("Split a cabin. Share the fare.", "A compatible cabin mate can make a shared cabin cost easier to manage."),
    ("Meet your cabin mate before booking", "SoloCruz helps solo travelers connect around shared cabin arrangements before booking."),
]


def main():
    asset_key = "b75f54afeba87c75eb45c0a2-text-only-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    asset_dir = Path("data/social_assets/7") / asset_key / "instagram"
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        source = conn.execute(
            "select content_json,content_text from social_posts where id=? and site_id=?",
            (SOURCE_POST_ID, SITE_ID),
        ).fetchone()
        if not source:
            raise RuntimeError("Source Reel draft not found")
        payload = json.loads(source["content_json"])
        reel = payload["instagramReel"]
        storyboard = copy.deepcopy(reel["storyboard"])
        render_scenes = []
        for scene, (overlay, narration) in zip(storyboard["scenes"], COPY):
            index = int(scene["index"])
            background = SOURCE_DIR / f"scene-{index:02d}-background.png"
            foregrounds = sorted(SOURCE_DIR.glob(f"scene-{index:02d}-photo-layer-*.png"))
            if not background.is_file() or not foregrounds:
                raise RuntimeError(f"Missing preserved photo assets for scene {index}")
            scene["overlayText"] = overlay
            scene["narration"] = narration
            scene["supportingText"] = ""
            scene["layers"] = [layer for layer in (scene.get("layers") or []) if str(layer.get("role") or "") != "evidence_graphic"]
            scene["assets"] = {
                "backgroundUrl": f"/sites/{SITE_ID}/social-assets/{asset_key}/instagram/{background.name}",
                "foregroundUrls": [f"/sites/{SITE_ID}/social-assets/{asset_key}/instagram/{path.name}" for path in foregrounds],
            }
            scene["composition"] = {**(scene.get("composition") or {}), "lockTextPlacement": True}
            scene["textDirection"] = {**(scene.get("textDirection") or {}), "maxLines": 3}
            render_scenes.append({
                **scene,
                "backgroundPath": str(background),
                "foregroundPaths": [str(path) for path in foregrounds],
                "fullCanvasLayers": True,
            })
        storyboard["scenes"] = render_scenes
        asset_dir.mkdir(parents=True, exist_ok=False)
        output_name = "instagram-reel-text-only.mp4"
        rendered = render_vertical_reel(
            render_scenes,
            asset_dir / output_name,
            asset_dir / "render-work",
            accent_hex="#36d6c6",
            music_path="data/reel_music/7/d5d3adad1ae6578a7d05ff2a/brand-track.mp3",
            narration_path=None,
        )
        validation = {
            "version": 17,
            "copyStyle": "large_kinetic_only_no_evidence_cards_no_scrim",
            "voiceEnabled": False,
            "reusedVisualAssets": SOURCE_KEY,
            "newImageGenerations": 0,
            "durationTargetSeconds": rendered["durationSeconds"],
            "scenes": len(render_scenes),
            "musicMode": rendered.get("musicMode") or "none",
        }
        reel.update({
            "assetKey": asset_key,
            "storyboard": storyboard,
            "visualProductionScenes": [],
            "voiceEnabled": False,
            "audioMode": "music_only",
            "voice": {"provider": "none", "mode": "disabled"},
            "videoUrl": f"/sites/{SITE_ID}/social-assets/{asset_key}/instagram/{output_name}",
            "coverUrl": f"/sites/{SITE_ID}/social-assets/{asset_key}/instagram/{Path(rendered['thumbnailPath']).name}",
            "durationSeconds": rendered["durationSeconds"],
            "fps": rendered["fps"],
            "musicMode": rendered.get("musicMode") or "none",
            "progress": {"phase": "ready", "scene": len(render_scenes), "totalScenes": len(render_scenes), "message": "Text-only Reel draft is ready for review"},
            "revision": {"basedOnPostId": SOURCE_POST_ID, "reason": "Removed evidence-card copy; reused approved visual assets; no voiceover"},
        })
        payload["instagramReel"] = reel
        payload["validation"] = validation
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cursor = conn.execute(
            """insert into social_posts(site_id,job_id,channel,content_text,content_json,remote_url,status,asset_type,language,max_chars,char_count,include_link,validation_json,created_at,updated_at)
               select site_id,job_id,channel,?,?,?,?,asset_type,language,max_chars,?,include_link,?,?,?
               from social_posts where id=?""",
            ("", json.dumps(payload, ensure_ascii=False), "", "DRAFT", len(source["content_text"] or ""), json.dumps(validation, ensure_ascii=False), now, now, SOURCE_POST_ID),
        )
        post_id = cursor.lastrowid
        conn.execute("update social_posts set status='SUPERSEDED',updated_at=? where id=?", (now, SOURCE_POST_ID))
        conn.execute(
            "insert into content_job_logs(site_id,job_id,ts,level,step,message) select site_id,job_id,?,?,?,?,? from social_posts where id=?",
            (now, "INFO", "instagram-reel", f"Rendered text-only Reel #{post_id} from preserved assets; no image generation; no voiceover", post_id),
        )
        conn.commit()
        print(json.dumps({"postId": post_id, "videoUrl": reel["videoUrl"], "duration": rendered["durationSeconds"]}))
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
