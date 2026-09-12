#!/usr/bin/env python3
"""Seed, submit and collect a reviewed article-derived Pinterest Pin ledger.

The ledger is site configuration.  This runner is universal: it never branches
on a domain and never publishes.  Provider images contain no generated text or
logos; exact overlay copy and a site-owned logo are composited deterministically
when a completed Gemini batch is collected.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

sys.path.insert(0, ".")
import app

IMAGE_MODEL = "gemini-3.1-flash-image"
READY = "BATCH_READY"
SUBMITTED = "BATCH_SUBMITTED"


def load_ledger(path: str) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("pins"), list):
        raise RuntimeError("ledger must be an object with a pins array")
    return payload


def pin_id(site_id: int, key: str) -> str:
    digest = hashlib.sha256(f"{site_id}:{key}".encode()).hexdigest()[:18]
    return f"pin-{site_id}-{digest}"


def normalized(value) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def validate_ledger(site_id: int, ledger: dict) -> list[dict]:
    pins = ledger["pins"]
    expected = int(ledger.get("expectedPins") or len(pins))
    if len(pins) != expected:
        raise RuntimeError(f"expected {expected} pins, found {len(pins)}")
    required = {"key", "sourceJobId", "overlayText", "title", "description", "altText", "keywords", "scene"}
    seen = {"key": set(), "overlayText": set(), "title": set(), "scene": set()}
    with app.db() as conn:
        jobs = {row["id"]: row for row in conn.execute(
            "select * from content_jobs where site_id=? and status in ('PUBLISHED','IMPORTED')", (site_id,)
        ).fetchall()}
    clean = []
    for index, raw in enumerate(pins, 1):
        if not isinstance(raw, dict) or required - set(raw):
            raise RuntimeError(f"pin {index} is missing {sorted(required - set(raw or {}))}")
        item = {**raw}
        for field in ("key", "sourceJobId", "overlayText", "title", "description", "altText", "scene"):
            item[field] = normalized(item[field])
        item["keywords"] = [normalized(value) for value in item["keywords"] if normalized(value)]
        if item["sourceJobId"] not in jobs:
            raise RuntimeError(f"{item['key']}: source is not a public site article")
        job = jobs[item["sourceJobId"]]
        destination = normalized(job["published_url"])
        if not destination.startswith(("https://", "http://")):
            raise RuntimeError(f"{item['key']}: source has no public destination")
        for field, limit in (("overlayText", 80), ("title", 100), ("description", 500), ("altText", 250)):
            if not item[field] or len(item[field]) > limit:
                raise RuntimeError(f"{item['key']}: {field} must be 1..{limit} chars")
        if len(item["overlayText"].split()) > 9:
            raise RuntimeError(f"{item['key']}: overlay exceeds the nine-word mobile limit")
        if len(item["keywords"]) < 3:
            raise RuntimeError(f"{item['key']}: at least three search phrases are required")
        for field in seen:
            marker = item[field].casefold()
            if marker in seen[field]:
                raise RuntimeError(f"{item['key']}: duplicate {field}")
            seen[field].add(marker)
        item.update({
            "id": pin_id(site_id, item["key"]),
            "sourceTitle": normalized(job["title"] or job["topic"]),
            "destinationUrl": destination,
            "pinType": normalized(item.get("pinType") or "searchable_inspiration"),
            "boardKey": normalized(item.get("boardKey") or ledger.get("boardKey") or ""),
            "previewFile": normalized(item.get("previewFile")),
        })
        if item["pinType"] not in app.PINTEREST_DEFAULT_MIX:
            raise RuntimeError(f"{item['key']}: unsupported pinType")
        clean.append(item)
    return clean


def provider_prompt(site, item: dict) -> str:
    return f"""
Create the photographic background for one premium Pinterest Pin.

FORMAT:
- Vertical 2:3 composition, equivalent to 1000x1500.
- The final asset will receive a large exact headline in the top 26-30% and a small official brand mark at the bottom during deterministic post-processing.
- Reserve a calm, uncluttered, naturally dark or softly defocused area across the full top 30%; no face, hand, clock, ship, or essential proof may enter that headline-safe area.
- Put the story-defining visual proof in the middle and lower portions. It must remain understandable as a small mobile thumbnail.

EDITORIAL CONTEXT:
- Brand: {site['brand_name'] or site['domain']}.
- Source article: {item['sourceTitle']}.
- Exact scene: {item['scene']}.

STYLE:
- Photorealistic, candid editorial travel photography with believable cruise-ship scale, natural adult anatomy, real materials and specific physical detail.
- Make this scene visibly different from generic cruise advertising.
- No generated words, letters, numbers, logo, watermark, fake UI, infographic, badge, arrow, price, receipt text, or branded cruise-line marks.
- No person sitting at a desk, no paperwork meeting, no posed stock-photo smile, and no generic empty ocean unless the scene explicitly makes it meaningful.
""".strip()


def seed(site_id: int, ledger_path: str, preview_dir: str | None) -> dict:
    ledger = load_ledger(ledger_path)
    pins = validate_ledger(site_id, ledger)
    now = app.now_iso()
    created = updated = preview_count = 0
    preview_root = Path(preview_dir).resolve() if preview_dir else None
    with app.db() as conn:
        for item in pins:
            existing = conn.execute("select * from visual_pins where site_id=? and id=?", (site_id, item["id"])).fetchone()
            if existing and existing["status"] in {"SENT", "SCHEDULED"}:
                raise RuntimeError(f"{item['key']}: published/scheduled Pin cannot be reseeded")
            concept = {
                "schema": "article-derived-pin/v1",
                "ledgerKey": item["key"],
                "sourceJobId": item["sourceJobId"],
                "sourceTitle": item["sourceTitle"],
                "overlayText": item["overlayText"],
                "keywords": item["keywords"],
                "scene": item["scene"],
                "imagePrompt": provider_prompt(app.get_site(site_id), item),
                "pinType": item["pinType"],
                "boardKey": item["boardKey"],
                "cta": normalized(item.get("cta")),
                "batch": {},
            }
            filename = "pin.jpg" if item["previewFile"] else None
            status = "DRAFT" if filename else READY
            if existing:
                previous_concept = app.parse_json_object(existing["concept_json"])
                if previous_concept.get("ledgerKey") != item["key"]:
                    raise RuntimeError(f"{item['key']}: deterministic Pin id belongs to another ledger item")
                previous_batch = previous_concept.get("batch") if isinstance(previous_concept.get("batch"), dict) else {}
                if previous_batch:
                    concept["batch"] = previous_batch
                if existing["status"] in {SUBMITTED, "DRAFT", "SENT", "SCHEDULED"}:
                    status = existing["status"]
                    filename = existing["image_filename"]
            values = (site_id, "article_derived_pin", json.dumps(concept, ensure_ascii=False), item["title"], item["description"], item["altText"], filename, item["destinationUrl"], status, now, now, item["id"])
            if existing:
                conn.execute(
                    """update visual_pins set site_id=?,mode=?,concept_json=?,title=?,description=?,alt_text=?,image_filename=?,destination_url=?,status=?,error=null,updated_at=? where id=?""",
                    (site_id, "article_derived_pin", json.dumps(concept, ensure_ascii=False), item["title"], item["description"], item["altText"], filename, item["destinationUrl"], status, now, item["id"]),
                )
                updated += 1
            else:
                conn.execute("""insert into visual_pins(site_id,mode,concept_json,title,description,alt_text,image_filename,destination_url,status,created_at,updated_at,id)
                                values(?,?,?,?,?,?,?,?,?,?,?,?)""", values)
                created += 1
            if item["previewFile"]:
                if not preview_root:
                    raise RuntimeError(f"{item['key']}: preview directory is required")
                source = (preview_root / item["previewFile"]).resolve()
                if preview_root not in source.parents or not source.is_file():
                    raise RuntimeError(f"{item['key']}: approved preview is missing")
                target = app.visual_pin_asset_dir(site_id, item["id"])
                target.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target / "pin.jpg")
                preview_count += 1
    return {"pins": len(pins), "created": created, "updated": updated, "approvedPreviews": preview_count, "batchReady": len(pins) - preview_count}


def gemini_key() -> str:
    value = os.environ.get("GEMINI_IMAGE_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not value:
        raise RuntimeError("GEMINI_IMAGE_API_KEY is not configured")
    return value


def submit(site_id: int, expected: int) -> dict:
    with app.db() as conn:
        rows = conn.execute("select * from visual_pins where site_id=? and mode='article_derived_pin' and status=? order by id", (site_id, READY)).fetchall()
    if len(rows) != expected:
        raise RuntimeError(f"expected {expected} batch-ready Pins, found {len(rows)}")
    requests = []
    for row in rows:
        concept = app.parse_json_object(row["concept_json"])
        requests.append({
            "request": {
                "contents": [{"role": "user", "parts": [{"text": concept["imagePrompt"]}]}],
                "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": "2:3"}},
            },
            "metadata": {"key": row["id"]},
        })
    payload = {"batch": {"display_name": f"pinterest-site-{site_id}-{app.datetime.now(app.timezone.utc).strftime('%Y%m%d-%H%M%S')}", "input_config": {"requests": {"requests": requests}}}}
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{urllib.parse.quote(IMAGE_MODEL, safe='.-')}:batchGenerateContent"
    request = urllib.request.Request(endpoint, data=json.dumps(payload).encode(), headers={"content-type": "application/json", "x-goog-api-key": gemini_key()}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        detail = error.read(2200).decode("utf-8", "replace")
        raise RuntimeError(f"Gemini image batch create HTTP {error.code}: {detail}") from error
    batch_name = normalized(data.get("name"))
    if not batch_name:
        raise RuntimeError(f"Gemini batch returned no name: {data}")
    now = app.now_iso()
    with app.db() as conn:
        for row in rows:
            concept = app.parse_json_object(row["concept_json"])
            concept["batch"] = {"name": batch_name, "model": IMAGE_MODEL, "status": SUBMITTED, "submittedAt": now}
            conn.execute("update visual_pins set concept_json=?,status=?,updated_at=? where id=?", (json.dumps(concept, ensure_ascii=False), SUBMITTED, now, row["id"]))
    return {"batch": batch_name, "submitted": len(rows), "model": IMAGE_MODEL}


def load_batch(batch_name: str) -> dict:
    request = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/{urllib.parse.quote(batch_name, safe='/')}", headers={"x-goog-api-key": gemini_key()})
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode())


def batch_for_site(site_id: int, requested_batch: str = "") -> tuple[str, list]:
    with app.db() as conn:
        all_rows = conn.execute("select * from visual_pins where site_id=? and mode='article_derived_pin' order by id", (site_id,)).fetchall()
    rows = []
    for row in all_rows:
        name = normalized((app.parse_json_object(row["concept_json"]).get("batch") or {}).get("name"))
        if name and (not requested_batch or name == requested_batch):
            rows.append(row)
    names = {normalized((app.parse_json_object(row["concept_json"]).get("batch") or {}).get("name")) for row in rows}
    names.discard("")
    if len(names) != 1:
        raise RuntimeError("Pins do not resolve to exactly one requested batch")
    return next(iter(names)), rows


def first_image(response: dict) -> bytes:
    for candidate in response.get("candidates") or []:
        for part in ((candidate.get("content") or {}).get("parts") or []):
            inline = part.get("inlineData") or part.get("inline_data") or {}
            if inline.get("data"):
                return base64.b64decode(inline["data"])
    raise RuntimeError("batch response contains no image")


def load_finish_config(path: str) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != "article-derived-pin-finish/v1":
        raise RuntimeError("finish config must use article-derived-pin-finish/v1")
    if payload.get("layout") != "top_gradient_panel":
        raise RuntimeError("unsupported Pin finish layout")
    if not isinstance(payload.get("pins"), dict):
        raise RuntimeError("finish config must contain a pins object")
    return payload


def finish_for_row(config: dict, concept: dict) -> dict:
    key = normalized(concept.get("ledgerKey"))
    pin = config["pins"].get(key)
    if not isinstance(pin, dict):
        raise RuntimeError(f"{key}: finish config is missing")
    lines = [normalized(value) for value in pin.get("lines") or []]
    overlay = normalized(concept.get("overlayText"))
    if not 2 <= len(lines) <= 4 or normalized(" ".join(lines)) != overlay:
        raise RuntimeError(f"{key}: finish lines do not reproduce the exact overlay")
    accent_line = int(pin.get("accentLine", -1))
    if accent_line < 0 or accent_line >= len(lines):
        raise RuntimeError(f"{key}: invalid accent line")
    return {
        "layout": config["layout"],
        "panelHeight": int(config.get("panelHeight") or 450),
        "gradientStart": normalized(config.get("gradientStart") or "#0B3B72"),
        "gradientEnd": normalized(config.get("gradientEnd") or "#06162F"),
        "textColor": normalized(config.get("textColor") or "#FFFFFF"),
        "accentColor": normalized(config.get("accentColor") or "#18C2C7"),
        "logoRelative": normalized(config.get("logoRelative")),
        "logoWidth": int(config.get("logoWidth") or 230),
        "logoBottom": int(config.get("logoBottom") or 18),
        "lines": lines,
        "accentLine": accent_line,
    }


def pin_font_path() -> str:
    candidates = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Avenir Next.ttc",
    )
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate
    raise RuntimeError("no supported bold Pin font is installed")


def fit_finish_font(draw, lines: list[str], font_path: str, max_width: int, max_height: int):
    from PIL import ImageFont
    for size in range(118, 49, -2):
        font = ImageFont.truetype(font_path, size)
        boxes = [draw.textbbox((0, 0), value, font=font) for value in lines]
        widths = [box[2] - box[0] for box in boxes]
        heights = [box[3] - box[1] for box in boxes]
        # A glyph bounding box is much shorter than the font's nominal size.
        # Tight spacing based on that box can make uppercase lines visually
        # collide even when their numeric boxes do not overlap.  Keep a real,
        # mobile-readable gap proportional to the selected font size.
        spacing = max(20, round(size * 0.20))
        height = sum(heights) + spacing * (len(lines) - 1)
        if max(widths) <= max_width and height <= max_height:
            return font, boxes, spacing
    raise RuntimeError("overlay cannot fit safely")


def _hex_color(value: str) -> tuple[int, int, int]:
    cleaned = normalized(value).lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", cleaned):
        raise RuntimeError(f"invalid finish colour: {value}")
    return tuple(int(cleaned[index:index + 2], 16) for index in (0, 2, 4))


def trim_uniform_bands(source):
    from PIL import ImageStat
    height = source.height
    strip_height = max(4, height // 160)
    top_boundary = 0
    for top in range(0, min(height // 3, height // 2), strip_height):
        bottom = min(height, top + strip_height)
        stats = ImageStat.Stat(source.crop((0, top, source.width, bottom)).convert("L"))
        mean = stats.mean[0]
        deviation = stats.stddev[0]
        if (mean <= 42 or mean >= 225) and deviation <= 18:
            top_boundary = bottom
        elif top_boundary:
            break
    bottom_boundary = height
    for bottom in range(height, max(height // 2, height - height // 3), -strip_height):
        top = max(0, bottom - strip_height)
        stats = ImageStat.Stat(source.crop((0, top, source.width, bottom)).convert("L"))
        mean = stats.mean[0]
        deviation = stats.stddev[0]
        if (mean <= 42 or mean >= 225) and deviation <= 18:
            bottom_boundary = top
        elif bottom_boundary < height:
            break
    if top_boundary < height * 0.06:
        top_boundary = 0
    if height - bottom_boundary < height * 0.06:
        bottom_boundary = height
    if bottom_boundary - top_boundary < height * 0.45:
        return source
    source = source.crop((0, top_boundary, source.width, bottom_boundary))
    height = source.height
    strip_height = max(4, height // 160)
    runs = []
    run_start = None
    for top in range(0, height, strip_height):
        bottom = min(height, top + strip_height)
        stats = ImageStat.Stat(source.crop((0, top, source.width, bottom)).convert("L"))
        mean = stats.mean[0]
        deviation = stats.stddev[0]
        uniform = (mean <= 42 or mean >= 225) and deviation <= 18
        if uniform and run_start is None:
            run_start = top
        elif not uniform and run_start is not None:
            runs.append((run_start, top))
            run_start = None
    if run_start is not None:
        runs.append((run_start, height))
    substantial = [run for run in runs if run[1] - run[0] >= height * 0.08]
    if substantial:
        start, end = max(substantial, key=lambda run: run[1] - run[0])
        before = start
        after = height - end
        if max(before, after) >= height * 0.40:
            if after >= before:
                return source.crop((0, end, source.width, height))
            return source.crop((0, 0, source.width, start))
    return source


def compose(raw: bytes, overlay: str, logo_path: str, finish: dict) -> bytes:
    from PIL import Image, ImageDraw, ImageOps
    if normalized(" ".join(finish["lines"])) != normalized(overlay):
        raise RuntimeError("finish lines changed the exact overlay")
    panel_height = int(finish["panelHeight"])
    if not 360 <= panel_height <= 520:
        raise RuntimeError("panel height must be 360..520")
    photo_height = 1500 - panel_height
    source = trim_uniform_bands(Image.open(BytesIO(raw)).convert("RGB"))
    photo = ImageOps.fit(source, (1000, photo_height), method=Image.Resampling.LANCZOS, centering=(0.5, 1.0))
    canvas = Image.new("RGBA", (1000, 1500), (255, 255, 255, 255))
    canvas.alpha_composite(photo.convert("RGBA"), (0, panel_height))
    gradient_start = _hex_color(finish["gradientStart"])
    gradient_end = _hex_color(finish["gradientEnd"])
    panel = Image.new("RGBA", (1000, panel_height), (*gradient_start, 255))
    panel_draw = ImageDraw.Draw(panel)
    for x in range(1000):
        ratio = x / 999
        color = tuple(round(gradient_start[i] * (1 - ratio) + gradient_end[i] * ratio) for i in range(3))
        panel_draw.line((x, 0, x, panel_height), fill=(*color, 255))
    canvas.alpha_composite(panel, (0, 0))
    draw = ImageDraw.Draw(canvas)
    lines = finish["lines"]
    font, boxes, spacing = fit_finish_font(draw, lines, pin_font_path(), 900, panel_height - 72)
    heights = [box[3] - box[1] for box in boxes]
    total = sum(heights) + spacing * (len(lines) - 1)
    y = (panel_height - total) // 2
    text_color = (*_hex_color(finish["textColor"]), 255)
    accent_color = (*_hex_color(finish["accentColor"]), 255)
    rendered_boxes = []
    for index, (line, box, height) in enumerate(zip(lines, boxes, heights)):
        width = box[2] - box[0]
        x = (1000 - width) // 2 - box[0]
        baseline_y = y - box[1]
        rendered_box = draw.textbbox((x, baseline_y), line, font=font)
        if rendered_boxes and rendered_box[1] - rendered_boxes[-1][3] < 18:
            raise RuntimeError("headline lines do not have a safe visual gap")
        rendered_boxes.append(rendered_box)
        draw.text((x, baseline_y), line, font=font, fill=accent_color if index == finish["accentLine"] else text_color)
        y += height + spacing
    if rendered_boxes[0][1] < 36 or rendered_boxes[-1][3] > panel_height - 36:
        raise RuntimeError("headline violates panel safety padding")
    logo = Image.open(logo_path).convert("RGBA")
    logo_width = int(finish["logoWidth"])
    if not 120 <= logo_width <= 320:
        raise RuntimeError("logo width must be 120..320")
    logo.thumbnail((logo_width, logo_width), Image.Resampling.LANCZOS)
    logo_x = (1000 - logo.width) // 2
    logo_y = 1500 - int(finish["logoBottom"]) - logo.height
    if logo_y < panel_height:
        raise RuntimeError("logo overlaps the headline panel")
    canvas.alpha_composite(logo, (logo_x, logo_y))
    out = BytesIO()
    canvas.convert("RGB").save(out, "JPEG", quality=92, optimize=True, progressive=True)
    return out.getvalue()


def status(site_id: int, requested_batch: str = "") -> dict:
    batch_name, rows = batch_for_site(site_id, requested_batch)
    batch = load_batch(batch_name)
    return {"batch": batch_name, "pins": len(rows), "state": (batch.get("metadata") or {}).get("state")}


def collect(site_id: int, logo_relative: str, requested_batch: str = "", finish_config_path: str = "") -> dict:
    batch_name, rows = batch_for_site(site_id, requested_batch)
    batch = load_batch(batch_name)
    metadata = batch.get("metadata") or {}
    if metadata.get("state") != "BATCH_STATE_SUCCEEDED":
        raise RuntimeError(f"batch is not complete: {metadata.get('state')}")
    container = (metadata.get("output") or {}).get("inlinedResponses") or {}
    responses = container.get("inlinedResponses") if isinstance(container, dict) else container
    response_by_key = {normalized((item.get("metadata") or {}).get("key")): item.get("response") or {} for item in responses or []}
    missing = [row["id"] for row in rows if row["id"] not in response_by_key]
    if missing:
        raise RuntimeError(f"batch omitted {len(missing)} Pins")
    # Decode every provider response before writing any file or changing any
    # status.  A single failed request must not leave a half-collected ledger.
    raw_by_id = {row["id"]: first_image(response_by_key[row["id"]]) for row in rows}
    finish_config = load_finish_config(finish_config_path) if finish_config_path else None
    site = app.get_site(site_id)
    configured_logo = normalized((finish_config or {}).get("logoRelative")) or logo_relative
    logo_path = (Path(site["root_path"]).resolve() / configured_logo).resolve()
    if Path(site["root_path"]).resolve() not in logo_path.parents or not logo_path.is_file():
        raise RuntimeError("site-owned logo is missing")
    finished_by_id = {}
    for row in rows:
        concept = app.parse_json_object(row["concept_json"])
        if finish_config:
            finish = finish_for_row(finish_config, concept)
        else:
            raise RuntimeError("--finish-config is required for article-derived Pin collection")
        finished_by_id[row["id"]] = (compose(raw_by_id[row["id"]], concept["overlayText"], str(logo_path), finish), finish)
    now = app.now_iso()
    for row in rows:
        concept = app.parse_json_object(row["concept_json"])
        final, finish = finished_by_id[row["id"]]
        target = app.visual_pin_asset_dir(site_id, row["id"])
        target.mkdir(parents=True, exist_ok=True)
        (target / "pin.jpg").write_bytes(final)
        concept["batch"].update({"status": "COLLECTED", "collectedAt": now})
        concept["finish"] = finish
        with app.db() as conn:
            conn.execute("update visual_pins set concept_json=?,image_filename='pin.jpg',status='DRAFT',error=null,updated_at=? where id=?", (json.dumps(concept, ensure_ascii=False), now, row["id"]))
    return {"batch": batch_name, "collected": len(rows), "status": "DRAFT", "published": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("seed", "submit", "status", "collect"))
    parser.add_argument("--site-id", type=int, required=True)
    parser.add_argument("--ledger")
    parser.add_argument("--preview-dir")
    parser.add_argument("--expected", type=int, default=41)
    parser.add_argument("--logo-relative", default="assets/brand/logo-email.png")
    parser.add_argument("--finish-config", default="")
    parser.add_argument("--batch-name", default="")
    args = parser.parse_args()
    if args.action == "seed":
        if not args.ledger:
            raise RuntimeError("--ledger is required for seed")
        result = seed(args.site_id, args.ledger, args.preview_dir)
    elif args.action == "submit":
        result = submit(args.site_id, args.expected)
    elif args.action == "status":
        result = status(args.site_id, args.batch_name)
    else:
        result = collect(args.site_id, args.logo_relative, args.batch_name, args.finish_config)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
