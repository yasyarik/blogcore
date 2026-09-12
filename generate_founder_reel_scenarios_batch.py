#!/usr/bin/env python3
"""Create unique founder-Reel scenarios for existing YAS vacancy evidence drafts.

The text stage is one Gemini 3.7 Flash Batch job.  It creates plans only;
Omni media generation is deliberately a separate queued stage.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import app

SITE_ID = 12
OUT_DIR = Path("data/founder_reel_scenarios")
# These two have already been designed and rendered as the approved test cases.
EXCLUDED_SOURCE_POST_IDS = {146, 147}

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "caption": {"type": "string"},
        "engagementAction": {"type": "string", "enum": ["follow", "comment", "share"]},
        "frames": {
            "type": "array",
            "minItems": 4,
            "maxItems": 4,
            "items": {
                "type": "object",
                "properties": {"label": {"type": "string"}, "direction": {"type": "string"}},
                "required": ["label", "direction"],
            },
        },
        "clips": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "speech": {"type": "string"}, "direction": {"type": "string"}},
                "required": ["name", "speech", "direction"],
            },
        },
    },
    "required": ["title", "caption", "engagementAction", "frames", "clips"],
}


def prompt_for(row) -> str:
    text = str(row["content_text"] or "").strip()
    return f"""You are creating one original 30-second founder-led Instagram Reel for YAS, a company that builds bespoke software systems to remove repetitive business work. The source is a verified job-description insight, not an accusation or a claim about the employer's internal systems.

Source vacancy draft (use its actual company, role, problem and proposed custom-system direction; do not invent facts):
{text}

Return strict JSON only, matching the schema.

The Reel must make an ordinary business viewer understand the job and operational bottleneck, then show a concrete bespoke-system answer. It is founder-led: the same approved founder is the only person on screen. His portrait fixes his identity only. Each of the four generated boundary frames may use a different meaningful location, interior, wardrobe, action, lighting and camera approach. Do not recycle a generic dark studio. Make each location a physical metaphor for this specific workflow.

Create exactly four frame directions in this order: start, boundary-01, boundary-02, end. The end direction must reserve a clean lower-third for exactly one real YAS logo and final CTA; other frames must explicitly prohibit a YAS logo and CTA.

Create exactly three 10-second clips named clip-01, clip-02 and clip-03. Every spoken line must be 16-20 English words, complete, natural and understandable. Never cut a sentence to fit. Speech starts around 0.3s and ends near 9.5s.

Narrative rules:
- clip-01 is a strong plain-language hook only. No brand, company logo, CTA, website or engagement request.
- clip-02 names the real company and job purpose, then uses exactly one engagement action selected intelligently: FOLLOW for a recurring pattern, COMMENT for a genuine decision/experience question, SHARE for a specific colleague/team who would benefit. No YAS logo, website or final CTA.
- clip-03 shows a concrete custom-system flow and ends with exactly one final CTA plus yas.ooo and exactly one YAS logo. Do not repeat company branding here.

Visual rules for every clip direction:
- everything (speech, readable type, company wordmark if used, physical evidence objects, diagram, CTA, YAS logo) must be generated natively inside Omni; never describe external overlays or compositing;
- use one clear physical/editorial visual idea per clip, not dashboard fiction;
- state exact on-screen copy; keep each key text and graphic fully visible for at least 3.5 seconds, and specify its hold window;
- no extra people, no fake UI, no tiny text, no distorted hands, no face crop, no irrelevant B-roll;
- the company wordmark may appear once only in clip-02 where it identifies the source vacancy;
- no unsupported business-outcome claims. If including time/money, label it illustrative and explain the model in the caption.

The Instagram caption must be self-contained, accurate to the source, explain the custom-system approach, and match the selected engagement action."""


def main() -> None:
    with app.db() as conn:
        rows = conn.execute(
            """select id,job_id,content_text,content_json from social_posts
               where site_id=? and channel='twitter' and status='DRAFT'
                 and asset_type like 'evidence_post%'
               order by id""",
            (SITE_ID,),
        ).fetchall()
    rows = [row for row in rows if int(row["id"]) not in EXCLUDED_SOURCE_POST_IDS]
    requests = {str(row["id"]): prompt_for(row) for row in rows}
    results, batch_name = app._gemini_batch_text_json(requests, response_schema=SCHEMA, temperature=0.25, timeout=7200)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for row in rows:
        plan = results[str(row["id"])]
        if [item.get("label") for item in plan["frames"]] != ["start", "boundary-01", "boundary-02", "end"]:
            raise RuntimeError(f"Plan {row['id']} has invalid frame order")
        if [item.get("name") for item in plan["clips"]] != ["clip-01", "clip-02", "clip-03"]:
            raise RuntimeError(f"Plan {row['id']} has invalid clip order")
        for clip in plan["clips"]:
            count = len(re.findall(r"[\w’'-]+", str(clip["speech"] or ""), flags=re.UNICODE))
            if not 16 <= count <= 20:
                raise RuntimeError(f"Plan {row['id']} {clip['name']} has {count} spoken words, not 16-20")
        plan.update({"sourcePostId": int(row["id"]), "jobId": row["job_id"], "siteId": SITE_ID, "model": "gemini-3.7-flash", "batch": batch_name})
        path = OUT_DIR / f"{int(row['id'])}.json"
        path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        saved.append({"sourcePostId": int(row["id"]), "path": str(path), "title": plan["title"]})
    print(json.dumps({"ok": True, "batch": batch_name, "model": "gemini-3.7-flash", "scenarios": saved}, ensure_ascii=False))


if __name__ == "__main__":
    main()
