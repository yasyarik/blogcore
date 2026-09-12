import json
import shutil
import sqlite3
from pathlib import Path

from registered_scene import refine_registered_layer_file


DB_PATH = Path("data/blog_core.sqlite3")
ASSET_DIR = Path("data/social_assets/7/b75f54afeba87c75eb45c0a2-ea8b9332fb15b8c7/instagram")


connection = sqlite3.connect(DB_PATH)
payload = json.loads(connection.execute("select content_json from social_posts where id=33").fetchone()[0])
reel = payload["instagramReel"]
storyboard = reel.get("storyboard") if isinstance(reel.get("storyboard"), dict) else {}
roles_by_scene = {}
for scene in storyboard.get("scenes") or []:
    index = int(scene.get("index") or 0)
    roles_by_scene[index] = [str(layer.get("role") or "story_object") for layer in scene.get("layers") or []]

updated = []
for visual in reel.get("visualProductionScenes") or []:
    index = int(visual.get("sceneIndex") or 0)
    if not 1 <= index <= 6:
        continue
    master = ASSET_DIR / f"scene-{index:02d}-attempt-1/master.jpg"
    clean = ASSET_DIR / f"scene-{index:02d}-attempt-1/clean.jpg"
    roles = roles_by_scene.get(index) or []
    for layer_index, filename in enumerate(visual.get("foregroundFilenames") or []):
        path = ASSET_DIR / filename
        role = roles[layer_index] if layer_index < len(roles) else "story_object"
        manifest = json.loads((ASSET_DIR / f"scene-{index:02d}-attempt-1/manifest.json").read_text(encoding="utf-8"))
        source_name = manifest["layers"][layer_index]["filename"]
        shutil.copy2(ASSET_DIR / f"scene-{index:02d}-attempt-1" / source_name, path)
        refine_registered_layer_file(path, clean, master, role=role)
        updated.append({"scene": index, "file": filename, "role": role})

print(json.dumps({"updated": updated}, ensure_ascii=False, indent=2))
