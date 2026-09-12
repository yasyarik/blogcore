"""One-off review render for the approved SoloCruz pair-story masters.

This does not publish anything. It creates a DRAFT Reel record only.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from reel_renderer import render_vertical_reel


ROOT = Path("/var/www/blog.yas.ooo")
DB_PATH = ROOT / "data/blog_core.sqlite3"
ASSET_DIR = ROOT / "data/social_assets/7/solocruz-pair-story-v2/instagram"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> None:
    transparent = ASSET_DIR / "reel-ambient-layer.png"
    if not transparent.exists():
        Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(transparent)

    scene_specs = [
        ("scene-01-solocruz-match.jpg", "A SOLOCRUZ MATCH.", 4.4),
        ("scene-02-terminal-meet-v2.jpg", "SAME SHIP. SAME DATE.", 4.0),
        ("scene-03-deck-new-friends-v2.jpg", "THEY BOARDED TOGETHER.", 4.4),
        ("scene-04-shore-day.jpg", "ONE MATCH. NEW CREW.", 4.2),
        ("scene-05-sunset-deck-v2.jpg", "YOUR PEOPLE. YOUR CRUISE.", 4.5),
    ]
    scenes = []
    for index, (filename, headline, duration) in enumerate(scene_specs, start=1):
        scenes.append({
            "index": index,
            "backgroundPath": str(ASSET_DIR / filename),
            "foregroundPaths": [str(transparent)],
            "layers": [{"role": "ambient"}],
            "durationSeconds": duration,
            "overlayText": headline,
            "composition": {"textPlacement": "top_left", "lockTextPlacement": True},
            "cameraMove": "push_in" if index in {1, 3} else "pan_right",
            "directorCameraPlan": {"beats": [{"movement": "push_in", "start": 0, "end": duration}]},
        })

    token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = ASSET_DIR / f"instagram-reel-{token}.mp4"
    rendered = render_vertical_reel(
        scenes,
        output,
        ASSET_DIR / f"render-work-{token}",
        accent_hex="#36d6c6",
    )
    payload = {
        "source": "solocruz_pair_story_v2",
        "instagramReel": {
            "assetKey": "solocruz-pair-story-v2",
            "videoUrl": f"/sites/7/social-assets/solocruz-pair-story-v2/instagram/{output.name}",
            "coverUrl": f"/sites/7/social-assets/solocruz-pair-story-v2/instagram/{Path(rendered['thumbnailPath']).name}",
            "durationSeconds": rendered["durationSeconds"],
            "fps": rendered["fps"],
            "voice": {"provider": "none", "mode": "disabled"},
            "progress": {"phase": "ready", "scene": 5, "totalScenes": 5, "message": "Review draft ready"},
            "storyboard": {"scenes": [{"index": item["index"], "overlayText": item["overlayText"]} for item in scenes]},
        },
    }
    caption = "A cabin match can turn a solo cruise into a shared story.\n\nSoloCruz"
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """insert into social_posts(site_id,job_id,channel,content_text,content_json,remote_url,status,asset_type,language,max_chars,char_count,include_link,validation_json,created_at,updated_at)
               values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (7, "b75f54afeba87c75eb45c0a2", "instagram", caption, json.dumps(payload), "", "DRAFT", "instagram_reel", "en", 2200, len(caption), 0, "{}", now_iso(), now_iso()),
        )
        post_id = int(cur.lastrowid)
    print(json.dumps({"postId": post_id, "video": payload["instagramReel"]["videoUrl"]}))


if __name__ == "__main__":
    main()
