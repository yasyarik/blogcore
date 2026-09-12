import json
import os
import sys
import time

sys.path.insert(0, "/var/www/blog.yas.ooo")
import app


PLAN_DIR = "/tmp/solocruz-reel-locked-test"
with open(os.path.join(PLAN_DIR, "01-architecture.json"), encoding="utf-8") as handle:
    architecture = json.load(handle)
with open(os.path.join(PLAN_DIR, "02-scene-skeleton.json"), encoding="utf-8") as handle:
    skeleton = json.load(handle)

with app.db() as conn:
    site = conn.execute("select * from sites where id=7").fetchone()
    job = conn.execute(
        "select * from content_jobs where site_id=7 and id=?",
        ("0a9d3ddba2653f160592e281",),
    ).fetchone()

started = time.monotonic()


def report_progress(completed, total, _scene):
    print(json.dumps({"progress": completed, "total": total, "media": "disabled"}), flush=True)


detailed = app.elaborate_instagram_reel_scenes(
    site,
    job,
    app.content_job_language(job, site),
    architecture,
    skeleton,
    progress_callback=report_progress,
)

assert len(detailed) == len(skeleton["scenes"])
scene_fields = (
    "stageId",
    "coveredBeatIds",
    "durationSeconds",
    "cameraMove",
    "composition",
    "usesLogoReference",
    "stageBackgroundPrompt",
    "visualStory",
    "stateAtStart",
    "stateAtEnd",
    "transitionFromPrevious",
)
layer_fields = ("id", "role", "sourceEvidence", "action", "emotion", "relationship")
for scene_index, (locked, result) in enumerate(zip(skeleton["scenes"], detailed), start=1):
    for field in scene_fields:
        assert result.get(field) == locked.get(field), (scene_index, field)
    assert len(result["layers"]) == len(locked["layers"]), scene_index
    for layer_index, (input_layer, output_layer) in enumerate(zip(locked["layers"], result["layers"]), start=1):
        for field in layer_fields:
            if input_layer.get(field) not in (None, ""):
                assert output_layer.get(field) == input_layer.get(field), (scene_index, layer_index, field)
        assert output_layer.get("id") == (input_layer.get("id") or f"element-{layer_index:02d}")

output = {
    "sourceArchitecture": architecture,
    "approvedScenePlan": skeleton,
    "productionScenes": detailed,
    "sceneCount": len(detailed),
    "mediaGenerated": False,
}
output_path = os.path.join(PLAN_DIR, "03-production-plan-locked.json")
with open(output_path, "w", encoding="utf-8") as handle:
    json.dump(output, handle, ensure_ascii=False, indent=2)
print(json.dumps({
    "status": "accepted",
    "seconds": round(time.monotonic() - started, 1),
    "scenes": len(detailed),
    "output": output_path,
    "media": "disabled",
}))
