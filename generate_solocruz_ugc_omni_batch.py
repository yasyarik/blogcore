#!/usr/bin/env python3
"""Create six owner-requested, review-only SoloCruz UGC Reels with Gemini Omni.

Each item is an independent 10-second 9:16 video.  The script deliberately
keeps generated pixels text-free; the exact hook and brand copy is recorded in
the manifest for post-generation overlay.  It does not create social posts,
schedule content, or publish anything.
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


FRAME_MODEL = "gemini-3.1-flash-image"
OMNI_MODEL = "gemini-omni-1.1-flash"
VOICE_NAME = "Kore"
OUT = Path(os.environ.get("SOLOCRUZ_UGC_OMNI_OUT", "data/social_assets/7/solocruz-ugc-omni-20260905"))

CAST = """The same two adult women throughout this one Reel: Maya, 31, warm brown shoulder-length wavy hair, coral linen shirt and white shorts; Lena, 30, dark-blonde curly ponytail, cobalt-blue sleeveless top and light linen trousers. They are stylish, natural, relaxed solo cruise travelers with immediate easy warmth. Preserve their exact faces, hair, wardrobe, body proportions and screen direction between the boundary frames."""

PHONE_STYLE = """Authentic 9:16 iPhone UGC filmed casually by a friend on the trip, not an advertisement: close handheld framing, minor natural hand movement, believable autofocus and exposure changes, bright daytime ocean light or real evening ship light, imperfect spontaneous laughter, realistic skin texture. No cinematic lighting, gimbal movement, slow motion, commercial polish, stock-video poses, text, captions, logos, readable signs, app UI, watermark, split screen, danger, loneliness, or awkwardness."""

REELS = [
    {
        "slug": "not-a-tinder-date",
        "overlay": ["THIS IS NOT A TINDER DATE.", "IT’S THE START OF OUR CRUISE STORY."],
        "speaker": "maya",
        "speech": "This is not a Tinder date. It’s the start of our cruise story.",
        "start": "In a small lively waterfront café before boarding, Maya and Lena sit across a small table with one carry-on suitcase each. They look at one another for a tiny beat, then share an immediate genuine laugh. The shot feels like their friend quietly filmed the first second of a new friendship.",
        "end": "On the open deck of a modern cruise ship at golden hour, Maya and Lena lean together against the railing with two colorful drinks, laughing into the sea wind as the port falls away behind them. A friend filming close by catches their real joyful reaction, then a quick imperfect selfie attempt.",
        "motion": "Begin in the café with Maya speaking directly but casually toward the iPhone camera. Use one energetic natural whip-pan match transition on the laughter into the ship deck. Let the remainder be candid shared laughter and movement toward the railing, ending precisely on the supplied final frame.",
    },
    {
        "slug": "best-upgrade",
        "overlay": ["THE BEST CRUISE UPGRADE COSTS LESS.", "A CRUISE PERSON."],
        "speaker": "voiceover",
        "speech": "The best upgrade? Someone who gets just as excited as you do.",
        "start": "Maya opens the door of a sunny cruise cabin with twin beds and a private balcony facing deep blue water. Her friend films just behind her shoulder as she sees the view for the first time and naturally smiles in surprise.",
        "end": "Maya and Lena stand shoulder to shoulder at the balcony railing, holding two colorful drinks and reacting with delight to the moving ocean below. They turn to the phone for an imperfect joyful selfie. The twin cabin is visible only as warm context, not as a hotel advert.",
        "motion": "Follow Maya from behind as she opens the cabin door, then make one natural handheld pivot to the balcony. Lena enters playfully with two drinks; capture the authentic surprise and both women rushing to the view. End exactly on the supplied final frame.",
    },
    {
        "slug": "survive-one-cabin",
        "overlay": ["WOULD WE SURVIVE ONE CABIN?", "FIND YOUR CRUISE PERSON."],
        "speaker": "both",
        "speech": "Coffee at seven, or dancing at two? Both.",
        "start": "Inside a bright modern cruise cabin in early morning, Maya and Lena stand on opposite sides of the cabin with coffee cups. They exchange an exaggerated mock-serious look, as if about to discover whether they are the same kind of traveler, then both start smiling.",
        "end": "Later on the open deck at blue hour, the same two women dance badly but enthusiastically together near the rail, then collapse into a laughing high-five. Their friend records from close range on an iPhone; warm ship lights and a dark ocean create a real holiday-night atmosphere.",
        "motion": "Maya asks the first half of the line in the cabin while looking at Lena; Lena immediately answers the final word with a playful grin. On their shared laugh, make one phone-like jump cut to their matching high-energy dance on deck. No other speech, music, text or graphics. End exactly on the supplied final frame.",
    },
    {
        "slug": "shared-reaction",
        "overlay": ["A VIEW IS GOOD.", "A SHARED REACTION IS BETTER."],
        "speaker": "voiceover",
        "speech": "The view was unreal. Having someone to lose it with made it better.",
        "start": "Maya stands at the rail on a departing cruise ship at sunset, looking toward a breathtaking stretch of glowing coastline and ocean. Her friend holds an iPhone close behind her, catching Maya’s authentic silent intake of breath rather than a posed travel shot.",
        "end": "Lena is now beside Maya at the same rail. Both women react at once with delighted disbelief, grab each other’s arms, laugh, point toward the glowing horizon, and try to capture it together on one phone. The final moment is an intimate real reaction, not a posed postcard.",
        "motion": "Stay close and handheld at shoulder level. Maya turns toward the view, then the camera naturally reveals Lena arriving beside her. Capture their synchronized emotional reaction and the shared attempt to record it. End precisely on the supplied final frame.",
    },
    {
        "slug": "cruise-person",
        "overlay": ["COME SOLO.", "MEET YOUR CRUISE PERSON."],
        "speaker": "maya",
        "speech": "We came solo. Then we met.",
        "start": "At a bright cruise terminal, Maya walks in confidently with one carry-on suitcase. She is excited and purposeful, not sad or waiting. Her friend films from several steps ahead on an iPhone as Maya notices someone just outside frame and her face lights up.",
        "end": "Maya and Lena walk through a ship corridor side by side, each with a small suitcase, talking and laughing like friends already on an adventure. They pause at a cabin door, exchange an excited look, and head inside together. The moment feels warm, casual and real.",
        "motion": "Maya speaks the line directly to the friend filming as she approaches the terminal. She then sees Lena, they greet with immediate excitement, and the phone follows them in one natural fast transition onto the ship. End exactly on the supplied final frame.",
    },
    {
        "slug": "two-main-characters",
        "overlay": ["ONE CABIN. TWO MAIN CHARACTERS.", "SPLIT THE CABIN. DOUBLE THE STORY."],
        "speaker": "lena",
        "speech": "Okay, you win.",
        "start": "In a bright cruise cabin before an evening onboard event, Maya emerges in a striking playful evening outfit and does a deliberately overconfident little turn for the iPhone. Lena watches from the bed area, gives an exaggerated impressed reaction, then laughs. Keep it candid and affectionate, never fashion-commercial.",
        "end": "Maya and Lena link arms and run laughing down an illuminated ship corridor toward an open-air deck party. The iPhone camera follows slightly behind, catching their movement, loose hair, ship lights and infectious pre-party excitement.",
        "motion": "Lena says the line with mock defeat after Maya’s playful outfit reveal. Maya pulls Lena into frame; both laugh, grab their small evening bags and run toward the deck. The phone follows with genuine handheld energy. End exactly on the supplied final frame.",
    },
]


def request_json(url: str, payload: dict, headers: dict, timeout: int) -> dict:
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")
        raise RuntimeError(f"Google HTTP {error.code}: {detail[:2400]}") from error


def image_data(parts: list[dict]) -> bytes:
    encoded = next(((part.get("inlineData") or {}).get("data") for part in parts if (part.get("inlineData") or {}).get("data")), None)
    if not encoded:
        raise RuntimeError("Image model returned no inline image")
    return base64.b64decode(encoded)


def make_frame(api_key: str, destination: Path, direction: str, reference: bytes | None = None) -> bytes:
    if destination.is_file() and destination.stat().st_size > 50_000:
        return destination.read_bytes()
    reference_copy = "" if reference is None else "Attached Image 1 is the exact identity and wardrobe reference; preserve both women exactly. "
    parts = [{"text": f"{reference_copy}{CAST}\n\n{PHONE_STYLE}\n\nCreate one exact boundary frame: {direction}"}]
    if reference is not None:
        parts.append({"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(reference).decode("ascii")}})
    payload = {"contents": [{"role": "user", "parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "9:16"}}}
    url = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}".format(urllib.parse.quote(FRAME_MODEL, safe=".-"), urllib.parse.quote(api_key, safe=""))
    data = request_json(url, payload, {"content-type": "application/json"}, 300)
    result = image_data(((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
    destination.write_bytes(result)
    return result


def make_video(api_key: str, reel: dict, start: bytes, end: bytes, destination: Path) -> None:
    if destination.is_file() and destination.stat().st_size > 100_000:
        return
    if reel["speaker"] == "voiceover":
        audio = f'A warm, pleasant, conversational American female narrator voice, preset {VOICE_NAME}, speaks exactly this once from 0.6s to 6.2s: "{reel["speech"]}".'
    elif reel["speaker"] == "both":
        audio = f'The two visible women speak exactly this short exchange with natural synchronized lip movement and warm American female voices from 0.5s to 3.0s: "{reel["speech"]}".'
    else:
        audio = f'The visible heroine speaks exactly this once directly and naturally with synchronized lip movement, warm American female voice preset {VOICE_NAME}, from 0.5s to 3.2s: "{reel["speech"]}".'
    prompt = f"""[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image2]
Use Image1 as the exact first frame and Image2 as the exact final frame. Create one continuous ten-second vertical iPhone UGC Reel between them. {CAST}\n\n{PHONE_STYLE}\n\n{reel['motion']}\n\n{audio} Generate only quiet natural ship, café or sea ambience behind speech; no music and no extra dialogue. No readable text, captions, logos, graphic overlays, fake UI, watermark, product packaging, advertisements, visual effects, glamour-commercial styling or extra people. The final decoded frame must match Image2 exactly."""
    payload = {
        "model": OMNI_MODEL,
        "input": [
            {"type": "image", "data": base64.b64encode(start).decode("ascii"), "mime_type": "image/jpeg"},
            {"type": "image", "data": base64.b64encode(end).decode("ascii"), "mime_type": "image/jpeg"},
            {"type": "text", "text": prompt},
        ],
        "response_format": {"type": "video", "aspect_ratio": "9:16", "resolution": "720p"},
        "generation_config": {"video_config": {"task": "image_to_video"}},
    }
    data = request_json("https://generativelanguage.googleapis.com/v1beta/interactions", payload, {"content-type": "application/json", "x-goog-api-key": api_key}, 900)
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
        raise RuntimeError(f"Omni returned no video: {str(data)[:1800]}")
    destination.write_bytes(base64.b64decode(encoded))


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_TEXT_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini API key is not configured")
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"model": OMNI_MODEL, "voice": VOICE_NAME, "status": "review_only", "reels": []}
    for reel in REELS:
        slug = reel["slug"]
        item = {"slug": slug, "overlay": reel["overlay"], "speech": reel["speech"], "speaker": reel["speaker"]}
        try:
            start = make_frame(api_key, OUT / f"{slug}-start.jpg", reel["start"])
            end = make_frame(api_key, OUT / f"{slug}-end.jpg", reel["end"], reference=start)
            video = OUT / f"{slug}.mp4"
            make_video(api_key, reel, start, end, video)
            item.update({"status": "GENERATED", "video": str(video), "startFrame": str(OUT / f"{slug}-start.jpg"), "endFrame": str(OUT / f"{slug}-end.jpg")})
        except Exception as error:
            item.update({"status": "ERROR", "error": str(error)[:2600]})
        manifest["reels"].append(item)
        (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(item, ensure_ascii=False), flush=True)
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
