import json
import os
import sys

sys.path.insert(0, "/var/www/blog.yas.ooo")
import app

SITE_ID = 7
JOB_ID = "0a9d3ddba2653f160592e281"
PLAN_DIR = "/tmp/solocruz-reel-text-plan"

with app.db() as conn:
    site = conn.execute("select * from sites where id=?", (SITE_ID,)).fetchone()
    job = conn.execute("select * from content_jobs where site_id=? and id=?", (SITE_ID, JOB_ID)).fetchone()
with open(os.path.join(PLAN_DIR, "01-architecture-v2.json"), encoding="utf-8") as handle:
    architecture = json.load(handle)

language = app.content_job_language(job, site)
scenes = []
for number, beat in enumerate(architecture["beats"], 1):
    single = dict(architecture)
    single["beats"] = [beat]
    errors = []
    for attempt in range(1, 4):
        prompt = app.build_instagram_reel_composition_contract_prompt(site, job, language, single)
        prompt += f"\n\nPLAN ONLY locked scene {number} of {len(architecture['beats'])}. Use exactly background-{number:02d} and component IDs ending in -{number:02d}-NN."
        if errors:
            prompt += "\nThe prior candidate violated the universal manifest contract: " + errors[-1] + ". Re-plan this one scene with distinct, legible components."
        raw = app._gemini_text_json(prompt, response_schema=app.INSTAGRAM_REEL_COMPOSITION_CONTRACT_SCHEMA, temperature=0.2, repair=False)
        candidate = raw.get("scenes", [None])[0]
        with open(os.path.join(PLAN_DIR, f"v4-scene-{number:02d}-attempt-{attempt}.json"), "w", encoding="utf-8") as handle:
            json.dump(candidate, handle, ensure_ascii=False, indent=2)
        try:
            app.compile_instagram_reel_technical_manifest({"scenes": [candidate]}, single)
            scenes.append(candidate)
            print(json.dumps({"scene": number, "status": "accepted", "attempt": attempt}), flush=True)
            break
        except ValueError as error:
            errors.append(str(error))
    else:
        raise RuntimeError(f"scene {number} rejected: {' | '.join(errors)}")

manifest = app.compile_instagram_reel_technical_manifest({"scenes": scenes}, architecture)
with open(os.path.join(PLAN_DIR, "03-technical-manifest-v4.json"), "w", encoding="utf-8") as handle:
    json.dump(manifest, handle, ensure_ascii=False, indent=2)
print(json.dumps({"status": "complete", "scenes": manifest["sceneCount"], "media": "disabled"}), flush=True)
