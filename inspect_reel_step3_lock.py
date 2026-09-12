import json
import os
import sys

sys.path.insert(0, "/var/www/blog.yas.ooo")
import app

plan_dir = "/tmp/solocruz-reel-locked-test"
architecture = json.load(open(os.path.join(plan_dir, "01-architecture.json"), encoding="utf-8"))
skeleton = json.load(open(os.path.join(plan_dir, "02-scene-skeleton.json"), encoding="utf-8"))
with app.db() as conn:
    site = conn.execute("select * from sites where id=7").fetchone()
    job = conn.execute("select * from content_jobs where site_id=7 and id=?", ("0a9d3ddba2653f160592e281",)).fetchone()

candidate = app._gemini_text_json(
    app.build_instagram_reel_scene_detail_prompt(site, job, app.content_job_language(job, site), architecture, skeleton, 0, []),
    response_schema=app.INSTAGRAM_REEL_VISUAL_SCENE_SCHEMA,
    temperature=0.1,
    repair=False,
)
app.hydrate_instagram_reel_architecture_copy({"scenes": [candidate]}, architecture)
locked = skeleton["scenes"][0]
scene_fields = ("stageBackgroundPrompt", "visualStory", "stateAtStart", "stateAtEnd", "transitionFromPrevious")
layer_fields = ("id", "role", "sourceEvidence", "action", "emotion", "relationship")
diffs = []
for field in scene_fields:
    if candidate.get(field) != locked.get(field):
        diffs.append({"field": field, "locked": locked.get(field), "candidate": candidate.get(field)})
for index, (before, after) in enumerate(zip(locked.get("layers") or [], candidate.get("layers") or []), 1):
    for field in layer_fields:
        if after.get(field) != before.get(field):
            diffs.append({"field": f"layers[{index}].{field}", "locked": before.get(field), "candidate": after.get(field)})
json.dump(candidate, open(os.path.join(plan_dir, "03-candidate-debug.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(diffs, open(os.path.join(plan_dir, "03-lock-diffs.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps({"diffCount": len(diffs), "diffFields": [item["field"] for item in diffs], "media": "disabled"}))
