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
    job = conn.execute("select * from content_jobs where site_id=7 and id=?", ("0a9d3ddba2653f160592e281",)).fetchone()

single = dict(skeleton)
single["scenes"] = [skeleton["scenes"][0]]
started = time.monotonic()
detailed = app.elaborate_instagram_reel_scenes(
    site,
    job,
    app.content_job_language(job, site),
    architecture,
    single,
)
result = detailed[0]
locked = single["scenes"][0]
immutable_fields = ("stageBackgroundPrompt", "visualStory", "stateAtStart", "stateAtEnd", "transitionFromPrevious")
layer_fields = ("id", "role", "sourceEvidence", "action", "emotion", "relationship")
assert all(result.get(field) == locked.get(field) for field in immutable_fields)
assert len(result["layers"]) == len(locked["layers"])
assert all(
    all(
        output_layer.get(field) == input_layer.get(field)
        for field in layer_fields
        if input_layer.get(field) not in (None, "")
    )
    and output_layer.get("id") == (input_layer.get("id") or f"element-{index:02d}")
    for index, (input_layer, output_layer) in enumerate(zip(locked["layers"], result["layers"]), start=1)
)
output_path = os.path.join(PLAN_DIR, "03-scene-01-locked.json")
with open(output_path, "w", encoding="utf-8") as handle:
    json.dump(result, handle, ensure_ascii=False, indent=2)
print(json.dumps({"status": "accepted", "seconds": round(time.monotonic() - started, 1), "output": output_path, "media": "disabled"}))
