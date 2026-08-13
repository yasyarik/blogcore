#!/usr/bin/env python3
"""Layer-first vertical video renderer used by Blog Core Instagram Reels."""

from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageStat


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


FULL_CANVAS_REVEALS = ("slide_left", "slide_right", "drop", "rise", "focus")


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
    if not 0 <= start < end <= 0.38:
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


def _composite_full_canvas_layer(base: Image.Image, layer: Image.Image):
    """Composite a registered full-frame layer and derive shadows without cropping it."""
    alpha = layer.getchannel("A")
    shadow_alpha = alpha.filter(ImageFilter.GaussianBlur(24)).point(lambda value: round(value * 0.32))
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    shadow.putalpha(shadow_alpha)
    shifted_shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    shifted_shadow.alpha_composite(shadow, (18, 28))
    base.alpha_composite(shifted_shadow)
    base.alpha_composite(layer)


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
    amount = _ease(amount)
    return tuple(first[index] + (second[index] - first[index]) * amount for index in range(3))


def _layer_focus_targets(foregrounds: list[Image.Image], layer_specs: list[dict]):
    targets = []
    for index, foreground in enumerate(foregrounds):
        spec = layer_specs[index] if index < len(layer_specs) else {}
        if str(spec.get("role") or "") == "story_object":
            continue
        fitted = ImageOps.fit(foreground.convert("RGBA"), (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
        bbox = fitted.getchannel("A").getbbox()
        if not bbox:
            continue
        center_x = ((bbox[0] + bbox[2]) / 2) / WIDTH
        # Faces and expressive upper bodies normally occupy the upper third of a
        # complete person/group silhouette. Keep enough context to avoid a harsh crop.
        focus_y = (bbox[1] + (bbox[3] - bbox[1]) * 0.30) / HEIGHT
        targets.append((1.30, min(0.88, max(0.12, center_x)), min(0.28, max(-0.28, focus_y - 0.5))))
    return targets


def _subject_camera_values(kind: str, progress: float, targets, scene_index: int):
    base = _camera_values(kind, 0.0)
    if progress <= 0.46 or not targets:
        return base
    first = targets[0]
    if progress < 0.62:
        return _mix_camera(base, first, (progress - 0.46) / 0.16)
    if progress < 0.70:
        return first
    if len(targets) > 1:
        neutral = _camera_values(kind, 0.45)
        if progress < 0.82:
            return _mix_camera(first, neutral, (progress - 0.70) / 0.12)
        second = targets[1]
        if progress < 0.94:
            return _mix_camera(neutral, second, (progress - 0.82) / 0.12)
        return second
    end = _camera_values(kind, 1.0)
    return _mix_camera(first, end, (progress - 0.70) / 0.30)


def _choose_text_placement(background: Image.Image, foregrounds: list[Image.Image], requested: str) -> str:
    assembled = ImageOps.fit(background.convert("RGBA"), (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    occupied = Image.new("L", (WIDTH, HEIGHT), 0)
    for foreground in foregrounds:
        fitted = ImageOps.fit(foreground.convert("RGBA"), (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
        occupied = ImageChops.lighter(occupied, fitted.getchannel("A"))
        assembled.alpha_composite(fitted)
    candidates = {
        "top_left": (45, 70, 660, 560),
        "top_right": (420, 70, 1035, 560),
        "lower_left": (45, 1070, 660, 1570),
        "lower_right": (420, 1070, 1035, 1570),
    }
    grayscale = assembled.convert("L")
    edges = grayscale.filter(ImageFilter.FIND_EDGES)
    scored = []
    for name, box in candidates.items():
        occupancy = ImageStat.Stat(occupied.crop(box)).mean[0] / 255.0
        texture = ImageStat.Stat(grayscale.crop(box)).stddev[0]
        edge = ImageStat.Stat(edges.crop(box)).mean[0]
        lower_penalty = 9.0 if name.startswith("lower") else 0.0
        preference_bonus = -4.0 if name == requested else 0.0
        scored.append((occupancy * 900.0 + texture + edge * 0.7 + lower_penalty + preference_bonus, name))
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
    return lines[:3]


def _text_position(placement: str, text_width: int, line_width: int) -> int:
    if placement.endswith("right"):
        return WIDTH - 66 - line_width
    return 66


def _draw_kinetic_caption(canvas: Image.Image, scene: dict, progress: float, accent: tuple[int, int, int]):
    """Reveal the actual hook word-by-word without a card or generic dashboard UI."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    composition = scene.get("composition") if isinstance(scene.get("composition"), dict) else {}
    placement = str(composition.get("textPlacement") or "top_left")
    text_fill, text_stroke = _caption_palette(canvas, placement)
    hook_font = _font(96, bold=True)
    supporting_font = _font(34)
    hook = str(scene.get("overlayText") or scene.get("title") or "").strip()
    supporting = str(scene.get("supportingText") or "").strip()
    lines = _wrap_words(draw, hook, hook_font, WIDTH - 132)
    if not lines:
        return
    top = 122 if placement.startswith("top") else 1140
    word_index = 0
    for line_index, line in enumerate(lines):
        line_text = " ".join(line)
        line_width = draw.textbbox((0, 0), line_text, font=hook_font)[2]
        x = _text_position(placement, WIDTH, line_width)
        y = top + line_index * 106
        for word in line:
            reveal = _ease((progress - 0.05 - word_index * 0.055) / 0.17)
            if reveal > 0:
                word_width = draw.textbbox((0, 0), word, font=hook_font)[2]
                alpha = round(255 * reveal)
                draw.text(
                    (x, y + round((1 - reveal) * 26)),
                    word,
                    font=hook_font,
                    fill=(*text_fill, alpha),
                    stroke_width=3,
                    stroke_fill=(*text_stroke, round(225 * reveal)),
                )
                x += word_width + draw.textbbox((0, 0), " ", font=hook_font)[2]
            word_index += 1
    final_reveal = _ease((progress - 0.12) / 0.42)
    underline_width = round(min(WIDTH - 132, 190 + len(hook) * 10) * final_reveal)
    line_y = top + len(lines) * 106 + 12
    anchor_x = WIDTH - 66 - underline_width if placement.endswith("right") else 66
    draw.rounded_rectangle((anchor_x, line_y, anchor_x + underline_width, line_y + 7), radius=4, fill=(*accent, round(235 * final_reveal)))
    if supporting and final_reveal > 0:
        max_width = WIDTH - 132
        support_lines = _wrap_words(draw, supporting, supporting_font, max_width)[:2]
        support_y = line_y + 28 + round((1 - final_reveal) * 12)
        for line in support_lines:
            line_text = " ".join(line)
            line_width = draw.textbbox((0, 0), line_text, font=supporting_font)[2]
            support_x = _text_position(placement, WIDTH, line_width)
            draw.text(
                (support_x, support_y),
                line_text,
                font=supporting_font,
                fill=(*text_fill, round(235 * final_reveal)),
                stroke_width=2,
                stroke_fill=(*text_stroke, round(210 * final_reveal)),
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
        # Scene timing follows its own voice, so one Gemini TTS segment cannot overlap the next one.
        duration = max(3.5, planned_duration, voice_duration + 0.55)
        frame_count = max(1, round(duration * fps))
        background = Image.open(background_path).convert("RGBA")
        foregrounds = [Image.open(path).convert("RGBA") for path in foreground_paths]
        layer_specs = scene.get("layers") if isinstance(scene.get("layers"), list) else []
        composition = scene.get("composition") if isinstance(scene.get("composition"), dict) else {}
        scene["composition"] = {
            **composition,
            "textPlacement": _choose_text_placement(background, foregrounds, str(composition.get("textPlacement") or "top_left")),
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
                zoom, pan_x, pan_y = _subject_camera_values(
                    str(scene.get("cameraMove") or "dolly_in"),
                    progress,
                    focus_targets,
                    int(scene.get("index") or 1),
                )
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
    audio_inputs = []
    offset_seconds = 0.0
    for loaded_scene in loaded:
        voice_path = loaded_scene["voice_path"]
        if voice_path and loaded_scene["voice_duration"] > 0:
            audio_inputs.append((voice_path, round(offset_seconds * 1000), loaded_scene["voice_duration"]))
        offset_seconds += loaded_scene["frame_count"] / fps
    music_file = Path(music_path) if music_path else None
    if music_file and not music_file.is_file():
        music_file = None
    voice_intervals = [(delay_ms / 1000.0, min(duration_seconds, delay_ms / 1000.0 + clip_duration)) for _, delay_ms, clip_duration in audio_inputs]
    if audio_inputs or music_file:
        command = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent_path)]
        for path, _, _ in audio_inputs:
            command.extend(["-i", str(path)])
        if music_file:
            command.extend(["-stream_loop", "-1", "-i", str(music_file)])
        filters = [f"anullsrc=r=48000:cl=stereo:d={duration_seconds}[base]"]
        labels = ["[base]"]
        for index, (_, delay_ms, clip_duration) in enumerate(audio_inputs, start=1):
            filters.append(f"[{index}:a]atrim=0:{clip_duration:.3f},adelay={delay_ms}:all=1,aresample=48000,aformat=channel_layouts=stereo[a{index}]")
            labels.append(f"[a{index}]")
        filters.append("".join(labels) + f"amix=inputs={len(labels)}:duration=first:normalize=0[voicebed]")
        if music_file:
            music_index = len(audio_inputs) + 1
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
