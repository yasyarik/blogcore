#!/usr/bin/env python3
"""Master-derived, spatially registered scene layers for vertical storyboards."""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


WIDTH = 1080
HEIGHT = 1920
FPS = 24
_SAM2_PREDICTOR = None
_VITMATTE_PROCESSOR = None
_VITMATTE_MODEL = None
_RUNTIME_DEVICE = None


def _ease(value: float) -> float:
    value = min(1.0, max(0.0, value))
    return 1.0 - (1.0 - value) ** 3


def _runtime_device():
    global _RUNTIME_DEVICE
    if _RUNTIME_DEVICE is None:
        import torch

        if torch.cuda.is_available():
            _RUNTIME_DEVICE = torch.device("cuda")
        elif torch.backends.mps.is_available():
            _RUNTIME_DEVICE = torch.device("mps")
        else:
            _RUNTIME_DEVICE = torch.device("cpu")
    return _RUNTIME_DEVICE


def _sam2_predictor():
    """Load the production SAM 2.1 model; never silently fall back to quantized SAM."""
    global _SAM2_PREDICTOR
    if _SAM2_PREDICTOR is None:
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor

        checkpoint = Path(
            os.getenv("SAM2_CHECKPOINT")
            or Path(__file__).resolve().parent / "models" / "sam2.1_hiera_large.pt"
        )
        if not checkpoint.exists():
            raise FileNotFoundError(
                f"SAM 2.1 checkpoint is required for production layer extraction: {checkpoint}"
            )
        config = os.getenv("SAM2_CONFIG", "configs/sam2.1/sam2.1_hiera_l.yaml")
        model = build_sam2(
            config,
            str(checkpoint),
            device=_runtime_device(),
            apply_postprocessing=False,
        )
        _SAM2_PREDICTOR = SAM2ImagePredictor(model)
    return _SAM2_PREDICTOR


def _vitmatte():
    global _VITMATTE_PROCESSOR, _VITMATTE_MODEL
    if _VITMATTE_MODEL is None:
        from transformers import VitMatteForImageMatting, VitMatteImageProcessor

        model_id = os.getenv("VITMATTE_MODEL", "hustvl/vitmatte-small-composition-1k")
        _VITMATTE_PROCESSOR = VitMatteImageProcessor.from_pretrained(model_id)
        _VITMATTE_MODEL = (
            VitMatteForImageMatting.from_pretrained(model_id).to(_runtime_device()).eval()
        )
    return _VITMATTE_PROCESSOR, _VITMATTE_MODEL


def _pixel_box(raw_box, width: int, height: int) -> tuple[int, int, int, int]:
    if not isinstance(raw_box, (list, tuple)) or len(raw_box) != 4:
        raise ValueError("Each registered layer needs a four-value normalized bounding box")
    values = [float(value) for value in raw_box]
    if min(values) < 0 or max(values) > 1000 or values[2] <= values[0] or values[3] <= values[1]:
        raise ValueError("Registered layer bounding boxes use ordered 0..1000 coordinates")
    left = max(0, min(width - 2, round(values[0] * width / 1000)))
    top = max(0, min(height - 2, round(values[1] * height / 1000)))
    right = max(left + 1, min(width, round(values[2] * width / 1000)))
    bottom = max(top + 1, min(height, round(values[3] * height / 1000)))
    return left, top, right, bottom


def _box_intersection(first, second) -> int:
    left = max(first[0], second[0])
    top = max(first[1], second[1])
    right = min(first[2], second[2])
    bottom = min(first[3], second[3])
    return max(0, right - left) * max(0, bottom - top)


def _component_mask(mask: np.ndarray, minimum_area: int) -> np.ndarray:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    if count <= 1:
        return mask.astype(bool)
    areas = stats[1:, cv2.CC_STAT_AREA]
    largest = int(areas.max(initial=0))
    keep = np.zeros(mask.shape, dtype=np.uint8)
    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area >= max(minimum_area, round(largest * 0.08)):
            keep[labels == label] = 1
    return keep.astype(bool)


def _fill_small_holes(mask: np.ndarray, maximum_area: int) -> np.ndarray:
    """Repair enclosed segmentation holes without swallowing open background regions."""
    inverse = (~mask.astype(bool)).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(inverse, 8)
    repaired = mask.astype(np.uint8).copy()
    height, width = mask.shape
    for label in range(1, count):
        left = int(stats[label, cv2.CC_STAT_LEFT])
        top = int(stats[label, cv2.CC_STAT_TOP])
        component_width = int(stats[label, cv2.CC_STAT_WIDTH])
        component_height = int(stats[label, cv2.CC_STAT_HEIGHT])
        area = int(stats[label, cv2.CC_STAT_AREA])
        touches_edge = left == 0 or top == 0 or left + component_width >= width or top + component_height >= height
        if not touches_edge and area <= maximum_area:
            repaired[labels == label] = 1
    return repaired.astype(bool)


def _vitmatte_alpha(master: Image.Image, mask: np.ndarray) -> np.ndarray:
    """Turn a semantic SAM mask into a hair/clothing-quality alpha matte."""
    import torch

    binary = mask.astype(np.uint8) * 255
    kernel_size = max(7, round(min(mask.shape) * 0.010))
    if kernel_size % 2 == 0:
        kernel_size += 1
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    certain_foreground = cv2.erode(binary, kernel, iterations=1)
    possible_foreground = cv2.dilate(binary, kernel, iterations=1)
    trimap = np.zeros_like(binary)
    trimap[possible_foreground > 0] = 128
    trimap[certain_foreground > 0] = 255
    processor, model = _vitmatte()
    inputs = processor(
        images=master.convert("RGB"),
        trimaps=Image.fromarray(trimap, "L"),
        return_tensors="pt",
    )
    inputs = {key: value.to(_runtime_device()) for key, value in inputs.items()}
    with torch.inference_mode():
        alpha = model(**inputs).alphas[0, 0].detach().float().cpu().numpy()
    alpha = cv2.resize(alpha, master.size, interpolation=cv2.INTER_CUBIC)
    alpha = np.clip(alpha, 0.0, 1.0)
    alpha[(mask == 0) & (alpha < 0.35)] = 0.0
    return np.round(alpha * 255.0).astype(np.uint8)


def _decontaminated_layer(master: Image.Image, clean: Image.Image, alpha_u8: np.ndarray) -> np.ndarray:
    """Recover foreground edge colour without eroding or replacing matte pixels."""
    alpha = alpha_u8.astype(np.float32) / 255.0
    master_rgb = np.asarray(master.convert("RGB"), dtype=np.float32)
    clean_rgb = np.asarray(clean.convert("RGB"), dtype=np.float32)
    safe_alpha = np.maximum(alpha[..., None], 0.08)
    foreground = (master_rgb - (1.0 - alpha[..., None]) * clean_rgb) / safe_alpha
    foreground = np.clip(foreground, 0, 255).astype(np.uint8)
    foreground[alpha_u8 == 0] = 0
    layer = np.zeros((*alpha_u8.shape, 4), dtype=np.uint8)
    layer[..., :3] = foreground
    layer[..., 3] = alpha_u8
    return layer


def refine_registered_layer_file(
    layer_path: str | Path,
    clean_path: str | Path,
    master_path: str | Path | None = None,
    role: str = "story_object",
) -> None:
    """Upgrade an existing binary registered layer to the current clean-edge matte."""
    layer_path = Path(layer_path)
    layer = Image.open(layer_path).convert("RGBA")
    clean = Image.open(clean_path).convert("RGB")
    if clean.size != layer.size:
        clean = ImageOps.fit(clean, layer.size, method=Image.Resampling.LANCZOS)
    mask = np.asarray(layer.getchannel("A")) > 0
    master = Image.open(master_path).convert("RGB") if master_path else Image.fromarray(np.asarray(layer)[..., :3], "RGB")
    if master.size != layer.size:
        master = ImageOps.fit(master, layer.size, method=Image.Resampling.LANCZOS)
    alpha = _vitmatte_alpha(master, mask)
    Image.fromarray(_decontaminated_layer(master, clean, alpha), "RGBA").save(layer_path)


def _segment_registered_layer(predictor, master: Image.Image, box, role: str) -> np.ndarray:
    width, height = master.size
    left, top, right, bottom = box
    masks, scores, _ = predictor.predict(
        box=np.asarray([[left, top, right, bottom]], dtype=np.float32),
        multimask_output=True,
    )
    mask = masks[int(np.argmax(scores))].astype(bool)
    allowed = np.zeros((height, width), dtype=bool)
    padding = max(4, round(min(width, height) * 0.012))
    allowed[max(0, top - padding):min(height, bottom + padding), max(0, left - padding):min(width, right + padding)] = True
    mask &= allowed
    mask = _component_mask(mask, max(48, round(width * height * 0.00025)))
    kernel_size = 5 if role in {"protagonist", "supporting_character"} else 3
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel).astype(bool)
    return _fill_small_holes(mask, max(1100, round(mask.size * 0.0018)))


def _mask_box(mask: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.where(mask)
    if not len(xs):
        return 0, 0, 0, 0
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def build_registered_scene_pack(
    clean_path: str | Path | list[str | Path] | tuple[str | Path, ...],
    master_path: str | Path,
    layer_specs: list[dict],
    output_dir: str | Path,
) -> dict:
    """Derive non-overlapping full-canvas layers from one integrated master frame."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    master = Image.open(master_path).convert("RGB")
    clean_paths = list(clean_path) if isinstance(clean_path, (list, tuple)) else [clean_path]
    clean_candidates = []
    for candidate_path in clean_paths:
        candidate = Image.open(candidate_path).convert("RGB")
        if candidate.size != master.size:
            candidate = ImageOps.fit(candidate, master.size, method=Image.Resampling.LANCZOS)
        clean_candidates.append(candidate)
    clean = clean_candidates[0]
    width, height = master.size
    if len(layer_specs) < 1 or len(layer_specs) > 4:
        raise ValueError("A registered scene needs one to four visually valid master-derived layers")

    # Detector boxes are deliberately conservative and may overlap around clear
    # neighboring silhouettes. Pixel masks below are the authoritative separation
    # check, so boxes are prompts only and never a rejection signal by themselves.
    boxes = [_pixel_box(spec.get("bbox"), width, height) for spec in layer_specs]

    predictor = _sam2_predictor()
    predictor.set_image(np.asarray(master))
    masks = []
    alphas = []
    manifest_layers = []
    for index, (spec, box) in enumerate(zip(layer_specs, boxes), start=1):
        role = str(spec.get("role") or "story_object")
        mask = _segment_registered_layer(predictor, master, box, role)
        area_ratio = float(mask.mean())
        actual_box = _mask_box(mask)
        height_ratio = (actual_box[3] - actual_box[1]) / height if actual_box[3] > actual_box[1] else 0.0
        if role in {"protagonist", "supporting_character"}:
            minimum_height = 0.34 if role == "protagonist" else 0.22
            minimum_area = 0.035 if role == "protagonist" else 0.015
            if height_ratio < minimum_height or area_ratio < minimum_area:
                raise ValueError(
                    f"Registered person layer {index} is too small for mobile viewing "
                    f"(height={height_ratio:.3f}, area={area_ratio:.3f})"
                )
        elif area_ratio < 0.012 and not (height_ratio >= 0.22 and area_ratio >= 0.003):
            raise ValueError(f"Registered layer {index} is too small to carry visual meaning")
        for prior in masks:
            overlap = np.logical_and(mask, prior).sum()
            smaller_area = min(mask.sum(), prior.sum())
            overlap_ratio = overlap / smaller_area if smaller_area else 0.0
            if overlap_ratio > 0.05:
                raise ValueError("Registered masks materially overlap; every animated element must remain a separate part of the master frame")
            if overlap:
                # The visual review has already confirmed clear silhouettes. Tiny
                # boundary overlap here is SAM leakage, so assign it to the earlier
                # primary group instead of rejecting or regenerating a valid master.
                mask &= ~prior
        masks.append(mask)

        alpha = _vitmatte_alpha(master, mask)
        alphas.append(alpha)
        layer_array = _decontaminated_layer(master, clean, alpha)
        filename = f"layer-{index:02d}-{str(spec.get('id') or index)}.png"
        Image.fromarray(layer_array, "RGBA").save(output_dir / filename)
        manifest_layers.append({
            **spec,
            "filename": filename,
            "pixelBox": list(actual_box),
            "areaRatio": round(area_ratio, 5),
            "heightRatio": round(height_ratio, 5),
            "canvas": [width, height],
        })

    union = np.logical_or.reduce(masks)
    master_array = np.asarray(master).copy()
    base_array = master_array.copy()
    candidate_arrays = [np.asarray(candidate) for candidate in clean_candidates]
    selected_base_indices = []
    for mask, layer in zip(masks, manifest_layers):
        ring = cv2.dilate(mask.astype(np.uint8), np.ones((25, 25), dtype=np.uint8)).astype(bool) & ~mask
        choices = []
        for index, candidate_array in enumerate(candidate_arrays):
            delta = np.mean(np.abs(master_array.astype(np.int16) - candidate_array.astype(np.int16)), axis=2)
            inner_delta = float(delta[mask].mean()) if mask.any() else 0.0
            ring_delta = float(delta[ring].mean()) if ring.any() else 0.0
            choices.append({
                "index": index,
                "innerDelta": inner_delta,
                "ringDelta": ring_delta,
                "score": inner_delta - 1.5 * ring_delta,
            })
        choice = max(choices, key=lambda item: item["score"])
        if choice["innerDelta"] < 8.0:
            raise ValueError(
                f"No clean plate actually removes registered component {layer['id']} "
                f"(inner={choice['innerDelta']:.3f}, ring={choice['ringDelta']:.3f}, score={choice['score']:.3f})"
            )
        selected_base_indices.append(int(choice["index"]))
        layer["baseSourceIndex"] = int(choice["index"])
        layer["baseInnerDelta"] = round(choice["innerDelta"], 3)
        layer["baseRingDelta"] = round(choice["ringDelta"], 3)
    # A removal edit is one coherent photograph. Use the most consistently selected
    # empty plate as the complete base instead of cutting independently recolored
    # patches into the master, which would introduce visible seams during reveals.
    base_source_index = max(set(selected_base_indices), key=selected_base_indices.count)
    base_array = candidate_arrays[base_source_index].copy()
    base_source = clean_candidates[base_source_index]
    for index, (alpha, layer) in enumerate(zip(alphas, manifest_layers), start=1):
        Image.fromarray(_decontaminated_layer(master, base_source, alpha), "RGBA").save(output_dir / layer["filename"])
    base = Image.fromarray(base_array, "RGB").convert("RGBA")
    base_filename = "registered-base.png"
    base.save(output_dir / base_filename)

    reconstructed = base.copy()
    for layer in manifest_layers:
        reconstructed = Image.alpha_composite(reconstructed, Image.open(output_dir / layer["filename"]).convert("RGBA"))
    reconstruction_filename = "registered-reconstruction.png"
    reconstructed.convert("RGB").save(output_dir / reconstruction_filename)
    master_array_float = np.asarray(master, dtype=np.float32)
    reconstruction_array = np.asarray(reconstructed.convert("RGB"), dtype=np.float32)
    opaque_core = cv2.erode(union.astype(np.uint8), np.ones((9, 9), dtype=np.uint8)).astype(bool)
    mae = float(np.mean(np.abs(master_array_float[opaque_core] - reconstruction_array[opaque_core])))
    if mae > 0.5:
        raise ValueError(f"Registered layers do not reconstruct the master frame accurately (MAE {mae:.3f})")

    master_filename = "registered-master.jpg"
    clean_filename = "clean-reference.jpg"
    master.save(output_dir / master_filename, quality=94)
    clean.save(output_dir / clean_filename, quality=94)
    for index, candidate in enumerate(clean_candidates[1:], start=2):
        candidate.save(output_dir / f"clean-reference-{index}.jpg", quality=94)
    manifest = {
        "contract": "master-derived-full-canvas-v1",
        "matteContract": "sam2.1-large-vitmatte-decontaminated-v2",
        "canvas": [width, height],
        "cleanFilename": clean_filename,
        "masterFilename": master_filename,
        "baseFilename": base_filename,
        "reconstructionFilename": reconstruction_filename,
        "reconstructionMae": round(mae, 5),
        "coverageRatio": round(float(union.mean()), 5),
        "overlapPixels": 0,
        "layers": manifest_layers,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def _fit_registered(image: Image.Image) -> Image.Image:
    return ImageOps.fit(image.convert("RGBA"), (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)


def render_registered_scene_proof(pack_dir: str | Path, output_path: str | Path, duration: float = 10.0) -> dict:
    """Render a proof without changing layer coordinates, scale, or stacking order."""
    pack_dir = Path(pack_dir)
    output_path = Path(output_path)
    manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
    base = _fit_registered(Image.open(pack_dir / manifest["baseFilename"]))
    layers = [_fit_registered(Image.open(pack_dir / layer["filename"])) for layer in manifest["layers"]]
    frames = max(1, round(duration * FPS))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "pipe:0", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output_path),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for frame in range(frames):
            progress = frame / max(1, frames - 1)
            canvas = base.copy()
            for index, layer in enumerate(layers):
                reveal_start = 0.08 + index * (0.68 / max(1, len(layers)))
                reveal = _ease((progress - reveal_start) / 0.16)
                if reveal <= 0:
                    continue
                visible = layer.copy()
                alpha = np.asarray(visible.getchannel("A"), dtype=np.float32)
                alpha *= reveal
                visible.putalpha(Image.fromarray(np.clip(alpha, 0, 255).astype(np.uint8), "L"))
                canvas = Image.alpha_composite(canvas, visible)
            zoom = 1.0 + 0.025 * _ease(progress)
            scaled = canvas.resize((round(WIDTH * zoom), round(HEIGHT * zoom)), Image.Resampling.LANCZOS)
            left = max(0, (scaled.width - WIDTH) // 2)
            top = max(0, (scaled.height - HEIGHT) // 2)
            frame_image = scaled.crop((left, top, left + WIDTH, top + HEIGHT))
            process.stdin.write(frame_image.convert("RGB").tobytes())
    finally:
        if process.stdin:
            process.stdin.close()
    stderr = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
    if process.wait() != 0:
        raise RuntimeError(f"Registered scene proof render failed: {stderr[:1000]}")
    return {"videoPath": str(output_path), "durationSeconds": duration, "fps": FPS, "layers": len(layers)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a master-derived registered-scene proof")
    parser.add_argument("--clean", required=True)
    parser.add_argument("--removal", required=True)
    parser.add_argument("--master", required=True)
    parser.add_argument("--specs", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--video")
    args = parser.parse_args()
    specs = json.loads(Path(args.specs).read_text(encoding="utf-8"))
    pack = build_registered_scene_pack([args.clean, args.removal], args.master, specs, args.output_dir)
    render = render_registered_scene_proof(args.output_dir, args.video) if args.video else None
    print(json.dumps({"pack": pack, "render": render}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
