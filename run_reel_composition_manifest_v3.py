import json
import os
import sys
import time

sys.path.insert(0, "/var/www/blog.yas.ooo")
import app


SITE_ID = 7
JOB_ID = "0a9d3ddba2653f160592e281"
PLAN_DIR = "/tmp/solocruz-reel-text-plan"
ARCHITECTURE_FILE = os.path.join(PLAN_DIR, "01-architecture-v2.json")
COMPOSITION_FILE = os.path.join(PLAN_DIR, "02-composition-contract-v3.json")
MANIFEST_FILE = os.path.join(PLAN_DIR, "03-technical-manifest-v3.json")


def save_json(path, value):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)


with app.db() as connection:
    site = connection.execute("select * from sites where id=?", (SITE_ID,)).fetchone()
    job = connection.execute(
        "select * from content_jobs where site_id=? and id=?", (SITE_ID, JOB_ID)
    ).fetchone()

if not site or not job:
    raise RuntimeError("SoloCruz source article is unavailable")

with open(ARCHITECTURE_FILE, encoding="utf-8") as handle:
    architecture = json.load(handle)

language = app.content_job_language(job, site)
print(json.dumps({"step": 2, "status": "running", "media": "disabled"}), flush=True)
started = time.monotonic()
errors = []
manifest = None
for attempt in range(1, 4):
    retry = ""
    if errors:
        retry = (
            "\n\nThe previous complete contract did not pass the universal production validator: "
            + errors[-1]
            + ". Return a new complete contract. Preserve the locked article architecture; "
              "make every component footprint independently legible in its assigned zone."
        )
    composition = app._gemini_text_json(
        app.build_instagram_reel_composition_contract_prompt(site, job, language, architecture) + retry,
        response_schema=app.INSTAGRAM_REEL_COMPOSITION_CONTRACT_SCHEMA,
        temperature=0.25,
        repair=False,
    )
    save_json(COMPOSITION_FILE, composition)
    print(json.dumps({"step": 2, "status": "candidate", "attempt": attempt, "seconds": round(time.monotonic() - started, 1)}), flush=True)
    print(json.dumps({"step": 3, "status": "validating", "attempt": attempt, "media": "disabled"}), flush=True)
    try:
        manifest = app.compile_instagram_reel_technical_manifest(composition, architecture)
        break
    except ValueError as error:
        errors.append(str(error))
else:
    raise RuntimeError("technical manifest did not pass after three text-only composition attempts: " + " | ".join(errors))

print(json.dumps({"step": 2, "status": "saved", "attempts": len(errors) + 1, "seconds": round(time.monotonic() - started, 1)}), flush=True)
save_json(MANIFEST_FILE, manifest)
print(
    json.dumps(
        {
            "step": 3,
            "status": "saved",
            "scenes": manifest["sceneCount"],
            "assetJobs": sum(len(scene["assets"]) for scene in manifest["scenes"]),
            "media": "disabled",
        }
    ),
    flush=True,
)
