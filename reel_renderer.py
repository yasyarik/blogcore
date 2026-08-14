#!/usr/bin/env python3
"""Layer-first vertical video renderer used by Blog Core Instagram Reels."""

from __future__ import annotations

import math
import subprocess
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageStat
from scipy import ndimage


WIDTH = 1080
HEIGHT = 1920
FPS = 24


def _font(size: int, bold: bool = False):
    candidates = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ) if bold else (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    )
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def _ease(value: float) -> float:
    value = min(1.0, max(0.0, value))
    return 1 - (1 - value) ** 3


def _cover(image: Image.Image, zoom: float, pan_x: float, pan_y: float) -> Image.Image:
    image = image.convert("RGB")
    scale = max(WIDTH / image.width, HEIGHT / image.height) * zoom
    size = (max(WIDTH, round(image.width * scale)), max(HEIGHT, round(image.height * scale)))
    canvas = image.resize(size, Image.Resampling.LANCZOS)
    extra_x = max(0, canvas.width - WIDTH)
    extra_y = max(0, canvas.height - HEIGHT)
    left = round(extra_x * min(1, max(0, 0.5 + pan_x)))
    top = round(extra_y * min(1, max(0, 0.5 + pan_y)))
    return canvas.crop((left, top, left + WIDTH, top + HEIGHT)).convert("RGBA")


def _cover_rgba(image: Image.Image, zoom: float, pan_x: float, pan_y: float) -> Image.Image:
    """Apply the identical whole-scene camera transform without discarding alpha."""
    image = image.convert("RGBA")
    scale = max(WIDTH / image.width, HEIGHT / image.height) * zoom
    size = (max(WIDTH, round(image.width * scale)), max(HEIGHT, round(image.height * scale)))
    resized = image.resize(size, Image.Resampling.LANCZOS)
    extra_x = max(0, resized.width - WIDTH)
    extra_y = max(0, resized.height - HEIGHT)
    left = round(extra_x * min(1, max(0, 0.5 + pan_x)))
    top = round(extra_y * min(1, max(0, 0.5 + pan_y)))
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


FULL_CANVAS_REVEALS = ("slide_left", "slide_right", "drop", "rise", "focus", "settle")


def _multiply_alpha(alpha: Image.Image, reveal: Image.Image) -> Image.Image:
    return ImageChops.multiply(alpha.convert("L"), reveal.convert("L"))


def _full_canvas_layer_frame(
    layer: Image.Image,
    spec: dict,
    progress: float,
    duration: float,
) -> tuple[Image.Image, str]:
    """Execute the approved manifest reveal for a registered full-canvas layer."""
    layer = ImageOps.fit(layer.convert("RGBA"), (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    mode = str(spec.get("manifestReveal") or "")
    motion = str(spec.get("manifestMotion") or "")
    if mode not in FULL_CANVAS_REVEALS or motion != "hold":
        raise ValueError("Registered Reel layer has no supported approved reveal contract")
    try:
        start = float(spec.get("manifestStartSeconds")) / duration
        end = float(spec.get("manifestEndSeconds")) / duration
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError("Registered Reel layer has invalid approved timing") from error
    if not 0 <= start < end <= 1.0:
        raise ValueError("Registered Reel layer entrance must finish before camera motion")
    amount = _ease((progress - start) / (end - start))
    alpha = layer.getchannel("A")
    if amount <= 0:
        layer.putalpha(Image.new("L", (WIDTH, HEIGHT), 0))
        return layer, mode
    if mode == "focus":
        layer.putalpha(alpha.point(lambda value: round(value * amount)))
        if amount < 0.995:
            layer = layer.filter(ImageFilter.GaussianBlur(max(0.0, (1.0 - amount) * 14.0)))
        return layer, mode
    if mode == "settle":
        bbox = alpha.getbbox()
        if not bbox:
            return layer, mode
        scale = 0.88 + 0.12 * amount
        subject = layer.crop(bbox)
        resized = subject.resize(
            (max(1, round(subject.width * scale)), max(1, round(subject.height * scale))),
            Image.Resampling.LANCZOS,
        )
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        x = round(center_x - resized.width / 2)
        y = round(center_y - resized.height / 2 + (1.0 - amount) * 48)
        settled = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        settled.alpha_composite(resized, (x, y))
        return settled, mode

    offsets = {
        "slide_left": (-WIDTH, 0),
        "slide_right": (WIDTH, 0),
        "drop": (0, -HEIGHT),
        "rise": (0, HEIGHT),
    }
    start_x, start_y = offsets[mode]
    offset_x = round(start_x * (1.0 - amount))
    offset_y = round(start_y * (1.0 - amount))
    shifted = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shifted.alpha_composite(layer, (offset_x, offset_y))
    layer = shifted
    return layer, mode


def _decorate_registered_layer(layer: Image.Image) -> Image.Image:
    """Build natural separation once without a sticker-like silhouette outline."""
    alpha = layer.getchannel("A")
    soft_alpha = alpha.filter(ImageFilter.GaussianBlur(24)).point(lambda value: round(value * 0.42))
    contact_alpha = alpha.filter(ImageFilter.GaussianBlur(8)).point(lambda value: round(value * 0.16))
    soft_shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    soft_shadow.putalpha(soft_alpha)
    contact_shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    contact_shadow.putalpha(contact_alpha)
    decorated = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    decorated.alpha_composite(soft_shadow, (14, 22))
    decorated.alpha_composite(contact_shadow, (6, 10))
    decorated.alpha_composite(layer)
    return decorated


def _composite_full_canvas_layer(base: Image.Image, layer: Image.Image):
    base.alpha_composite(layer)


def _refine_legacy_registered_edge(layer: Image.Image, clean_background: Image.Image) -> Image.Image:
    """Remove binary-mask background fringe from already checkpointed registered layers."""
    layer = ImageOps.fit(layer.convert("RGBA"), (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    alpha_image = layer.getchannel("A")
    extrema = alpha_image.getextrema()
    if extrema == (0, 0):
        return layer
    histogram = alpha_image.histogram()
    intermediate_pixels = sum(histogram[1:255])
    opaque_pixels = histogram[255]
    # Current matte packs already have a soft, decontaminated edge. This path is
    # only for older binary checkpoint layers so they can be safely re-rendered.
    if intermediate_pixels > max(64, round(opaque_pixels * 0.002)):
        return layer
    clean = ImageOps.fit(clean_background.convert("RGB"), (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    # Preserve hands, clothing and other narrow details. Residual legacy fringe
    # is concealed by the renderer's outline instead of eroding the subject.
    inner = alpha_image.filter(ImageFilter.MinFilter(3))
    soft_alpha = inner.filter(ImageFilter.GaussianBlur(0.7))
    alpha = np.asarray(soft_alpha, dtype=np.float32) / 255.0
    source_rgb = np.asarray(layer.convert("RGB"), dtype=np.float32)
    clean_rgb = np.asarray(clean, dtype=np.float32)
    safe_alpha = np.maximum(alpha[..., None], 0.08)
    foreground = (source_rgb - (1.0 - alpha[..., None]) * clean_rgb) / safe_alpha
    foreground = np.clip(foreground, 0, 255).astype(np.uint8)
    interior_image = alpha_image.filter(ImageFilter.MinFilter(9))
    interior = np.asarray(interior_image, dtype=np.uint8) > 250
    edge = (np.asarray(soft_alpha, dtype=np.uint8) > 0) & ~interior
    if interior.any() and edge.any():
        nearest = ndimage.distance_transform_edt(~interior, return_distances=False, return_indices=True)
        foreground[edge] = source_rgb.astype(np.uint8)[nearest[0][edge], nearest[1][edge]]
    foreground[alpha <= 0.001] = 0
    result = np.zeros((HEIGHT, WIDTH, 4), dtype=np.uint8)
    result[..., :3] = foreground
    result[..., 3] = np.asarray(soft_alpha, dtype=np.uint8)
    return Image.fromarray(result, "RGBA")


def _camera_values(kind: str, progress: float) -> tuple[float, float, float]:
    eased = _ease(progress)
    if kind == "dolly_out":
        return 1.14 - 0.085 * eased, 0.5, 0.02 - 0.04 * eased
    if kind == "tracking_left":
        return 1.05 + 0.065 * eased, 0.22 + 0.25 * eased, -0.04
    if kind == "tracking_right":
        return 1.05 + 0.065 * eased, 0.78 - 0.25 * eased, 0.04
    if kind == "follow_left":
        return 1.10 + 0.025 * eased, 0.20 + 0.34 * eased, 0.08 - 0.10 * eased
    if kind == "follow_right":
        return 1.10 + 0.025 * eased, 0.80 - 0.34 * eased, -0.04 + 0.10 * eased
    if kind == "crane_up":
        return 1.05 + 0.06 * eased, 0.5, 0.17 - 0.3 * eased
    if kind == "crane_down":
        return 1.05 + 0.06 * eased, 0.5, -0.17 + 0.3 * eased
    if kind == "orbit":
        return 1.06 + 0.07 * eased, 0.4 + 0.19 * eased, -0.08 + 0.16 * eased
    return 1.04 + 0.09 * eased, 0.5, 0.0


def _mix_camera(first, second, amount):
    amount = min(1.0, max(0.0, amount))
    amount = amount * amount * (3.0 - 2.0 * amount)
    return tuple(first[index] + (second[index] - first[index]) * amount for index in range(3))


def _layer_focus_targets(foregrounds: list[Image.Image], layer_specs: list[dict]):
    targets = {}
    for index, foreground in enumerate(foregrounds):
        spec = layer_specs[index] if index < len(layer_specs) else {}
        fitted = ImageOps.fit(foreground.convert("RGBA"), (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
        bbox = fitted.getchannel("A").getbbox()
        if not bbox:
            continue
        center_x = ((bbox[0] + bbox[2]) / 2) / WIDTH
        layer_type = str(spec.get("layerType") or spec.get("type") or "")
        role = str(spec.get("role") or spec.get("storyRole") or "")
        is_person = layer_type == "person_group" or role in {"protagonist", "supporting_character"}
        focus_fraction = 0.24 if is_person else 0.50
        focus_y = (bbox[1] + (bbox[3] - bbox[1]) * focus_fraction) / HEIGHT
        targets[str(spec.get("id") or index)] = {
            "camera": (1.68 if is_person else 1.74, min(0.88, max(0.12, center_x)), min(0.34, max(-0.34, focus_y - 0.5))),
            "kind": "person" if is_person else "object",
            "area": ((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])) / (WIDTH * HEIGHT),
        }
    return targets


def _target_camera(record, default=(1.42, 0.5, 0.0)):
    if isinstance(record, dict) and isinstance(record.get("camera"), tuple):
        return record["camera"]
    if isinstance(record, tuple) and len(record) == 3:
        return record
    return default


def _pick_camera_target(targets: dict, requested: str, movement: str, used: set[str]):
    requested_record = targets.get(requested)
    preferred_kind = "object" if movement == "object_zoom" else "person" if movement == "face_zoom" else ""
    # The director's named target is authoritative, including a deliberate
    # return to the same subject for a tighter shot later in the scene.
    if requested_record:
        return requested, requested_record
    candidates = [
        (name, record) for name, record in targets.items()
        if name not in used and (not preferred_kind or record.get("kind") == preferred_kind)
    ]
    if not candidates:
        candidates = [(name, record) for name, record in targets.items() if name not in used]
    if not candidates:
        return "", None
    return max(candidates, key=lambda item: float(item[1].get("area") or 0))


def _subject_camera_values(kind: str, progress: float, targets, scene_index: int):
    base = _camera_values(kind, 0.0)
    if progress <= 0.46 or not targets:
        return base
    ordered = [_target_camera(value) for value in targets.values()] if isinstance(targets, dict) else list(targets)
    first = ordered[0]
    if progress < 0.62:
        return _mix_camera(base, first, (progress - 0.46) / 0.16)
    if progress < 0.70:
        return first
    if len(ordered) > 1:
        neutral = _camera_values(kind, 0.45)
        if progress < 0.82:
            return _mix_camera(first, neutral, (progress - 0.70) / 0.12)
        second = ordered[1]
        if progress < 0.94:
            return _mix_camera(neutral, second, (progress - 0.82) / 0.12)
        return second
    end = _camera_values(kind, 1.0)
    return _mix_camera(first, end, (progress - 0.70) / 0.30)


def _director_camera_values(scene: dict, progress: float, targets: dict):
    """Turn all director beats into one continuous time-aware camera trajectory."""
    duration = float(scene.get("durationSeconds") or 0)
    plan = scene.get("directorCameraPlan") if isinstance(scene.get("directorCameraPlan"), dict) else {}
    beats = [item for item in plan.get("beats") or [] if isinstance(item, dict)]
    if duration <= 0 or not beats:
        return _subject_camera_values(str(scene.get("cameraMove") or "dolly_in"), progress, targets, int(scene.get("index") or 1))
    second = progress * duration
    state = (1.035, 0.5, 0.0)
    used_targets: set[str] = set()
    keyframes = [(0.0, state)]
    for beat_index, beat in enumerate(beats):
        start = max(0.0, min(duration, float(beat.get("startSeconds") or 0.0)))
        end = float(beat.get("endSeconds") or duration)
        movement = str(beat.get("movement") or "")
        target_name, target_record = _pick_camera_target(
            targets,
            str(beat.get("focusTarget") or ""),
            movement,
            used_targets,
        )
        if target_name:
            used_targets.add(target_name)
        target = _target_camera(target_record, state)
        target_kind = str((target_record or {}).get("kind") or "")
        framing = str(beat.get("toFraming") or "").lower()
        if movement == "environment_pan_left":
            destination = (1.10, 0.42, -0.01)
        elif movement == "environment_pan_right":
            destination = (1.10, 0.58, -0.01)
        elif movement == "pull_out":
            destination = (1.035, 0.5, 0.0)
        elif movement in {"pan_left", "pan_right", "track_left", "track_right", "follow_left", "follow_right"}:
            # A lateral move ends on a close frame, not another wide crop.
            destination = (2.20 if target_kind == "person" else 1.92, target[1], target[2])
        elif movement in {"object_zoom", "face_zoom"}:
            destination = (2.34 if target_kind == "person" else 2.18, target[1], target[2])
        elif movement in {"push_in", "rack_focus", "focus_transfer"}:
            if "close-up" in framing or "close up" in framing or "tight" in framing:
                zoom = 2.30 if target_kind == "person" else 2.12
            elif "medium close" in framing or "waist" in framing:
                zoom = 2.24 if beat_index and target_kind == "person" else 1.82
            elif "medium" in framing or "wide" in framing:
                zoom = 1.52 if beat_index else 1.46
            elif movement in {"rack_focus", "focus_transfer"}:
                zoom = 2.30 if target_kind == "person" else 2.12
            else:
                zoom = 1.52 if beat_index else 1.46
            destination = (zoom, target[1], target[2])
        else:
            destination = (1.40, target[1], target[2])
        if start > keyframes[-1][0] + 0.001:
            keyframes.append((start, state))
        keyframe_time = max(keyframes[-1][0] + 0.001, min(duration, end))
        keyframes.append((keyframe_time, destination))
        state = destination
    if scene.get("usesLogoReference"):
        # A brand-resolution scene must finish by revealing the complete
        # physical context that carries the verified mark, never on a crop
        # that pushes that mark outside the frame.
        reveal_start = duration * 0.76
        if keyframes[-1][0] >= reveal_start:
            keyframes[-1] = (reveal_start, keyframes[-1][1])
        elif keyframes[-1][0] < reveal_start:
            keyframes.append((reveal_start, keyframes[-1][1]))
        keyframes.append((duration, (1.035, 0.5, 0.0)))
    if keyframes[-1][0] < duration:
        # Continue a restrained drift through the cut instead of freezing on
        # the last destination.
        zoom, pan_x, pan_y = keyframes[-1][1]
        direction = -1 if int(scene.get("index") or 1) % 2 else 1
        keyframes.append((duration, (zoom * 1.025, pan_x + 0.018 * direction, pan_y - 0.008)))
    if second <= keyframes[0][0]:
        return keyframes[0][1]
    for index in range(len(keyframes) - 1):
        start_time, current = keyframes[index]
        end_time, following = keyframes[index + 1]
        if second > end_time and index < len(keyframes) - 2:
            continue
        previous = keyframes[index - 1][1] if index else current
        after = keyframes[index + 2][1] if index + 2 < len(keyframes) else following
        amount = min(1.0, max(0.0, (second - start_time) / max(0.001, end_time - start_time)))
        # Cubic Hermite/Catmull-Rom interpolation keeps both position and
        # velocity continuous at shot-scale and focus-transfer keyframes.
        h00 = 2 * amount ** 3 - 3 * amount ** 2 + 1
        h10 = amount ** 3 - 2 * amount ** 2 + amount
        h01 = -2 * amount ** 3 + 3 * amount ** 2
        h11 = amount ** 3 - amount ** 2
        values = []
        for axis in range(3):
            tangent_in = (following[axis] - previous[axis]) * 0.5
            tangent_out = (after[axis] - current[axis]) * 0.5
            values.append(h00 * current[axis] + h10 * tangent_in + h01 * following[axis] + h11 * tangent_out)
        return (
            min(2.45, max(1.02, values[0])),
            min(0.92, max(0.08, values[1])),
            min(0.42, max(-0.42, values[2])),
        )
    return keyframes[-1][1]


TEXT_ZONES = {
    "top_left": (54, 100, 826, 560),
    "top_right": (254, 100, 1026, 560),
    "middle_left": (54, 690, 826, 1150),
    "middle_right": (254, 690, 1026, 1150),
    "lower_left": (54, 1260, 826, 1720),
    "lower_right": (254, 1260, 1026, 1720),
}


def _choose_text_placement(background: Image.Image, foregrounds: list[Image.Image], layer_specs: list[dict], requested: str) -> str:
    assembled = ImageOps.fit(background.convert("RGBA"), (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    occupied = Image.new("L", (WIDTH, HEIGHT), 0)
    important = Image.new("L", (WIDTH, HEIGHT), 0)
    for index, foreground in enumerate(foregrounds):
        fitted = ImageOps.fit(foreground.convert("RGBA"), (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
        alpha = fitted.getchannel("A")
        occupied = ImageChops.lighter(occupied, alpha)
        spec = layer_specs[index] if index < len(layer_specs) else {}
        if str(spec.get("role") or "") in {"protagonist", "supporting_character"}:
            bbox = alpha.getbbox()
            if bbox:
                face_bottom = bbox[1] + round((bbox[3] - bbox[1]) * 0.42)
                face_box = (max(0, bbox[0] - 55), max(0, bbox[1] - 55), min(WIDTH, bbox[2] + 55), min(HEIGHT, face_bottom + 55))
                face = Image.new("L", (WIDTH, HEIGHT), 0)
                ImageDraw.Draw(face).rectangle(face_box, fill=255)
                important = ImageChops.lighter(important, face)
        assembled.alpha_composite(fitted)
    grayscale = assembled.convert("L")
    edges = grayscale.filter(ImageFilter.FIND_EDGES)
    scored = []
    for name, box in TEXT_ZONES.items():
        occupancy = ImageStat.Stat(occupied.crop(box)).mean[0] / 255.0
        face_occupancy = ImageStat.Stat(important.crop(box)).mean[0] / 255.0
        texture = ImageStat.Stat(grayscale.crop(box)).stddev[0]
        edge = ImageStat.Stat(edges.crop(box)).mean[0]
        lower_penalty = 4.0 if name.startswith("lower") else 0.0
        preference_bonus = -4.0 if name == requested else 0.0
        scored.append((face_occupancy * 2200.0 + occupancy * 820.0 + texture + edge * 0.7 + lower_penalty + preference_bonus, name))
    return min(scored)[1]


def _caption_palette(canvas: Image.Image, placement: str):
    """Reel captions stay light; contrast comes from shadow and an adaptive scrim."""
    return (247, 253, 255), (1, 11, 22)


def _wrap_words(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[list[str]]:
    lines: list[list[str]] = []
    current: list[str] = []
    for word in (text or "").split():
        candidate = current + [word]
        candidate_text = " ".join(candidate)
        if current and draw.textbbox((0, 0), candidate_text, font=font)[2] > max_width:
            lines.append(current)
            current = [word]
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _text_position(placement: str, text_width: int, line_width: int) -> int:
    box = TEXT_ZONES.get(placement, TEXT_ZONES["top_left"])
    if placement.endswith("right"):
        return box[2] - line_width
    return box[0]


@lru_cache(maxsize=len(TEXT_ZONES))
def _caption_scrim_mask(placement: str) -> Image.Image:
    box = TEXT_ZONES.get(placement, TEXT_ZONES["top_left"])
    height, width = box[3] - box[1], box[2] - box[0]
    ys = np.linspace(0.0, 1.0, height, dtype=np.float32)
    xs = np.linspace(0.0, 1.0, width, dtype=np.float32)
    vertical = np.clip(1.0 - np.abs(ys - 0.42) / 0.58, 0.0, 1.0)
    horizontal = np.clip(np.minimum(xs / 0.10, (1.0 - xs) / 0.10), 0.0, 1.0)
    zone = Image.fromarray(np.round(vertical[:, None] * horizontal[None, :] * 150).astype(np.uint8), "L")
    zone = zone.filter(ImageFilter.GaussianBlur(36))
    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    mask.paste(zone, (box[0], box[1]))
    return mask


def _draw_caption_scrim(canvas: Image.Image, placement: str, text_fill: tuple[int, int, int], opacity: float):
    box = TEXT_ZONES.get(placement, TEXT_ZONES["top_left"])
    crop = canvas.convert("L").crop(box)
    stats = ImageStat.Stat(crop)
    if stats.stddev[0] < 25 and (stats.mean[0] < 92 or stats.mean[0] > 174):
        return
    local_rgb = ImageStat.Stat(canvas.convert("RGB").crop(box)).mean
    if sum(text_fill) > 420:
        color = tuple(max(0, round(channel * 0.30)) for channel in local_rgb)
    else:
        color = tuple(min(255, round(channel * 0.55 + 112)) for channel in local_rgb)
    scrim = Image.new("RGBA", (WIDTH, HEIGHT), (*color, 0))
    mask = _caption_scrim_mask(placement).point(
        lambda value: round(value * min(1.0, max(0.0, opacity)))
    )
    scrim.putalpha(mask)
    canvas.alpha_composite(scrim)


def _draw_kinetic_caption(canvas: Image.Image, scene: dict, progress: float, accent: tuple[int, int, int]):
    """Reveal the actual hook word-by-word without a card or generic dashboard UI."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    composition = scene.get("composition") if isinstance(scene.get("composition"), dict) else {}
    placement = str(composition.get("textPlacement") or "top_left")
    text_fill, _ = _caption_palette(canvas, placement)
    supporting_font = _font(34)
    hook = str(scene.get("overlayText") or scene.get("title") or "").strip()
    supporting = str(scene.get("supportingText") or "").strip()
    text_direction = scene.get("textDirection") if isinstance(scene.get("textDirection"), dict) else {}
    duration = float(scene.get("durationSeconds") or 1)
    start = float(text_direction.get("startSeconds") or 0) / max(duration, 0.001)
    end = float(text_direction.get("endSeconds") or duration) / max(duration, 0.001)
    if progress < start or progress > end:
        return
    text_progress = (progress - start) / max(0.001, end - start)
    scrim_opacity = min(1.0, text_progress / 0.12)
    _draw_caption_scrim(canvas, placement, text_fill, scrim_opacity)
    target_lines = min(3, max(1, int(text_direction.get("maxLines") or 3)))
    font_size = 132
    hook_font = _font(font_size, bold=True)
    zone = TEXT_ZONES.get(placement, TEXT_ZONES["top_left"])
    max_text_width = zone[2] - zone[0]
    lines = _wrap_words(draw, hook, hook_font, max_text_width)
    while len(lines) > target_lines and font_size > 88:
        font_size -= 4
        hook_font = _font(font_size, bold=True)
        lines = _wrap_words(draw, hook, hook_font, max_text_width)
    if not lines:
        return
    if len(lines) > target_lines:
        raise ValueError("Reel overlay cannot fit as one readable title")
    local_progress = text_progress
    line_height = round(font_size * 1.1)
    top = zone[1] + 26
    word_index = 0
    for line_index, line in enumerate(lines):
        line_text = " ".join(line)
        line_width = draw.textbbox((0, 0), line_text, font=hook_font)[2]
        x = _text_position(placement, WIDTH, line_width)
        y = top + line_index * line_height
        for word in line:
            reveal = _ease((local_progress - 0.03 - word_index * 0.055) / 0.18)
            if reveal > 0:
                word_width = draw.textbbox((0, 0), word, font=hook_font)[2]
                alpha = round(255 * reveal)
                # A soft offset shadow separates type without the rough outlined
                # lettering produced by contrasting strokes on photographic detail.
                draw.text(
                    (x + 5, y + round((1 - reveal) * 26) + 7),
                    word,
                    font=hook_font,
                    fill=(0, 0, 0, round(155 * reveal)),
                )
                draw.text(
                    (x, y + round((1 - reveal) * 26)),
                    word,
                    font=hook_font,
                    fill=(*text_fill, alpha),
                )
                x += word_width + draw.textbbox((0, 0), " ", font=hook_font)[2]
            word_index += 1
    final_reveal = _ease((local_progress - 0.10) / 0.40)
    underline_width = round(min(max_text_width, 190 + len(hook) * 10) * final_reveal)
    line_y = top + len(lines) * line_height + 12
    anchor_x = zone[2] - underline_width if placement.endswith("right") else zone[0]
    draw.rounded_rectangle((anchor_x, line_y, anchor_x + underline_width, line_y + 7), radius=4, fill=(*accent, round(235 * final_reveal)))
    if supporting and final_reveal > 0:
        max_width = max_text_width
        support_lines = _wrap_words(draw, supporting, supporting_font, max_width)[:2]
        support_y = line_y + 28 + round((1 - final_reveal) * 12)
        for line in support_lines:
            line_text = " ".join(line)
            line_width = draw.textbbox((0, 0), line_text, font=supporting_font)[2]
            support_x = _text_position(placement, WIDTH, line_width)
            draw.text(
                (support_x + 3, support_y + 5),
                line_text,
                font=supporting_font,
                fill=(0, 0, 0, round(145 * final_reveal)),
            )
            draw.text(
                (support_x, support_y),
                line_text,
                font=supporting_font,
                fill=(*text_fill, round(235 * final_reveal)),
            )
            support_y += 43


def _composite_layer(base: Image.Image, layer: Image.Image, x: int, y: int, scale: float, alpha: float, rotation: float = 0):
    if alpha <= 0:
        return
    target_width = max(1, round(layer.width * scale))
    target_height = max(1, round(layer.height * scale))
    foreground = layer.resize((target_width, target_height), Image.Resampling.LANCZOS)
    if rotation:
        foreground = foreground.rotate(rotation, Image.Resampling.BICUBIC, expand=True)
    mask = foreground.getchannel("A")
    if alpha < 0.999:
        mask = mask.point(lambda value: round(value * alpha))
        foreground.putalpha(mask)
    soft_shadow = Image.new("RGBA", foreground.size, (0, 0, 0, 0))
    soft_shadow.putalpha(mask.filter(ImageFilter.GaussianBlur(30)).point(lambda value: round(value * 0.58)))
    contact_shadow = Image.new("RGBA", foreground.size, (0, 0, 0, 0))
    contact_shadow.putalpha(mask.filter(ImageFilter.GaussianBlur(9)).point(lambda value: round(value * 0.36)))
    base.alpha_composite(soft_shadow, (round(x + 30), round(y + 38)))
    base.alpha_composite(contact_shadow, (round(x + 11), round(y + 18)))
    base.alpha_composite(foreground, (round(x), round(y)))


def _layer_position(layer: dict, layer_index: int, width: int, height: int, progress: float) -> tuple[int, int, float, float]:
    """Animate a directed story layer inside one coherent scene, never a generic sticker."""
    placement = str(layer.get("placement") or "middle_center")
    entrance_kind = str(layer.get("entrance") or "fade")
    motion = str(layer.get("motion") or "hold")
    size = str(layer.get("size") or "medium")
    delay = 0.08 + layer_index * 0.16
    entrance = _ease((progress - delay) / 0.28)
    exit_progress = _ease((progress - 0.90 - layer_index * 0.015) / 0.10)
    alpha = entrance * (1.0 - exit_progress * 0.16)
    horizontal = "left" if placement.endswith("left") else "right" if placement.endswith("right") else "center"
    vertical = "top" if placement.startswith("top") else "lower" if placement.startswith("lower") else "middle"
    if horizontal == "left":
        x = 42
    elif horizontal == "right":
        x = WIDTH - width - 42
    else:
        x = (WIDTH - width) // 2
    if vertical == "top":
        y = 280
    elif vertical == "lower":
        y = HEIGHT - height - 175
    else:
        y = (HEIGHT - height) // 2 + 130
    if entrance_kind == "slide_left":
        x -= round((1.0 - entrance) * 210)
    elif entrance_kind == "slide_right":
        x += round((1.0 - entrance) * 210)
    elif entrance_kind == "rise":
        y += round((1.0 - entrance) * 170)
    elif entrance_kind == "scale_in":
        pass
    elif entrance_kind == "fade":
        y += round((1.0 - entrance) * 26)
    motion_amount = 22 if size == "small" else 30 if size == "medium" else 38
    if motion == "drift_left":
        x -= round((progress - 0.5) * motion_amount * 2)
    elif motion == "drift_right":
        x += round((progress - 0.5) * motion_amount * 2)
    elif motion == "rise":
        y -= round(progress * motion_amount * 2)
    elif motion == "fall":
        y += round(progress * motion_amount * 2)
    elif motion == "float":
        y += round(math.sin((progress * math.pi * 2.0) + layer_index * 1.7) * motion_amount)
    scale = 0.92 + 0.08 * entrance
    if entrance_kind == "scale_in":
        scale *= 0.78 + 0.22 * entrance
    if motion == "scale":
        scale *= 0.96 + 0.09 * _ease(progress)
    return x, y, scale, alpha


def _wav_duration(path: Path) -> float:
    try:
        with wave.open(str(path), "rb") as source:
            return source.getnframes() / float(source.getframerate())
    except (wave.Error, OSError, ZeroDivisionError):
        return 0.0


def _build_continuous_narration(loaded_scenes: list[dict], target_path: Path, fps: int) -> tuple[Path | None, list[tuple[float, float]]]:
    """Join scene narration into one timeline-aligned WAV before FFmpeg mixing."""
    voice_sources = [scene["voice_path"] for scene in loaded_scenes if scene.get("voice_path")]
    if not voice_sources:
        return None, []

    with wave.open(str(voice_sources[0]), "rb") as first_source:
        audio_format = (
            first_source.getnchannels(),
            first_source.getsampwidth(),
            first_source.getframerate(),
            first_source.getcomptype(),
        )
    intervals = []
    offset_seconds = 0.0
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(target_path), "wb") as output:
        output.setnchannels(audio_format[0])
        output.setsampwidth(audio_format[1])
        output.setframerate(audio_format[2])
        output.setcomptype(audio_format[3], "not compressed")
        for loaded_scene in loaded_scenes:
            scene_duration = loaded_scene["frame_count"] / fps
            voice_path = loaded_scene.get("voice_path")
            voice_frames = b""
            voice_duration = 0.0
            if voice_path:
                with wave.open(str(voice_path), "rb") as source:
                    current_format = (
                        source.getnchannels(),
                        source.getsampwidth(),
                        source.getframerate(),
                        source.getcomptype(),
                    )
                    if current_format != audio_format:
                        raise ValueError("All Reel narration clips must use the same WAV format")
                    voice_frames = source.readframes(source.getnframes())
                    voice_duration = source.getnframes() / float(source.getframerate())
                intervals.append((offset_seconds, min(offset_seconds + voice_duration, offset_seconds + scene_duration)))

            output.writeframes(voice_frames)
            written_duration = min(scene_duration, voice_duration)
            silence_duration = max(0.0, scene_duration - written_duration)
            silence_frames = round(silence_duration * audio_format[2])
            output.writeframes(b"\x00" * silence_frames * audio_format[0] * audio_format[1])
            offset_seconds += scene_duration

    return target_path, intervals


def _music_volume_expression(voice_intervals: list[tuple[float, float]]) -> str:
    """Keep the brand bed continuous while ducking it gently during spoken narration."""
    speaking = "+".join(f"between(t\\,{start:.3f}\\,{end:.3f})" for start, end in voice_intervals)
    return f"0.16-0.105*min(1\\,{speaking})" if speaking else "0.16"


def render_vertical_reel(
    scenes: list[dict],
    output_path: str | Path,
    work_dir: str | Path,
    fps: int = FPS,
    accent_hex: str = "#36d6c6",
    music_path: str | Path | None = None,
    narration_path: str | Path | None = None,
) -> dict:
    if not scenes:
        raise ValueError("A reel needs at least one scene")
    output_path = Path(output_path)
    work_dir = Path(work_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    accent_hex = accent_hex.lstrip("#")
    try:
        accent = tuple(int(accent_hex[index:index + 2], 16) for index in (0, 2, 4))
    except Exception:
        accent = (54, 214, 198)

    loaded = []
    total_frames = 0
    for scene in scenes:
        background_path = Path(scene["backgroundPath"])
        foreground_paths = [Path(path) for path in scene.get("foregroundPaths") or []]
        if not background_path.is_file() or len(foreground_paths) < 1:
            raise ValueError("Storyboard assets are incomplete")
        voice_path = Path(str(scene.get("voicePath") or ""))
        voice_duration = _wav_duration(voice_path) if voice_path.is_file() else 0.0
        planned_duration = float(scene.get("durationSeconds") or 4.0)
        overlay_word_count = len(str(scene.get("overlayText") or scene.get("title") or "").split())
        natural_reading_duration = 1.8 + overlay_word_count * 0.55
        # Duration expands to the actual content. Narration is never truncated or
        # accelerated to satisfy an arbitrary total Reel duration.
        duration = max(3.5, planned_duration, natural_reading_duration, voice_duration + 0.9)
        scene["durationSeconds"] = duration
        text_direction = scene.get("textDirection") if isinstance(scene.get("textDirection"), dict) else {}
        scene["textDirection"] = {**text_direction, "endSeconds": duration}
        frame_count = max(1, round(duration * fps))
        background = Image.open(background_path).convert("RGBA")
        foregrounds = [
            _decorate_registered_layer(
                _refine_legacy_registered_edge(Image.open(path).convert("RGBA"), background)
            )
            for path in foreground_paths
        ]
        layer_specs = scene.get("layers") if isinstance(scene.get("layers"), list) else []
        composition = scene.get("composition") if isinstance(scene.get("composition"), dict) else {}
        requested_placement = str(composition.get("textPlacement") or "top_left")
        scene["composition"] = {
            **composition,
            "textPlacement": requested_placement if composition.get("lockTextPlacement") else _choose_text_placement(background, foregrounds, layer_specs, requested_placement),
        }
        loaded.append({
            "scene": scene,
            "background": background,
            "foregrounds": foregrounds,
            "focus_targets": _layer_focus_targets(foregrounds, layer_specs),
            "voice_path": voice_path if voice_path.is_file() else None,
            "voice_duration": voice_duration,
            "frame_count": frame_count,
            "full_canvas_layers": bool(scene.get("fullCanvasLayers")),
        })
        total_frames += frame_count

    silent_path = work_dir / "reel-silent.mp4"
    command = [
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}", "-r", str(fps), "-i", "pipe:0", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(silent_path),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for loaded_scene in loaded:
            scene = loaded_scene["scene"]
            background = loaded_scene["background"]
            foregrounds = loaded_scene["foregrounds"]
            focus_targets = loaded_scene["focus_targets"]
            full_canvas_layers = loaded_scene["full_canvas_layers"]
            layer_specs = scene.get("layers") if isinstance(scene.get("layers"), list) else []
            frame_count = loaded_scene["frame_count"]
            for frame in range(frame_count):
                progress = frame / max(1, frame_count - 1)
                zoom, pan_x, pan_y = _director_camera_values(scene, progress, focus_targets)
                canvas = _cover(background, zoom, pan_x - 0.5, pan_y).convert("RGBA")
                canvas.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (1, 11, 20, 36)))
                for layer_index, foreground in enumerate(foregrounds):
                    if full_canvas_layers:
                        layer_spec = layer_specs[layer_index] if layer_index < len(layer_specs) else {}
                        layer_frame, _ = _full_canvas_layer_frame(
                            foreground,
                            layer_spec,
                            progress,
                            float(scene.get("durationSeconds") or 0),
                        )
                        if str(layer_spec.get("role") or "") != "evidence_graphic":
                            layer_frame = _cover_rgba(layer_frame, zoom, pan_x - 0.5, pan_y)
                        _composite_full_canvas_layer(canvas, layer_frame)
                    else:
                        layer = layer_specs[layer_index] if layer_index < len(layer_specs) else {}
                        size = str(layer.get("size") or "medium")
                        max_width, max_height = {
                            "large": (820, 1120),
                            "medium": (590, 780),
                            "small": (390, 520),
                        }.get(size, (590, 780))
                        base_scale = min(max_width / foreground.width, max_height / foreground.height)
                        width = round(foreground.width * base_scale)
                        height = round(foreground.height * base_scale)
                        x, y, pulse_scale, alpha = _layer_position(layer, layer_index, width, height, progress)
                        rotation = math.sin(progress * math.pi + layer_index * 1.3) * (0.32 if size == "large" else 0.8)
                        _composite_layer(canvas, foreground, x, y, base_scale * pulse_scale, alpha, rotation=rotation)
                _draw_kinetic_caption(canvas, scene, progress, accent)
                process.stdin.write(canvas.convert("RGB").tobytes())
    finally:
        if process.stdin:
            process.stdin.close()
    stderr = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
    if process.wait() != 0:
        raise RuntimeError(f"ffmpeg video render failed: {stderr[:1000]}")

    duration_seconds = round(total_frames / fps, 2)
    narration_file = Path(narration_path) if narration_path else None
    if narration_file and narration_file.is_file():
        narration_duration = _wav_duration(narration_file)
        voice_intervals = [(0.0, min(duration_seconds, narration_duration))]
    else:
        narration_file, voice_intervals = _build_continuous_narration(loaded, work_dir / "reel-narration.wav", fps)
    music_file = Path(music_path) if music_path else None
    if music_file and not music_file.is_file():
        music_file = None
    if narration_file or music_file:
        command = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent_path)]
        if narration_file:
            command.extend(["-i", str(narration_file)])
        if music_file:
            command.extend(["-stream_loop", "-1", "-i", str(music_file)])
        filters = [f"anullsrc=r=48000:cl=stereo:d={duration_seconds}[base]"]
        labels = ["[base]"]
        if narration_file:
            filters.append(f"[1:a]atrim=0:{duration_seconds:.3f},aresample=48000,aformat=channel_layouts=stereo[narration]")
            labels.append("[narration]")
        filters.append("".join(labels) + f"amix=inputs={len(labels)}:duration=first:normalize=0[voicebed]")
        if music_file:
            music_index = 2 if narration_file else 1
            fade_start = max(0.0, duration_seconds - 0.8)
            filters.append(
                f"[{music_index}:a]atrim=0:{duration_seconds},aresample=48000,aformat=channel_layouts=stereo,"
                f"volume='{_music_volume_expression(voice_intervals)}':eval=frame,"
                f"afade=t=in:st=0:d=0.3,afade=t=out:st={fade_start:.3f}:d=0.8[music]"
            )
            filters.append("[voicebed][music]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000[aout]")
        else:
            filters.append("[voicebed]loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000[aout]")
        command.extend(["-filter_complex", ";".join(filters), "-map", "0:v", "-map", "[aout]", "-t", str(duration_seconds), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(output_path)])
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise RuntimeError(f"ffmpeg audio mix failed: {completed.stderr[:1000]}")
    else:
        silent_path.replace(output_path)
    thumbnail_path = output_path.with_suffix(".jpg")
    completed = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1", "-i", str(output_path), "-frames:v", "1", "-q:v", "2", str(thumbnail_path)], capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"ffmpeg thumbnail render failed: {completed.stderr[:1000]}")
    return {
        "durationSeconds": duration_seconds,
        "fps": fps,
        "videoPath": str(output_path),
        "thumbnailPath": str(thumbnail_path),
        "musicApplied": bool(music_file),
        "musicMode": "continuous_ducked" if music_file else "none",
    }
