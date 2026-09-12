import json
import os
import sys
import time

sys.path.insert(0, "/var/www/blog.yas.ooo")
import app


PLAN_DIR = "/tmp/solocruz-reel-locked-test"
architecture = json.load(open(os.path.join(PLAN_DIR, "01-architecture.json"), encoding="utf-8"))
skeleton = json.load(open(os.path.join(PLAN_DIR, "02-scene-skeleton.json"), encoding="utf-8"))
detailed_bundle = json.load(open(os.path.join(PLAN_DIR, "03-production-plan-locked.json"), encoding="utf-8"))
detailed = detailed_bundle["productionScenes"]

with app.db() as conn:
    site = conn.execute("select * from sites where id=7").fetchone()
    job = conn.execute(
        "select * from content_jobs where site_id=7 and id=?",
        ("0a9d3ddba2653f160592e281",),
    ).fetchone()


def progress(completed, total, _scene):
    print(json.dumps({"manifestProgress": completed, "total": total, "media": "disabled"}), flush=True)


started = time.monotonic()
manifest = app.generate_instagram_reel_step3_asset_manifest(
    site,
    job,
    app.content_job_language(job, site),
    skeleton,
    detailed,
    progress_callback=progress,
)
manifest["approvedScenePlan"] = skeleton
output_path = os.path.join(PLAN_DIR, "03-gemini-asset-manifest.json")
with open(output_path, "w", encoding="utf-8") as handle:
    json.dump(manifest, handle, ensure_ascii=False, indent=2)
print(json.dumps({
    "status": "accepted",
    "seconds": round(time.monotonic() - started, 1),
    "scenes": manifest["sceneCount"],
    "output": output_path,
    "media": "disabled",
}))
