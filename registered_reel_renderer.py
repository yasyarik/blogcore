#!/usr/bin/env python3
"""Render a production Reel from master-derived registered scene packs."""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from reel_renderer import (
    FPS,
    HEIGHT,
    WIDTH,
    _camera_values,
    _cover,
    _draw_kinetic_caption,
    _ease,
    _music_volume_expression,
    _wav_duration,
)


def _reveal_layer(layer: Image.Image, progress: float, mode: str) -> Image.Image:
    progress = _ease(progress)
    source = layer.convert("RGBA")
    alpha = np.asarray(source.getchannel("A"), dtype=np.float32)
    height, width = alpha.shape
    if mode == "wipe_right":
        edge = progress * (width + 120) - 60
        ramp = np.clip((edge - np.arange(width) + 40) / 80, 0, 1)
        alpha *= ramp[None, :]
    elif mode == "wipe_up":
        edge = height - progress * (height + 140) + 70
        ramp = np.clip((np.arange(height) - edge + 45) / 90, 0, 1)
        alpha *= ramp[:, None]
    elif mode == "radial":
        yy, xx = np.ogrid[:height, :width]
        radius = math.hypot(width, height) * progress
        distance = np.sqrt((xx - width * 0.5) ** 2 + (yy - height * 0.5) ** 2)
        alpha *= np.clip((radius - distance + 70) / 140, 0, 1)
    elif mode == "focus":
        source = source.filter(ImageFilter.GaussianBlur(max(0.0, (1.0 - progress) * 18.0)))
        alpha *= progress
    elif mode == "light_sweep":
        alpha *= progress
        if progress < 0.92:
            glow = Image.new("RGBA", source.size, (255, 238, 190, 0))
            glow_alpha = np.zeros((height, width), dtype=np.uint8)
            center = progress * (width + 260) - 130
            stripe = np.clip(1.0 - np.abs(np.arange(width) - center) / 120.0, 0, 1)
            glow_alpha[:] = (stripe[None, :] * 72).astype(np.uint8)
            glow.putalpha(Image.fromarray(glow_alpha))
            source = Image.alpha_composite(source, glow)
    else:
        alpha *= progress
    source.putalpha(Image.fromarray(np.clip(alpha, 0, 255).astype(np.uint8)))
    return source


def _mix_audio(silent_path: Path, scenes: list[dict], duration: float, output_path: Path, music_path: Path | None):
    inputs = []
    offset = 0.0
    for scene in scenes:
        voice = Path(str(scene.get("voicePath") or ""))
        voice_duration = _wav_duration(voice) if voice.is_file() else 0.0
        if voice_duration:
            inputs.append((voice, round(offset * 1000), voice_duration))
        offset += float(scene["renderDuration"])
    if music_path and not music_path.is_file():
        music_path = None
    command = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent_path)]
    for path, _, _ in inputs:
        command.extend(["-i", str(path)])
    if music_path:
        command.extend(["-stream_loop", "-1", "-i", str(music_path)])
    filters = [f"anullsrc=r=48000:cl=stereo:d={duration}[base]"]
    labels = ["[base]"]
    intervals = []
    for index, (_, delay_ms, clip_duration) in enumerate(inputs, start=1):
        filters.append(f"[{index}:a]atrim=0:{clip_duration:.3f},adelay={delay_ms}:all=1,aresample=48000,aformat=channel_layouts=stereo[a{index}]")
        labels.append(f"[a{index}]")
        intervals.append((delay_ms / 1000.0, min(duration, delay_ms / 1000.0 + clip_duration)))
    filters.append("".join(labels) + f"amix=inputs={len(labels)}:duration=first:normalize=0[voicebed]")
    if music_path:
        music_index = len(inputs) + 1
        fade_start = max(0.0, duration - 0.8)
        filters.append(
            f"[{music_index}:a]atrim=0:{duration},aresample=48000,aformat=channel_layouts=stereo,"
            f"volume='{_music_volume_expression(intervals)}':eval=frame,"
            f"afade=t=in:st=0:d=0.3,afade=t=out:st={fade_start:.3f}:d=0.8[music]"
        )
        filters.append("[voicebed][music]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000[aout]")
    else:
        filters.append("[voicebed]loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000[aout]")
    command.extend(["-filter_complex", ";".join(filters), "-map", "0:v", "-map", "[aout]", "-t", str(duration), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(output_path)])
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(f"Registered Reel audio mix failed: {completed.stderr[:1000]}")


def render_registered_reel(stages: dict[int, dict], scenes: list[dict], output_path: str | Path, work_dir: str | Path, accent_hex: str, music_path: str | Path | None = None) -> dict:
    output_path = Path(output_path)
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        accent_hex = accent_hex.lstrip("#")
        accent = tuple(int(accent_hex[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        accent = (54, 214, 198)
    loaded_stages = {}
    for stage_id, stage in stages.items():
        root = Path(stage["path"])
        manifest = stage["manifest"]
        loaded_stages[int(stage_id)] = {
            "base": Image.open(root / manifest["baseFilename"]).convert("RGBA"),
            "layers": [Image.open(root / item["filename"]).convert("RGBA") for item in manifest["layers"]],
        }
    total_frames = 0
    for scene in scenes:
        voice = Path(str(scene.get("voicePath") or ""))
        voice_duration = _wav_duration(voice) if voice.is_file() else 0.0
        scene["renderDuration"] = max(3.5, float(scene.get("durationSeconds") or 4.0), voice_duration + 0.55)
        scene["frameCount"] = max(1, round(scene["renderDuration"] * FPS))
        total_frames += scene["frameCount"]
    silent_path = work_dir / "registered-reel-silent.mp4"
    command = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "pipe:0", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(silent_path)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    previous_visible = {}
    try:
        for scene in scenes:
            stage_id = int(scene["stageId"])
            stage = loaded_stages[stage_id]
            previous = previous_visible.get(stage_id, 0)
            visible_count = int(scene.get("visibleLayerCount") or len(stage["layers"]))
            appearances = scene.get("appearances") or ["fade"]
            for frame in range(scene["frameCount"]):
                progress = frame / max(1, scene["frameCount"] - 1)
                composition = stage["base"].copy()
                for index, layer in enumerate(stage["layers"][:visible_count]):
                    if index < previous:
                        visible = layer
                    else:
                        reveal_progress = (progress - 0.04 - (index - previous) * 0.12) / 0.42
                        visible = _reveal_layer(layer, reveal_progress, appearances[(index - previous) % len(appearances)])
                    composition = Image.alpha_composite(composition, visible)
                zoom, pan_x, pan_y = _camera_values(str(scene.get("cameraMove") or "dolly_in"), progress)
                canvas = _cover(composition.convert("RGB"), zoom, pan_x - 0.5, pan_y).convert("RGBA")
                _draw_kinetic_caption(canvas, scene, progress, accent)
                process.stdin.write(canvas.convert("RGB").tobytes())
            previous_visible[stage_id] = visible_count
    finally:
        if process.stdin:
            process.stdin.close()
    stderr = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
    if process.wait():
        raise RuntimeError(f"Registered Reel video render failed: {stderr[:1000]}")
    duration = round(total_frames / FPS, 2)
    _mix_audio(silent_path, scenes, duration, output_path, Path(music_path) if music_path else None)
    thumbnail = output_path.with_suffix(".jpg")
    completed = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1", "-i", str(output_path), "-frames:v", "1", "-q:v", "2", str(thumbnail)], capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(f"Registered Reel cover render failed: {completed.stderr[:1000]}")
    return {"durationSeconds": duration, "fps": FPS, "videoPath": str(output_path), "thumbnailPath": str(thumbnail), "musicApplied": bool(music_path), "musicMode": "continuous_ducked" if music_path else "none"}
