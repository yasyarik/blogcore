import json
import sqlite3
from datetime import datetime, timezone


DB_PATH = "data/blog_core.sqlite3"
POST_ID = 33
SITE_ID = 7

COPY = {
    1: "Stop paying double to cruise solo",
    2: "Four checks. Best one comes last.",
    3: "4. Find your community early",
    4: "3. Choose built-in social moments",
    5: "2. Pick solo-designed ships",
    6: "1. Match first. Split costs.",
    7: "SoloCruz finds compatible cabin matches",
}


def scene_index(scene, fallback):
    try:
        return int(scene.get("index") or scene.get("sceneIndex") or str(scene.get("beatId") or "").split("-")[-1] or fallback)
    except (TypeError, ValueError):
        return fallback


def update_scenes(container):
    if not isinstance(container, dict) or not isinstance(container.get("scenes"), list):
        return
    for position, scene in enumerate(container["scenes"], 1):
        if not isinstance(scene, dict):
            continue
        index = scene_index(scene, position)
        if index not in COPY:
            continue
        scene["overlayText"] = COPY[index]
        direction = scene.get("textDirection")
        if isinstance(direction, dict):
            direction["copy"] = COPY[index]
            direction["startSeconds"] = 0.0
            direction["endSeconds"] = float(scene.get("durationSeconds") or 4.0)
            direction["maxLines"] = 3
        if index == 7:
            scene["usesLogoReference"] = True


connection = sqlite3.connect(DB_PATH)
row = connection.execute(
    "select content_json from social_posts where id=? and site_id=?",
    (POST_ID, SITE_ID),
).fetchone()
if not row:
    raise SystemExit("post not found")
payload = json.loads(row[0])
reel = payload["instagramReel"]
for key in ("storyboard", "directorPlan", "sceneConcepts"):
    update_scenes(reel.get(key))
checkpoint = reel.get("planningCheckpoint") if isinstance(reel.get("planningCheckpoint"), dict) else {}
for key in ("directorPlan", "sceneConcepts"):
    update_scenes(checkpoint.get(key))
briefs = [reel.get("editorialBrief"), checkpoint.get("editorialBrief")]
for brief in briefs:
    if isinstance(brief, dict) and isinstance(brief.get("hook"), dict):
        brief["hook"]["overlayText"] = COPY[1]
reel["progress"] = {
    "phase": "rendering",
    "scene": 7,
    "totalScenes": 7,
    "message": "Rebuilding registered layers, persistent scene text, and the logo-referenced final frame",
}
reel["version"] = 17
visuals = reel.get("visualProductionScenes")
if isinstance(visuals, list):
    reel["visualProductionScenes"] = [
        scene for scene in visuals
        if scene_index(scene, 0) != 7
    ]
payload["instagramReel"] = reel
now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
connection.execute(
    "update social_posts set content_json=?,status='GENERATING',updated_at=? where id=?",
    (json.dumps(payload, ensure_ascii=False), now, POST_ID),
)
connection.commit()
print(json.dumps({"updated": True, "copy": COPY}, ensure_ascii=False))
