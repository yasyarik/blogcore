import json
import os
import subprocess
import sys
from base64 import b64encode
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/var/www/blog.yas.ooo")
import app


SOURCE = Path("/var/www/blog.yas.ooo/data/video_layer_tests/solocruz-scene1-dependent-unit-20260811")
OUTPUT = Path("/var/www/blog.yas.ooo/data/video_layer_tests/solocruz-scene1-motion-proof-20260811")
OUTPUT.mkdir(parents=True, exist_ok=True)
os.environ["GEMINI_IMAGE_MODEL"] = "gemini-3.1-flash-lite-image"
BACKGROUND = SOURCE / "01-empty-room.jpg"


def ref(path):
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return {"mime_type": mime, "data": b64encode(path.read_bytes()).decode("ascii")}


def generated(path, prompt, references):
    path.write_bytes(app._gemini_image_jpeg(prompt, aspect_ratio="9:16", reference_image=references))
    return path


initial_prompt = """
Reference image 1 is the immutable empty bedroom. Generate one complete dependency-closed foreground unit on a perfectly uniform saturated chroma-green matte (#00FF00) as a registered 9:16 canvas.

The unit contains exactly one Sarah, exactly one chair, exactly one compact dark wooden desk, and exactly one open silver laptop as a single physically coherent group. Sarah is a 30-year-old woman with light brown hair in a loose bun and a grey knit sweater. Show her complete seated body from head through both feet, with natural anatomy. She sits behind the desk on the right. Show the complete chair and the desk's complete support structure, including multiple visible legs that reach the same floor plane as Sarah's feet. Nothing may terminate in mid-air. The same desk extends toward the lower-left foreground. The one laptop rests physically on that desk, between Sarah and the camera, turned 35 degrees toward camera. Sarah looks at that same laptop and her forearms lead naturally toward its keyboard. The whole screen, bezel, hinge, keyboard, trackpad, and base of this one laptop are visible at the same time as Sarah's face and hands. There is no second device anywhere in the image.

STRICT SAFE FRAME: every edge of the laptop, including all four screen corners and the complete keyboard base, must remain at least 8% inside the canvas. The complete connected unit must remain at least 6% inside the left, right, and bottom canvas edges. Reduce the unit rather than cropping any laptop, desk, chair, hand, head, or meaningful edge. Keep the upper-left 28% of the canvas empty for editorial copy.

Match reference 1's seated-eye camera, perspective, floor plane, warm-left/cool-right light, color temperature, and shadows. Render only this connected unit and its necessary contact shadows on the uniform chroma-green matte. The matte must remain pure green and must be visible around the complete silhouette. Do not reproduce any room, wall, floor, curtain, window, logo, border, additional person, or unrelated object. Do not use green on the unit. The laptop screen should be a clean dark neutral blank display with no text or interface because exact UI will be rendered later.
""".strip()

changed_prompt = """
Reference image 1 is the immutable empty bedroom. Reference image 2 is the approved initial Sarah+chair+desk+laptop foreground unit. Generate the second registered keyframe of exactly that same connected unit on the same perfectly uniform saturated chroma-green matte (#00FF00).

Preserve pixel-consistent identity, wardrobe, complete body and feet, chair, complete desk support structure and legs, laptop, blank screen, screen angle, complete laptop silhouette, canvas coordinates, scale, perspective, light, contact shadows, and external unit footprint. Change only Sarah's visible state: her expression becomes shocked and frustrated and her right hand reaches naturally to her temple. Her torso, shoulders, legs, feet, chair, desk, and laptop remain registered in exactly the same place. Her left hand remains near the laptop. The whole laptop and Sarah's complete body must remain visible with the same safe margins as reference image 2. Do not add or remove any limb, furniture part, support, or object.

Render only the connected unit on the uniform chroma-green matte. The matte must remain pure green and visible around the complete silhouette. Do not use green on the unit. Do not include the room or introduce, remove, crop, move, resize, rotate, or redesign any physical part. Keep the laptop screen blank and free of generated text.
""".strip()

COMPONENT_SCHEMA = {
    "type": "object",
    "properties": {
        "approved": {"type": "boolean"},
        "allRequiredComponentsVisible": {"type": "boolean"},
        "exactlyOneOfEachRequiredComponent": {"type": "boolean"},
        "laptopPhysicallySupported": {"type": "boolean"},
        "unitVisuallyCoherent": {"type": "boolean"},
        "completeLaptopVisible": {"type": "boolean"},
        "allScreenCornersVisible": {"type": "boolean"},
        "screenUnobstructed": {"type": "boolean"},
        "personFaceVisible": {"type": "boolean"},
        "personBodyAndFeetComplete": {"type": "boolean"},
        "furnitureSupportComplete": {"type": "boolean"},
        "safeMarginsPresent": {"type": "boolean"},
        "uniformChromaBackground": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["approved", "allRequiredComponentsVisible", "exactlyOneOfEachRequiredComponent", "laptopPhysicallySupported", "unitVisuallyCoherent", "completeLaptopVisible", "allScreenCornersVisible", "screenUnobstructed", "personFaceVisible", "personBodyAndFeetComplete", "furnitureSupportComplete", "safeMarginsPresent", "uniformChromaBackground", "reason"],
}


def validate_required_unit(path):
    return app._gemini_text_json_with_image(
        """Validate this generated foreground unit before compositing. Required components are exactly one seated woman with visible face and hands, exactly one complete chair, exactly one compact desk with a visibly complete load-bearing support structure reaching the floor plane, and exactly one complete open laptop. The woman's complete seated body, both legs, and both feet must be present without truncation or impossible anatomy. The laptop must rest physically on that same desk and the woman's pose must relate naturally to that laptop. Reject duplicate or floating laptops, unsupported tabletops, missing furniture supports, disconnected groups, inexplicable overlaps, and any body or object that terminates in mid-air. The laptop is complete only when the entire screen, all four inner screen corners, bezel, hinge, keyboard, trackpad, and outer base edges are visible. The display must be unobstructed. Every required component must have safe space from every canvas edge. The background must be a uniform saturated chroma green suitable for clean keying. Approve only if every condition is visibly satisfied.""",
        path.read_bytes(),
        "image/jpeg",
        COMPONENT_SCHEMA,
        temperature=0.0,
    )


def generate_validated(path_prefix, prompt, references, max_attempts=4):
    correction = ""
    for attempt in range(1, max_attempts + 1):
        path = OUTPUT / f"{path_prefix}-attempt-{attempt}.jpg"
        generated(path, prompt + correction, references)
        result = validate_required_unit(path)
        if result.get("approved"):
            return path, result, attempt
        correction = "\n\nThe previous candidate failed mandatory visual validation for this reason: " + result.get("reason", "required components were incomplete") + ". Regenerate the complete composition from the original requirements; do not patch or crop the failed image."
    raise RuntimeError(f"No approved foreground unit after {max_attempts} attempts: {result}")


initial_source, initial_validation, initial_attempts = generate_validated("01-unit-initial-source", initial_prompt, ref(BACKGROUND), max_attempts=6)

PAIR_SCHEMA = {
    "type": "object",
    "properties": {
        "approved": {"type": "boolean"},
        "sameIdentityAndWardrobe": {"type": "boolean"},
        "sameBodyAndLegGeometry": {"type": "boolean"},
        "sameFurnitureGeometry": {"type": "boolean"},
        "sameLaptopGeometry": {"type": "boolean"},
        "sameCanvasRegistration": {"type": "boolean"},
        "noPartsAddedOrRemoved": {"type": "boolean"},
        "onlyExpressionAndRightArmChanged": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["approved", "sameIdentityAndWardrobe", "sameBodyAndLegGeometry", "sameFurnitureGeometry", "sameLaptopGeometry", "sameCanvasRegistration", "noPartsAddedOrRemoved", "onlyExpressionAndRightArmChanged", "reason"],
}


def validate_registered_pair(initial_path, changed_path, pair_path):
    left = Image.open(initial_path).convert("RGB")
    right = Image.open(changed_path).convert("RGB")
    pair = Image.new("RGB", (left.width * 2, left.height), "white")
    pair.paste(left, (0, 0))
    pair.paste(right, (left.width, 0))
    pair.save(pair_path, quality=94)
    return app._gemini_text_json_with_image(
        """Compare the INITIAL image on the left with the CHANGED image on the right as registered animation keyframes. Approve only when identity, wardrobe, complete body and legs, chair, desk supports, laptop geometry, scale, perspective, and canvas coordinates remain the same. No body part, furniture part, support, or object may appear, disappear, grow, shrink, or move. The only allowed changes are facial expression and the right arm moving to the temple. Reject morphing silhouettes or newly visible legs/supports even if both individual images look plausible.""",
        pair_path.read_bytes(),
        "image/jpeg",
        PAIR_SCHEMA,
        temperature=0.0,
    )


def generate_registered_changed(max_attempts=6):
    correction = ""
    last = None
    for attempt in range(1, max_attempts + 1):
        candidate = OUTPUT / f"02-unit-changed-source-attempt-{attempt}.jpg"
        generated(candidate, changed_prompt + correction, [ref(BACKGROUND), ref(initial_source)])
        unit_result = validate_required_unit(candidate)
        if not unit_result.get("approved"):
            correction = "\n\nThe previous candidate failed component integrity: " + unit_result.get("reason", "incomplete unit") + ". Regenerate the complete registered unit from the original references."
            last = {"unit": unit_result}
            continue
        pair_path = OUTPUT / f"02-unit-pair-attempt-{attempt}.jpg"
        pair_result = validate_registered_pair(initial_source, candidate, pair_path)
        last = {"unit": unit_result, "pair": pair_result}
        if pair_result.get("approved"):
            return candidate, last, attempt
        correction = "\n\nThe previous candidate failed registered-keyframe comparison: " + pair_result.get("reason", "geometry changed") + ". Keep every pixel-level physical component registered; change only expression and right arm."
    raise RuntimeError(f"No registered changed keyframe after {max_attempts} attempts: {last}")


changed_source, changed_validation, changed_attempts = generate_registered_changed()
initial_alpha = OUTPUT / "01-unit-initial.png"
changed_alpha = OUTPUT / "02-unit-changed.png"


def remove_chroma_background(source, target):
    image = cv2.imread(str(source), cv2.IMREAD_COLOR)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    green = cv2.inRange(hsv, np.array([35, 70, 45]), np.array([95, 255, 255]))
    green = cv2.morphologyEx(green, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    green = cv2.GaussianBlur(green, (5, 5), 0)
    alpha = 255 - green
    rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = alpha
    cv2.imwrite(str(target), rgba)


remove_chroma_background(initial_source, initial_alpha)
remove_chroma_background(changed_source, changed_alpha)


def composite(unit_path, target):
    base = Image.open(BACKGROUND).convert("RGBA")
    unit = Image.open(unit_path).convert("RGBA")
    if unit.size != base.size:
        unit = unit.resize(base.size, Image.Resampling.LANCZOS)
    Image.alpha_composite(base, unit).convert("RGB").save(target, quality=94)


initial_composite = OUTPUT / "03-composite-initial.jpg"
changed_composite = OUTPUT / "04-composite-changed.jpg"
composite(initial_alpha, initial_composite)
composite(changed_alpha, changed_composite)

SCREEN_SCHEMA = {
    "type": "object",
    "properties": {
        "approved": {"type": "boolean"},
        "topLeft": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]},
        "topRight": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]},
        "bottomRight": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]},
        "bottomLeft": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]},
        "reason": {"type": "string"},
    },
    "required": ["approved", "topLeft", "topRight", "bottomRight", "bottomLeft", "reason"],
}


def detect_screen(path):
    return app._gemini_text_json_with_image(
        """Locate only the inner visible display surface of the foreground laptop. Return its four corners in normalized 0..1000 image coordinates, ordered top-left, top-right, bottom-right, bottom-left from the viewer's perspective. Exclude the bezel, keyboard, and any second dark rectangle. Set approved false if all four inner display corners are not clearly visible.""",
        path.read_bytes(),
        "image/jpeg",
        SCREEN_SCHEMA,
        temperature=0.0,
    )


def ui_card(total, supplement):
    card = Image.new("RGB", (900, 540), "#f7fafc")
    draw = ImageDraw.Draw(card)
    bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    huge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 128)
    medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    draw.rectangle((0, 0, 900, 88), fill="#0d2438")
    draw.text((44, 18), "CRUISE CHECKOUT", font=bold, fill="#ffffff")
    draw.text((48, 140), "1 GUEST", font=medium, fill="#385166")
    draw.text((48, 220), total, font=huge, fill="#09243a")
    if supplement:
        draw.rounded_rectangle((44, 400, 856, 510), radius=22, fill="#ffe5e5")
        draw.text((78, 424), "SINGLE SUPPLEMENT APPLIED", font=medium, fill="#b42318")
    else:
        draw.text((48, 430), "CABIN TOTAL", font=medium, fill="#557083")
    return np.array(card)


def apply_screen(path, screen, total, supplement, target):
    image = cv2.imread(str(path))
    height, width = image.shape[:2]
    points = []
    for key in ("topLeft", "topRight", "bottomRight", "bottomLeft"):
        points.append([screen[key]["x"] * width / 1000.0, screen[key]["y"] * height / 1000.0])
    destination = np.array(points, dtype=np.float32)
    source = np.array([[0, 0], [899, 0], [899, 539], [0, 539]], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(source, destination)
    card = cv2.cvtColor(ui_card(total, supplement), cv2.COLOR_RGB2BGR)
    warped = cv2.warpPerspective(card, matrix, (width, height), flags=cv2.INTER_CUBIC)
    mask = cv2.warpPerspective(np.full((540, 900), 255, dtype=np.uint8), matrix, (width, height))
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    alpha = mask.astype(np.float32)[..., None] / 255.0
    output = (warped.astype(np.float32) * alpha + image.astype(np.float32) * (1 - alpha)).astype(np.uint8)
    cv2.imwrite(str(target), output, [cv2.IMWRITE_JPEG_QUALITY, 94])


initial_screen = detect_screen(initial_composite)
changed_screen = detect_screen(changed_composite)
if not initial_screen.get("approved") or not changed_screen.get("approved"):
    raise RuntimeError(f"Laptop screen detection failed: {initial_screen} / {changed_screen}")
initial_ui = OUTPUT / "05-composite-initial-ui.jpg"
changed_ui = OUTPUT / "06-composite-changed-ui.jpg"
apply_screen(initial_composite, initial_screen, "$1,200", False, initial_ui)
apply_screen(changed_composite, changed_screen, "$2,400", True, changed_ui)


def ease(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def camera_frame(image, progress, size=(1080, 1920)):
    frame = image.resize(size, Image.Resampling.LANCZOS)
    zoom = 1.0 + 0.035 * ease(progress)
    scaled = frame.resize((round(size[0] * zoom), round(size[1] * zoom)), Image.Resampling.LANCZOS)
    max_x = scaled.width - size[0]
    max_y = scaled.height - size[1]
    x = round(max_x * (0.46 + 0.10 * progress))
    y = round(max_y * 0.58)
    return scaled.crop((x, y, x + size[0], y + size[1]))


background = Image.open(BACKGROUND).convert("RGB")
initial = Image.open(initial_ui).convert("RGB")
changed = Image.open(changed_ui).convert("RGB")
font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 78)
font_accent = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 94)
fps = 30
duration = 4.5
video_path = OUTPUT / "07-scene-motion-proof.mp4"
process = subprocess.Popen([
    "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
    "-s", "1080x1920", "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264",
    "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(video_path),
], stdin=subprocess.PIPE)

for frame_index in range(round(duration * fps)):
    time_seconds = frame_index / fps
    if time_seconds < 0.55:
        scene = background.copy()
    elif time_seconds < 1.05:
        scene = Image.blend(background, initial, ease((time_seconds - 0.55) / 0.5))
    elif time_seconds < 2.45:
        scene = initial.copy()
    elif time_seconds < 2.85:
        scene = Image.blend(initial, changed, ease((time_seconds - 2.45) / 0.4))
    else:
        scene = changed.copy()
    frame = camera_frame(scene, frame_index / max(1, round(duration * fps) - 1))
    draw = ImageDraw.Draw(frame)
    text_progress = ease((time_seconds - 0.12) / 0.45)
    y_offset = round((1 - text_progress) * 45)
    text_alpha = round(255 * text_progress)
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    shadow = (0, 0, 0, round(text_alpha * 0.55))
    white = (255, 255, 255, text_alpha)
    cyan = (84, 230, 224, text_alpha)
    for dx, dy in ((3, 4), (5, 6)):
        odraw.text((58 + dx, 106 + y_offset + dy), "WHY DOES SOLO", font=font_big, fill=shadow)
        odraw.text((58 + dx, 194 + y_offset + dy), "COST DOUBLE?", font=font_accent, fill=shadow)
    odraw.text((58, 106 + y_offset), "WHY DOES SOLO", font=font_big, fill=white)
    odraw.text((58, 194 + y_offset), "COST DOUBLE?", font=font_accent, fill=cyan)
    frame = Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")
    process.stdin.write(np.asarray(frame, dtype=np.uint8).tobytes())

process.stdin.close()
if process.wait() != 0:
    raise RuntimeError("ffmpeg failed")

contact = Image.new("RGB", (1080, 640), "#111318")
draw = ImageDraw.Draw(contact)
for index, (label, path) in enumerate((("INITIAL", initial_ui), ("CHANGED", changed_ui))):
    image = Image.open(path).convert("RGB")
    image.thumbnail((500, 560), Image.Resampling.LANCZOS)
    x = 25 + index * 530
    contact.paste(image, (x, 55))
    draw.text((x, 15), label, font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28), fill="white")
contact.save(OUTPUT / "08-contact-sheet.jpg", quality=94)

(OUTPUT / "manifest.json").write_text(json.dumps({
    "model": os.environ["GEMINI_IMAGE_MODEL"],
    "imagesGenerated": initial_attempts + changed_attempts,
    "mandatoryComponentValidation": {"initial": initial_validation, "changed": changed_validation},
    "reusedBackground": str(BACKGROUND),
    "screenDetection": {"initial": initial_screen, "changed": changed_screen},
    "video": str(video_path),
    "voice": False,
    "audio": False,
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"status": "complete", "output": str(OUTPUT), "video": str(video_path), "voice": False, "audio": False}))
