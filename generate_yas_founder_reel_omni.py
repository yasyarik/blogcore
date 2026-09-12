#!/usr/bin/env python3
"""Generate a founder-led Reel with Gemini Omni 1.1 Flash.

The source portrait is used only to create boundary frames. Omni receives only
those generated frames; every title, graphic, CTA and logo is native to Omni.

Narrative placement is fixed for every Reel:
  1. opening: hook only;
  2. middle: explanation plus a follow invitation;
  3. ending: solution, explicit CTA and exactly one YAS logo.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

OMNI_MODEL = "gemini-omni-1.1-flash"
FRAME_MODEL = "gemini-3.1-flash-image"
VOICE_NAME = "Charon"
PORTRAIT = Path(os.environ.get("FOUNDER_PORTRAIT", "yas-portrait-poster.webp"))
YAS_LOGO = Path(os.environ.get("YAS_LOGO_REFERENCE", "/var/www/blog.yas.ooo/assets-yas-header-logo.png"))
OUT = Path(os.environ.get("FOUNDER_REEL_OUT", "output/yas-founder-notion-omni.mp4"))
CASE = os.environ.get("FOUNDER_REEL_CASE", "notion_detection").strip().lower()
PLAN_PATH = Path(os.environ["FOUNDER_REEL_PLAN"]) if os.environ.get("FOUNDER_REEL_PLAN") else None

FRAME_COMMON = """Use the attached founder portrait as the mandatory identity reference. Preserve the exact face, glasses, hairstyle, beard and apparent age. This reference fixes the person, not the setting: choose the location, interior, clothing, lighting, action and camera treatment that make this exact story beat visually clear. The founder must be visibly plausible in the chosen situation, normally waist-up to three-quarter length, with full face and shoulders inside the 9:16 frame. Maintain believable continuity between adjacent frames, but do not force one background, one wardrobe or one camera setup across the Reel. No words, no readable UI, no watermark, no extra people, no cropped face, no distorted hands. This is a clean source frame only: all typography, brands, diagrams and calls to action will be generated natively by Omni later."""

NOTION_FRAMES = [
    ("start", "At night in a realistic security operations room, founder in a dark overshirt stands beside a wall of softly defocused telemetry screens. He is alert, looking directly at camera. The left side has clean negative space prepared for a native visual of a threat signal failing to enter a collection path."),
    ("boundary-01", "Founder now sits at a clean daylight investigation table in a charcoal shirt, matching the same person and calm authority. A physical printed threat report and a single disconnected evidence cable are visible in the scene. Keep room on the left for a native editorial explanation. Do not place a logo or CTA in this frame."),
    ("boundary-02", "Founder stands in a bright architectural briefing room wearing a dark blazer again, gesturing toward a real translucent three-step evidence path on the wall: input, coverage check, human approval. This is an editorial physical object, not a software dashboard. Do not place a logo or CTA in this frame."),
    ("end", "Founder is in a warm, minimal founder office at sunset, seated naturally at a table and looking calmly and invitingly into camera. The complete physical evidence path rests on the table. Keep a large clean lower-third area reserved only for the native final CTA and one YAS mark."),
]

NOTION_CLIPS = [
    ("clip-01", "Perfect rules still miss attacks when systems never collect the evidence that would expose the attacker in the first place.", "OPENING — HOOK ONLY. 10-second clip. Founder begins speaking at 0.3s and finishes close to 9.5s: no long silent opening or ending. While he speaks, create native, large, crisp on-video typography on the left reading exactly: YOU CAN'T DETECT WHAT YOU DON'T COLLECT. Reveal it as a physical editorial signal path breaking before collection. Do not show any company logo, follow invitation, CTA, website or YAS branding in this opening."),
    ("clip-02", "Notion is hiring someone to verify that the data needed to spot an attack exists before detection rules are written and deployed.", "MIDDLE — EXPLAIN THE VACANCY AND CHOOSE ONE RELEVANT ENGAGEMENT ACTION. 10-second clip. Founder begins speaking at 0.3s and finishes close to 9.5s. Create an integrated native editorial insert on the left: the genuine Notion wordmark once, followed by the readable heading NOTION IS HIRING FOR THIS. Under it, show one large concise evidence card: THREAT REPORT → MISSING LOGS. This case teaches a recurring workflow pattern, so at 7.2s show only this mid-video invitation in large readable type: FOLLOW FOR REAL WORKFLOW BREAKDOWNS. Do not add a comment or share invitation. This is not a final CTA: do not show YAS logo or website."),
    ("clip-03", "A custom coverage system checks sources automatically, flags blind spots, and gives the engineer only detection rules ready for informed approval.", "ENDING — SOLUTION, CTA AND BRAND ONLY HERE. 10-second clip. Founder begins speaking at 0.3s and finishes close to 9.5s. Build a native animated explanatory graphic alongside him with exactly three large labels: THREAT REPORT → COVERAGE CHECK → HUMAN APPROVAL. At 6.5s replace it with a strong, readable final CTA: COMMENT: WHAT WOULD YOU AUTOMATE? Show https://yas.ooo and exactly one clean YAS logo once with that final CTA. Do not repeat a company logo here. All typography, logo, graphic, inserts and transitions are generated inside Omni, never added after generation."),
]

FIGMA_FRAMES = [
    ("start", "Founder is standing in a dramatic daylight product-test workshop, wearing a slate work jacket. On a large physical wall map, three different vulnerability reports arrive through separate visible routes but stop before reaching one engineer's desk. Keep the upper left open for a native hook. No logo or CTA."),
    ("boundary-01", "Founder is seated at a tactile round review table in a refined Figma-like design studio, wearing a simple black shirt. Three real physical evidence objects sit clearly apart: a bug-bounty report envelope, a penetration-test folder and a scanner alert beacon. Keep room beside them for a native editorial label. No logo or CTA."),
    ("boundary-02", "Founder walks through a warm modern engineering library, now in a dark blazer, beside a large physical sorting wall that turns three scattered evidence objects into one ordered investigation packet. Keep it artistic, concrete and understandable rather than a dashboard. No logo or CTA."),
    ("end", "Founder stands on a quiet rooftop terrace at blue hour, in a dark open-collar shirt, holding one complete investigation packet. The city lights are softly behind him. Reserve a clean lower third only for final native CTA and one unchanged YAS logo."),
]

FIGMA_CLIPS = [
    ("clip-01", "Three vulnerability sources should not make one security engineer become the manual switchboard between them all.", "OPENING — HOOK ONLY. 10-second clip. Founder speaks from 0.3s to near 9.5s. Show the large native text exactly: THREE SOURCES. ONE MANUAL BOTTLENECK. Hold this text continuously from 1.0s through 6.0s. Beside it, keep one readable physical editorial visual of three source routes stopping before one human desk visible for at least 5 seconds. No company logo, follow request, CTA, YAS logo or website."),
    ("clip-02", "Figma is hiring a Security Engineer to triage reports from bug bounty, penetration tests, and internal scanners before engineering can fix them.", "MIDDLE — EXPLAIN THE VACANCY AND USE ONE RELEVANT ENGAGEMENT ACTION. 10-second clip. Founder speaks from 0.3s to near 9.5s. Show the genuine Figma wordmark once and the exact large heading: FIGMA IS HIRING FOR THIS. Hold both from 1.0s through 5.0s. Then hold one clear physical evidence trio labelled exactly: BUG BOUNTY + PENTEST + SCANNER from 4.0s through 8.0s. This role is directly relevant to security and engineering teammates, so at 7.0s show only: SHARE WITH THE TEAM THAT OWNS TRIAGE. Hold it until the end. No YAS logo, website or final CTA."),
    ("clip-03", "A custom triage system normalizes every report, finds the affected code owner, and sends engineers one review-ready investigation packet.", "ENDING — SOLUTION, CTA AND BRAND ONLY HERE. 10-second clip. Founder speaks from 0.3s to near 9.5s. Build one native physical before-to-after sorting graphic and hold it continuously from 1.0s through 6.5s, with exactly these large labels: THREE INTAKES → ONE REVIEW PACKET. At 6.5s change once to the final CTA, held through 10.0s: COMMENT: WHAT TRIAGE STEP WASTES YOUR TEAM'S TIME? Show https://yas.ooo and exactly one clean unchanged YAS logo with that final CTA. Do not repeat the Figma logo. All elements are native inside Omni, never overlays."),
]

if PLAN_PATH:
    if not PLAN_PATH.is_file():
        raise RuntimeError(f"Founder Reel plan is missing: {PLAN_PATH}")
    PLAN = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    FRAMES = [(str(item["label"]), str(item["direction"])) for item in PLAN.get("frames") or []]
    CLIPS = [(str(item["name"]), str(item["speech"]), str(item["direction"])) for item in PLAN.get("clips") or []]
    if [item[0] for item in FRAMES] != ["start", "boundary-01", "boundary-02", "end"]:
        raise RuntimeError("Founder Reel plan must have start, boundary-01, boundary-02 and end frames")
    if [item[0] for item in CLIPS] != ["clip-01", "clip-02", "clip-03"]:
        raise RuntimeError("Founder Reel plan must have exactly clip-01, clip-02 and clip-03")
elif CASE == "figma_triage":
    FRAMES, CLIPS = FIGMA_FRAMES, FIGMA_CLIPS
elif CASE == "notion_detection":
    FRAMES, CLIPS = NOTION_FRAMES, NOTION_CLIPS
else:
    raise RuntimeError(f"Unknown founder Reel case: {CASE}")


def post_json(url: str, payload: dict, headers: dict, timeout: int) -> dict:
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")
        raise RuntimeError(f"Google HTTP {error.code}: {detail[:3000]}") from error


def make_frame(api_key: str, label: str, direction: str) -> Path:
    output = OUT.with_name(f"{OUT.stem}-{label}.jpg")
    if output.is_file() and output.stat().st_size > 50_000:
        return output
    is_final_frame = label == "end"
    if is_final_frame and not YAS_LOGO.is_file():
        raise RuntimeError(f"YAS logo reference is missing: {YAS_LOGO}")
    reference_instruction = (
        "Attached Image 1 is the founder identity reference. Attached Image 2 is the real YAS logo reference. "
        "For this final boundary frame, reproduce Image 2 exactly once, unchanged and fully legible in the reserved lower third. "
        "Do not redraw, reinterpret, duplicate, crop, stylize or replace the logo."
        if is_final_frame else
        "Attached Image 1 is the founder identity reference."
    )
    parts = [
        {"text": f"{reference_instruction}\n\n{FRAME_COMMON}\n\nSpecific frame: {direction}"},
        {"inlineData": {"mimeType": "image/webp", "data": base64.b64encode(PORTRAIT.read_bytes()).decode("ascii")}},
    ]
    if is_final_frame:
        parts.append({"inlineData": {"mimeType": "image/png", "data": base64.b64encode(YAS_LOGO.read_bytes()).decode("ascii")}})
    payload = {"contents": [{"role": "user", "parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "9:16"}}}
    url = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}".format(urllib.parse.quote(FRAME_MODEL, safe=".-"), urllib.parse.quote(api_key, safe=""))
    data = post_json(url, payload, {"content-type": "application/json"}, 300)
    parts = ((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
    encoded = next(((part.get("inlineData") or {}).get("data") for part in parts if (part.get("inlineData") or {}).get("data")), None)
    if not encoded:
        raise RuntimeError(f"Frame {label} has no image output: {str(data)[:1000]}")
    output.write_bytes(base64.b64decode(encoded))
    return output


def make_clip(api_key: str, index: int, first: Path, last: Path) -> Path:
    name, speech, direction = CLIPS[index]
    output = OUT.with_name(f"{OUT.stem}-{name}.mp4")
    if output.is_file() and output.stat().st_size > 100_000:
        return output
    prompt = f'''[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image2]
Use Image1 as the exact first frame and Image2 as the exact last frame. Create a smooth continuous transition between them. {direction}

Spoken dialogue — exactly and only this, voiced by the configured preset voice {VOICE_NAME}: "{speech}". The specified typography, logo, evidence card, editorial inserts and explanatory graphics are required native elements inside this Omni-generated video. Critical text and graphics must remain static, fully in-frame and readable for their explicitly stated hold time; do not flash, shrink or replace them early. Do not add any other text, other voices, fake UI, watermarks or extra people. Keep the founder's face in frame at all times; no face crop, no unexpected body distortion, no shaky camera. The final decoded frame must match Image2 exactly.'''
    payload = {
        "model": OMNI_MODEL,
        "input": [
            {"type": "image", "data": base64.b64encode(first.read_bytes()).decode("ascii"), "mime_type": "image/jpeg"},
            {"type": "image", "data": base64.b64encode(last.read_bytes()).decode("ascii"), "mime_type": "image/jpeg"},
            {"type": "text", "text": prompt},
        ],
        "response_format": {"type": "video", "aspect_ratio": "9:16", "resolution": "720p"},
        "generation_config": {"video_config": {"task": "image_to_video"}},
    }
    data = post_json("https://generativelanguage.googleapis.com/v1beta/interactions", payload, {"content-type": "application/json", "x-goog-api-key": api_key}, 900)
    encoded = ((data.get("output_video") or {}).get("data"))
    if not encoded:
        for step in data.get("steps") or []:
            for content in step.get("content") or []:
                if content.get("type") == "video" and content.get("data"):
                    encoded = content["data"]
                    break
            if encoded:
                break
    if not encoded:
        raise RuntimeError(f"Omni {name} has no video output: {str(data)[:1800]}")
    output.write_bytes(base64.b64decode(encoded))
    return output


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_TEXT_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini API key is not configured")
    if not PORTRAIT.is_file():
        raise RuntimeError(f"Founder portrait is missing: {PORTRAIT}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames = [make_frame(api_key, label, direction) for label, direction in FRAMES]
    clips = [make_clip(api_key, i, frames[i], frames[i + 1]) for i in range(3)]
    manifest = OUT.with_suffix(".concat.txt")
    manifest.write_text("".join(f"file '{path.resolve()}'\n" for path in clips), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest), "-c", "copy", str(OUT)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    print(json.dumps({"status": "complete", "model": OMNI_MODEL, "output": str(OUT), "frames": [str(x) for x in frames], "clips": [str(x) for x in clips]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
