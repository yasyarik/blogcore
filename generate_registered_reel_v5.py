#!/usr/bin/env python3
"""Build the real registered-layer Reel for an existing Blog Core Reel draft."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from base64 import b64encode
from pathlib import Path

import app
from registered_reel_renderer import render_registered_reel


def stage_plan_prompt(site, job, storyboard, stage_id):
    scenes = [scene for scene in storyboard["scenes"] if int(scene["stageId"]) == stage_id]
    beats = "\n".join(
        f"- scene {scene['index']}: {scene['overlayText']} | {scene['narration']} | {scene['visualStory']}"
        for scene in scenes
    )
    group_note = (
        "This is the community resolution. The single protagonist component may be a cohesive group of two or three large adjacent travelers, with the continuity-anchor woman clearly closest to camera. Treat the group as one integrated character component."
        if stage_id == 3 else
        "Use one large continuity-anchor woman as the protagonist component."
    )
    return f"""
Plan one production master photograph for stage {stage_id} of a real seven-scene Instagram Reel.
Return JSON only using the supplied schema.

BRAND: {site['brand_name'] or site['domain']}
ARTICLE: {job['title'] or job['topic']}
CONTINUITY ANCHOR: {storyboard['continuityAnchor']}
STAGE STORY BEATS:
{beats}

Create exactly three physically integrated components inside one continuous 9:16 photograph:
1. Exactly one `protagonist` component in `left_subject` or `right_subject`. {group_note}
2. One non-textual `environment_detail` in the opposite upper zone, visibly attached to real architecture, railing, wall, mast, or ceiling.
3. One meaningful `story_object` in the opposite lower zone, resting directly on a visible floor or deck with a contact shadow.

    The protagonist must be an unmistakable close foreground waist-up or head-to-upper-thigh portrait, 68-82% frame height and 42-55% frame width. The lower body must leave the frame; never compose a seated full-body or room-wide portrait. No small or distant people. Each non-person element must occupy 8-18% of the frame area and carry a clear story beat at phone size; never choose a small decorative fitting. Keep at least 5% visible negative-space separation between all three bounding boxes.

This is one photograph from one lens and one moment. No collage, panels, floating items, overlapping silhouettes, signs, maps, labels, displays, text, logos, UI, tables, stands, shelves, or decorative symbols. Each component must advance the real stage story rather than decorate it.

`basePrompt` describes the exact empty location, camera, architecture, light, and surfaces before these three components appear. It must provide mounting architecture in the upper opposite zone and a clear floor/deck area in the lower opposite zone.
""".strip()


def generate_stage(site, job, storyboard, stage_id, root, identity_reference=None):
    stage_dir = root / f"stage-{stage_id:02d}"
    errors = []

    # Resume a production master that was already generated and only failed a
    # downstream registration check. This prevents paying to recreate valid art.
    existing_paths = {
        "plan": stage_dir / "scene-plan.json",
        "clean": stage_dir / "clean-reference-source.jpg",
        "master": stage_dir / "registered-master-source.jpg",
        "removal": stage_dir / "registered-removal-source.jpg",
        "specs": stage_dir / "layer-specs.json",
    }
    if all(path.exists() for path in existing_paths.values()):
        worker = subprocess.run(
            [sys.executable, str(app.BASE_DIR / "registered_scene.py"), "--clean", str(existing_paths["clean"]), "--removal", str(existing_paths["removal"]), "--master", str(existing_paths["master"]), "--specs", str(existing_paths["specs"]), "--output-dir", str(stage_dir)],
            capture_output=True, text=True, timeout=720, check=False,
        )
        if worker.returncode == 0:
            master_bytes = existing_paths["master"].read_bytes()
            return {
                "path": str(stage_dir),
                "manifest": json.loads(worker.stdout.strip().splitlines()[-1])["pack"],
                "plan": json.loads(existing_paths["plan"].read_text(encoding="utf-8")),
                "masterReference": {"mime_type": "image/jpeg", "data": b64encode(master_bytes).decode("ascii")},
                "attempt": 0,
            }
        errors.append((worker.stderr or worker.stdout)[-1600:])

    for attempt in range(1, 4):
        shutil.rmtree(stage_dir, ignore_errors=True)
        stage_dir.mkdir(parents=True, exist_ok=True)
        try:
            plan = app.normalize_registered_scene_plan(
                app._gemini_text_json(
                    stage_plan_prompt(site, job, storyboard, stage_id),
                    response_schema=app.REGISTERED_SCENE_PLAN_SCHEMA,
                    temperature=0.42,
                    repair=False,
                )
            )
            (stage_dir / "scene-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
            protagonist_zone = next(item["zone"] for item in plan["components"] if item["role"] == "protagonist")
            side = "left" if protagonist_zone == "left_subject" else "right"
            opposite = "right" if side == "left" else "left"
            clean_prompt = f"""
Create the empty production location plate for stage {stage_id} of a premium 9:16 cinematic Reel.
STORY: {plan['sceneStory']}
LOCATION: {plan['basePrompt']}

Reserve the nearest foreground {side} side for a dominant close portrait occupying roughly half the frame width and at least two thirds of its height. Build a broad continuous visible mounting surface in the upper-{opposite} quadrant and a separate broad floor/deck support area in the lower-{opposite} quadrant. Both must have room for a large story-bearing element, not a decorative detail. Keep a wide empty gap between all three areas.

Show only one continuous empty location from one camera: architecture, floor/deck, sky, water, and natural depth. Continuous perspective and uninterrupted structural lines. No people, luggage, props, furniture, vessels, signs, text, logos, screens, UI, panels, seams, quadrants, or collage.
""".strip()
            clean_bytes = app._gemini_image_jpeg(clean_prompt, aspect_ratio="9:16")
            clean_path = stage_dir / "clean-reference-source.jpg"
            clean_path.write_bytes(clean_bytes)
            master_prompt = app.build_registered_master_prompt(site, job, plan) + """

PRODUCTION FRAMING OVERRIDE:
- Crop the protagonist at the waist or upper thigh. Their face and torso must dominate the foreground, occupy 68-82% of frame height and 42-55% of frame width, and remain readable in a small vertical mobile frame.
- Do not show the protagonist's full legs, feet, chair, or a wide room around them. If seated, frame them as a close editorial portrait rather than a room interior.
- Each other planned component must occupy 8-18% of total frame area. Replace any tiny lamp, brochure, fitting, or decorative prop with a larger physically integrated story-bearing equivalent that still matches its role and zone.
""".strip()
            if identity_reference:
                master_prompt += "\n\nThe first attached image is the empty location plate. The second is the prior-stage identity reference. Preserve the same recognizable continuity-anchor woman and wardrobe, but use the new pose, emotion, framing, companions, and action required by this stage. Do not copy the prior pose or background."
            references = [{"mime_type": "image/jpeg", "data": b64encode(clean_bytes).decode("ascii")}]
            if identity_reference:
                references.append(identity_reference)
            master_bytes = app._gemini_image_jpeg(master_prompt, aspect_ratio="9:16", reference_image=references)
            master_path = stage_dir / "registered-master-source.jpg"
            master_path.write_bytes(master_bytes)
            removal_prompt = "Remove only the three planned components from this exact master and reconstruct the continuous physical surfaces behind them. Preserve every unmentioned pixel, camera line, deck seam, railing, wall, horizon, light and shadow. No replacement objects, people, text, signs, UI, seams or panels. Components:\n" + "\n".join(f"- {item['id']}: {item['description']}" for item in plan["components"])
            removal_bytes = app._gemini_image_jpeg(removal_prompt, aspect_ratio="9:16", reference_image={"mime_type": "image/jpeg", "data": b64encode(master_bytes).decode("ascii")})
            removal_path = stage_dir / "registered-removal-source.jpg"
            removal_path.write_bytes(removal_bytes)
            component_request = "\n".join(f"- {item['id']}: {item['description']}" for item in plan["components"])
            layout_prompt = f"""
Inspect this master photograph. Return JSON only using the supplied schema.
{component_request}

Set `singleCoherentPhotograph=true` only for one uninterrupted camera view with continuous perspective, horizon, deck/floor and architecture. Set `visibleSeamsOrPanels=true` for any patch, quadrant, split, pasted region, broken structural line, or picture-in-picture boundary.
For each exact component, return visibility, physical integration, and a tight `[left,top,right,bottom]` bbox in 0..1000 coordinates. `physicallyIntegrated` is true only when grounded on a visible surface or attached to continuous architecture with correct contact, perspective, light, and shadow.
""".strip()
            layout = app._gemini_text_json_with_image(layout_prompt, master_bytes, "image/jpeg", app.REGISTERED_SCENE_LAYOUT_SCHEMA, temperature=0.1)
            specs = app.normalize_registered_scene_layout(layout, plan)
            specs_path = stage_dir / "layer-specs.json"
            specs_path.write_text(json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8")
            worker = subprocess.run(
                [sys.executable, str(app.BASE_DIR / "registered_scene.py"), "--clean", str(clean_path), "--removal", str(removal_path), "--master", str(master_path), "--specs", str(specs_path), "--output-dir", str(stage_dir)],
                capture_output=True, text=True, timeout=720, check=False,
            )
            if worker.returncode:
                raise RuntimeError((worker.stderr or worker.stdout)[-1600:])
            result = json.loads(worker.stdout.strip().splitlines()[-1])
            manifest = result["pack"]
            return {
                "path": str(stage_dir),
                "manifest": manifest,
                "plan": plan,
                "masterReference": {"mime_type": "image/jpeg", "data": b64encode(master_bytes).decode("ascii")},
                "attempt": attempt,
            }
        except Exception as error:
            errors.append(str(error))
    raise RuntimeError(f"Stage {stage_id} failed production validation: {' | '.join(errors)[-2400:]}")


def main(site_id=7, post_id=32):
    with app.db() as conn:
        post = conn.execute("select * from social_posts where id=? and site_id=?", (post_id, site_id)).fetchone()
        site = conn.execute("select * from sites where id=?", (site_id,)).fetchone()
        job = conn.execute("select * from content_jobs where id=? and site_id=?", (post["job_id"], site_id)).fetchone() if post else None
    if not post or not site or not job:
        raise RuntimeError("Production Reel source not found")
    old_payload = app.parse_json_object(post["content_json"])
    old_reel = old_payload.get("instagramReel") or {}
    storyboard = old_reel.get("storyboard") or app.generate_instagram_reel_storyboard(site, job, app.content_job_language(job, site))
    old_asset_key = old_reel.get("assetKey")
    old_asset_dir = app.instagram_reel_asset_dir(site_id, old_asset_key)
    existing_v5 = sorted(
        (app.SOCIAL_ASSET_DIR / str(site_id)).glob(f"{job['id']}-registered-v5-*"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    asset_key = existing_v5[0].name if existing_v5 else app.social_asset_key(job["id"] + "-registered-v5")
    asset_dir = app.instagram_reel_asset_dir(site_id, asset_key)
    asset_dir.mkdir(parents=True, exist_ok=True)
    old_reel["progress"] = {"phase": "registered_assets", "scene": 0, "totalScenes": 7, "message": "Building three production master scenes"}
    old_payload["instagramReel"] = old_reel
    app._save_instagram_reel_payload(post_id, old_payload, "GENERATING")
    try:
        stages = {}
        identity = None
        for stage_id in (1, 2, 3):
            stage = generate_stage(site, job, storyboard, stage_id, asset_dir, identity)
            identity = stage.pop("masterReference")
            stages[stage_id] = stage
            old_reel["progress"] = {"phase": "registered_assets", "scene": 2 if stage_id == 1 else 4 if stage_id == 2 else 7, "totalScenes": 7, "message": f"Production master stage {stage_id} passed"}
            app._save_instagram_reel_payload(post_id, old_payload, "GENERATING")
        visibility = [1, 3, 1, 3, 1, 2, 3]
        appearances = [["focus"], ["wipe_up", "light_sweep"], ["wipe_right"], ["radial", "wipe_up"], ["focus"], ["light_sweep"], ["radial"]]
        production_scenes = []
        for index, scene in enumerate(storyboard["scenes"]):
            stage_id = int(scene["stageId"])
            protagonist_zone = next(item["zone"] for item in stages[stage_id]["plan"]["components"] if item["role"] == "protagonist")
            text_side = "right" if protagonist_zone == "left_subject" else "left"
            voice_path = old_asset_dir / f"scene-{index + 1:02d}-voice.wav"
            production_scenes.append({
                **scene,
                "composition": {"textPlacement": f"top_{text_side}" if index < 6 else f"lower_{text_side}"},
                "voicePath": str(voice_path),
                "visibleLayerCount": visibility[index],
                "appearances": appearances[index],
            })
        music_track = app.get_active_reel_music_track(site_id)
        music_path = app.reel_music_track_path(music_track)
        render = render_registered_reel(stages, production_scenes, asset_dir / "instagram-reel.mp4", asset_dir / "render-work", app._reel_accent(site_id), music_path=music_path)
        registered_stages = []
        for stage_id, stage in stages.items():
            stage_root = Path(stage["path"])
            registered_stages.append({
                "stageId": stage_id,
                "plan": stage["plan"],
                "attempt": stage["attempt"],
                "manifest": stage["manifest"],
                "masterUrl": f"/sites/{site_id}/social-assets/{asset_key}/instagram/stage-{stage_id:02d}/registered-master.jpg",
            })
        old_reel.update({
            "version": 5,
            "assetKey": asset_key,
            "storyboard": storyboard,
            "motionSystem": "master-derived registered scenes, varied mask reveals, whole-scene camera movement, kinetic type",
            "registeredStages": registered_stages,
            "videoUrl": app.social_asset_url(site_id, asset_key, "instagram", "instagram-reel.mp4"),
            "coverUrl": app.social_asset_url(site_id, asset_key, "instagram", "instagram-reel.jpg"),
            "durationSeconds": render["durationSeconds"],
            "fps": render["fps"],
            "musicMode": render["musicMode"],
            "progress": {"phase": "ready", "scene": 7, "totalScenes": 7, "message": "Registered production Reel is ready for review"},
        })
        old_reel.pop("error", None)
        validation = {
            "version": 5,
            "scenes": 7,
            "stages": 3,
            "registeredLayers": True,
            "cameraMoves": [scene["cameraMove"] for scene in production_scenes],
            "appearances": appearances,
            "published": False,
        }
        old_payload["validation"] = validation
        with app.db() as conn:
            conn.execute("update social_posts set content_text=?,content_json=?,status='DRAFT',validation_json=?,char_count=?,updated_at=? where id=?", (storyboard["caption"], json.dumps(old_payload, ensure_ascii=False), json.dumps(validation, ensure_ascii=False), len(storyboard["caption"]), app.now_iso(), post_id))
            conn.execute("insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)", (site_id, job["id"], app.now_iso(), "INFO", "instagram-reel-v5", "Rendered real master-derived registered production Reel; left unpublished for review"))
        print(json.dumps({"ok": True, "postId": post_id, "assetKey": asset_key, "videoUrl": old_reel["videoUrl"], "duration": render["durationSeconds"], "stages": [{"id": item["stageId"], "attempt": item["attempt"], "layers": len(item["manifest"]["layers"])} for item in registered_stages]}, ensure_ascii=False))
    except Exception as error:
        old_reel["progress"] = {"phase": "error", "scene": old_reel.get("progress", {}).get("scene", 0), "totalScenes": 7, "message": str(error)[:900]}
        old_reel["error"] = str(error)[:1600]
        app._save_instagram_reel_payload(post_id, old_payload, "ERROR")
        raise


if __name__ == "__main__":
    main()
