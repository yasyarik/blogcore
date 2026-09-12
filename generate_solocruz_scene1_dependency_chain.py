import json
import os
import sys
from base64 import b64encode
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, "/var/www/blog.yas.ooo")
import app


OUTPUT = Path("/var/www/blog.yas.ooo/data/video_layer_tests/solocruz-scene1-dependent-unit-20260811")
OUTPUT.mkdir(parents=True, exist_ok=True)
os.environ["GEMINI_IMAGE_MODEL"] = "gemini-3.1-flash-lite-image"


def reference(path):
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return {"mime_type": mime, "data": b64encode(path.read_bytes()).decode("ascii")}


def save_jpeg(name, data):
    path = OUTPUT / name
    path.write_bytes(data)
    return path


def composite(base_path, unit_path, output_path):
    base = Image.open(base_path).convert("RGBA")
    unit = Image.open(unit_path).convert("RGBA")
    if unit.size != base.size:
        unit = unit.resize(base.size, Image.Resampling.LANCZOS)
    Image.alpha_composite(base, unit).convert("RGB").save(output_path, quality=92)


background_prompt = """
Create a photorealistic 9:16 editorial background plate of a modern bedroom at night. Show only the immutable room: warm off-white walls, dark oak floor, one softly glowing wall lamp on the far left, a subtle curtain and window depth on the right, realistic empty floor area across the lower two thirds, and natural perspective viewed from the front-left corner at seated eye height. Keep the upper-left area visually calm for later typography. The room is completely empty: no person, desk, chair, laptop, furniture group, readable text, logo, or interface. Warm practical light from the left and faint cool moonlight from the right, realistic shadows and premium travel-editorial photography.
""".strip()

initial_prompt = """
Reference image 1 is the immutable empty bedroom plate. Generate one dependency-closed foreground assembly unit for that exact room, on a perfectly uniform shadowless near-white matte (#F4F4F4), as a complete 9:16 registered canvas.

The single unit must contain all physically dependent parts together: a dark wooden desk, its chair, a sleek open silver laptop, and Sarah seated naturally at that desk. Sarah is a 30-year-old woman with light brown hair in a loose bun, wearing a cozy grey knit sweater. The laptop occupies the lower-left foreground and is turned 35 degrees toward the camera so its screen is clearly visible. Sarah occupies the right-middle area behind the laptop, and her face, both hands, the laptop screen, desk edges, chair contact, and all contact shadows are simultaneously coherent and visible. She looks calmly and hopefully at the screen. The screen shows a simple cruise checkout with one guest and an initial total of $1,200.

Match reference 1 exactly in camera height, lens perspective, vanishing lines, warm-left/cool-right illumination, color temperature, scale, and floor contact. The desk group must fit the empty lower two thirds of reference 1 and leave the upper-left text-safe zone clear. Render only this entire connected foreground unit and its necessary contact shadows. Do not render the room, walls, floor, window, curtain, extra furniture, additional people, border, logo, watermark, or unrelated objects. Do not separate Sarah from the desk setup and do not crop any meaningful edge of the connected unit.
""".strip()

changed_prompt = """
Reference image 1 is the immutable empty bedroom plate. Reference image 2 is the approved initial foreground assembly unit on a near-white matte. Generate the second keyframe of that exact same dependency-closed unit as a complete 9:16 registered canvas on the same perfectly uniform shadowless near-white matte (#F4F4F4).

Preserve exactly the same Sarah identity, hair, sweater, seated body position, desk, chair, laptop model, laptop position, 35-degree screen angle, framing, scale, perspective, light, shadows, canvas coordinates, and every external silhouette from reference image 2. Change only the visible story state: the laptop total now reads $2,400 with a clearly emphasized single-supplement increase; Sarah's expression changes from hopeful to shocked and frustrated, her shoulders lower slightly, and her right hand reaches naturally to her temple while her left hand remains near the laptop. The face and screen must both remain clearly visible to the viewer.

Render only the same connected Sarah-plus-workstation unit and its necessary contact shadows. Do not regenerate or include the bedroom. Do not move, resize, rotate, recrop, redesign, add, remove, or substitute any physical part. No extra person, object, logo, watermark, border, or scenery.
""".strip()

background = save_jpeg("01-empty-room.jpg", app._gemini_image_jpeg(background_prompt, aspect_ratio="9:16"))
initial = save_jpeg(
    "02-unit-initial-source.jpg",
    app._gemini_image_jpeg(initial_prompt, aspect_ratio="9:16", reference_image=reference(background)),
)
changed = save_jpeg(
    "03-unit-changed-source.jpg",
    app._gemini_image_jpeg(changed_prompt, aspect_ratio="9:16", reference_image=[reference(background), reference(initial)]),
)

initial_alpha = OUTPUT / "02-unit-initial.png"
changed_alpha = OUTPUT / "03-unit-changed.png"
app._remove_reel_background(initial, initial_alpha, preserve_canvas=True)
app._remove_reel_background(changed, changed_alpha, preserve_canvas=True)

initial_composite = OUTPUT / "04-composite-initial.jpg"
changed_composite = OUTPUT / "05-composite-changed.jpg"
composite(background, initial_alpha, initial_composite)
composite(background, changed_alpha, changed_composite)

images = [
    ("Empty room", background),
    ("Initial unit source", initial),
    ("Initial composite", initial_composite),
    ("Changed unit source", changed),
    ("Changed composite", changed_composite),
]
thumb_width = 360
opened = []
for label, path in images:
    image = Image.open(path).convert("RGB")
    thumb_height = round(image.height * thumb_width / image.width)
    opened.append((label, image.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)))
sheet = Image.new("RGB", (thumb_width * len(opened), opened[0][1].height + 60), "#111318")
draw = ImageDraw.Draw(sheet)
for index, (label, image) in enumerate(opened):
    x = index * thumb_width
    sheet.paste(image, (x, 40))
    draw.text((x + 10, 12), label, fill="white")
sheet.save(OUTPUT / "06-contact-sheet.jpg", quality=92)

(OUTPUT / "manifest.json").write_text(json.dumps({
    "model": os.environ["GEMINI_IMAGE_MODEL"],
    "purpose": "Real SoloCruz first-scene dependency-closed keyframe proof",
    "media": "images only; no voice or video",
    "files": [str(path) for _, path in images] + [str(OUTPUT / "06-contact-sheet.jpg")],
    "prompts": {"background": background_prompt, "initialUnit": initial_prompt, "changedUnit": changed_prompt},
}, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps({"status": "complete", "output": str(OUTPUT), "model": os.environ["GEMINI_IMAGE_MODEL"], "images": 3, "voice": False, "video": False}))
