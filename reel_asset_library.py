from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageStat


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
REUSABLE_TYPES = {"scene_background", "registered_layer", "clean_plate", "master_frame"}
REFERENCE_TYPES = {"scene_background", "registered_layer", "clean_plate", "master_frame", "source_reference"}
TYPE_PRIORITY = {
    "scene_background": 5,
    "master_frame": 4,
    "source_reference": 3,
    "clean_plate": 2,
    "registered_layer": 1,
}
TOKEN_STOPWORDS = {
    "about", "after", "again", "against", "along", "also", "and", "are", "around", "before",
    "behind", "between", "both", "complete", "from", "into", "near", "only", "scene", "show",
    "that", "the", "their", "them", "then", "this", "through", "toward", "vertical", "visible",
    "with", "without", "within",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _average_hash(image: Image.Image, size: int = 16) -> str:
    gray = ImageOps.fit(image.convert("L"), (size, size), method=Image.Resampling.LANCZOS)
    values = list(gray.getdata())
    mean = sum(values) / max(1, len(values))
    bits = "".join("1" if value >= mean else "0" for value in values)
    return f"{int(bits, 2):0{size * size // 4}x}"


def _hash_distance(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def _thumbnail_rmse(left: Image.Image, right: Image.Image, size=(64, 114)) -> float:
    first = ImageOps.fit(left.convert("RGB"), size, method=Image.Resampling.LANCZOS)
    second = ImageOps.fit(right.convert("RGB"), size, method=Image.Resampling.LANCZOS)
    histogram = ImageStat.Stat(ImageOps.grayscale(Image.blend(first, second, 0.5))).mean
    del histogram  # Keep Pillow's decoder warm before the pixel loop.
    first_values = list(first.getdata())
    second_values = list(second.getdata())
    squared = 0
    for a, b in zip(first_values, second_values):
        squared += sum((int(a[channel]) - int(b[channel])) ** 2 for channel in range(3))
    return math.sqrt(squared / max(1, len(first_values) * 3))


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]{3,}", str(value or "").lower())
        if token not in TOKEN_STOPWORDS
    }


def _semantic_similarity(left: str, right: str) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = len(left_tokens & right_tokens)
    return intersection / math.sqrt(len(left_tokens) * len(right_tokens))


def _canonical_rank(asset: dict) -> tuple:
    return (
        asset.get("status") == "approved",
        TYPE_PRIORITY.get(str(asset.get("type") or ""), 0),
        float(asset.get("qualityScore") or 0),
        asset.get("postStatus") == "PUBLISHED",
        str(asset.get("relativePath") or ""),
    )


def _asset_type(path: Path) -> str:
    name = path.name.lower()
    if re.fullmatch(r"scene-\d+-background\.png", name):
        return "scene_background"
    if "evidence-layer" in name:
        return "evidence_graphic"
    if re.search(r"(?:photo-layer|^layer-\d+|scene-\d+-layer-\d+)(?:-|\.)", name) and path.suffix.lower() == ".png":
        return "source_reference" if "-source" in name else "registered_layer"
    if name in {"registered-base.png", "clean.jpg", "clean-reference.jpg", "clean-reference-2.jpg"}:
        return "clean_plate"
    if name in {"master.jpg", "registered-master.jpg", "registered-master-source.jpg"}:
        return "master_frame"
    if "reconstruction" in name or "layer-review" in name or "contact_sheet" in name:
        return "diagnostic"
    if "source" in name or "reference" in name:
        return "source_reference"
    if re.fullmatch(r"slide-\d+\.(?:jpg|jpeg|png|webp)", name):
        return "carousel_slide"
    if name.startswith("instagram-reel"):
        return "reel_poster"
    return "supporting_image"


def _scene_index(path: Path) -> int | None:
    for part in (path.name, *reversed(path.parts)):
        match = re.search(r"scene-(\d+)", part, re.I)
        if match:
            return int(match.group(1))
        match = re.search(r"stage-(\d+)", part, re.I)
        if match:
            return int(match.group(1))
    return None


def _layer_ordinal(path: Path) -> int | None:
    name = path.name.lower()
    for pattern in (r"photo-layer-(\d+)", r"scene-\d+-layer-(\d+)", r"^layer-(\d+)"):
        match = re.search(pattern, name)
        if match:
            return int(match.group(1))
    return None


def _asset_key(path: Path, source_root: Path) -> str:
    relative = path.relative_to(source_root)
    return relative.parts[0] if relative.parts else ""


def _image_metrics(path: Path) -> dict:
    with Image.open(path) as opened:
        image = opened.convert("RGBA")
        width, height = image.size
        alpha = image.getchannel("A")
        bbox = alpha.getbbox()
        alpha_extrema = alpha.getextrema()
        opaque = alpha_extrema == (255, 255)
        alpha_coverage = 1.0
        bbox_ratio = 1.0
        touches_edge = False
        semi_transparent_ratio = 0.0
        if not opaque and bbox:
            histogram = alpha.histogram()
            visible_pixels = sum(histogram[1:])
            alpha_coverage = visible_pixels / max(1, width * height)
            bbox_ratio = ((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])) / max(1, width * height)
            touches_edge = bbox[0] <= 1 or bbox[1] <= 1 or bbox[2] >= width - 1 or bbox[3] >= height - 1
            semi_transparent_ratio = sum(histogram[1:255]) / max(1, visible_pixels)
        gray = image.convert("L")
        edges = gray.filter(ImageFilter.FIND_EDGES)
        sharpness = float(ImageStat.Stat(edges).var[0])
        luminance = float(ImageStat.Stat(gray).mean[0])
        return {
            "width": width,
            "height": height,
            "aspectRatio": round(width / max(1, height), 6),
            "hasTransparency": not opaque,
            "alphaCoverage": round(alpha_coverage, 6),
            "alphaBoundingBoxRatio": round(bbox_ratio, 6),
            "alphaTouchesCanvasEdge": touches_edge,
            "semiTransparentVisibleRatio": round(semi_transparent_ratio, 6),
            "sharpness": round(sharpness, 3),
            "meanLuminance": round(luminance, 3),
            "perceptualHash": _average_hash(image),
        }


def _load_overrides(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _social_context(db_path: Path, site_id: int) -> dict:
    result = {}
    if not db_path.is_file():
        return result
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            "select id, job_id, status, content_json from social_posts where site_id=? and channel='instagram' and asset_type='instagram_reel'",
            (site_id,),
        ).fetchall()
    finally:
        connection.close()
    for row in rows:
        try:
            payload = json.loads(row["content_json"] or "{}")
        except json.JSONDecodeError:
            continue
        reel = payload.get("instagramReel") if isinstance(payload, dict) else None
        if not isinstance(reel, dict):
            continue
        key = str(reel.get("assetKey") or "")
        storyboard = reel.get("storyboard") if isinstance(reel.get("storyboard"), dict) else {}
        scenes = storyboard.get("scenes") if isinstance(storyboard.get("scenes"), list) else []
        scene_map = {}
        for scene in scenes:
            if not isinstance(scene, dict):
                continue
            index = int(scene.get("index") or 0)
            if not index:
                continue
            layers = [item for item in scene.get("layers") or [] if isinstance(item, dict)]
            semantic_parts = [
                scene.get("visualStory"), scene.get("stageBackgroundPrompt"), scene.get("productionBackgroundPrompt"),
                scene.get("shotFraming"), scene.get("overlayText"), scene.get("narration"),
                *[layer.get("prompt") for layer in layers], *[layer.get("action") for layer in layers],
            ]
            scene_map[index] = {
                "visualStory": str(scene.get("visualStory") or ""),
                "environment": str(scene.get("productionBackgroundPrompt") or scene.get("stageBackgroundPrompt") or ""),
                "overlayText": str(scene.get("overlayText") or ""),
                "layerRoles": [str(layer.get("role") or "") for layer in layers],
                "layerDescriptions": [str(layer.get("prompt") or "") for layer in layers],
                "semanticText": " ".join(str(item or "") for item in semantic_parts),
            }
        if key:
            result[key] = {
                "postId": int(row["id"]),
                "jobId": str(row["job_id"] or ""),
                "postStatus": str(row["status"] or ""),
                "ready": str((reel.get("progress") or {}).get("phase") or "") == "ready",
                "scenes": scene_map,
            }
    return result


def _manifest_evidence(source_root: Path) -> dict:
    evidence = {}
    for manifest_path in source_root.rglob("manifest.json"):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(manifest, dict) or not manifest.get("contract"):
            continue
        index = _scene_index(manifest_path)
        key = _asset_key(manifest_path, source_root)
        if not index:
            continue
        record = {
            "contract": str(manifest.get("contract") or ""),
            "reconstructionMae": float(manifest.get("reconstructionMae") or 1),
            "overlapPixels": int(manifest.get("overlapPixels") or 0),
            "coverageRatio": float(manifest.get("coverageRatio") or 0),
            "layers": manifest.get("layers") if isinstance(manifest.get("layers"), list) else [],
        }
        current = evidence.get((key, index))
        if current is None or record["reconstructionMae"] < current["reconstructionMae"]:
            evidence[(key, index)] = record
    return evidence


def _initial_status(asset: dict, scene_context: dict | None, manifest: dict | None) -> tuple[str, list[str], float]:
    kind = asset["type"]
    metrics = asset["metrics"]
    reasons = []
    score = 50.0
    if kind not in REFERENCE_TYPES:
        return "archive", ["not a reusable Reel scene or layer asset"], 0.0
    if metrics["width"] < 512 or metrics["height"] < 512:
        return "rejected", ["resolution below reusable production minimum"], 5.0
    score += min(18.0, metrics["sharpness"] / 16.0)
    if kind == "registered_layer":
        if not metrics["hasTransparency"]:
            return "rejected", ["registered layer has no transparent background"], 10.0
        coverage = metrics["alphaCoverage"]
        if coverage < 0.006:
            return "rejected", ["visible subject is too small for mobile reuse"], 10.0
        if coverage < 0.018:
            reasons.append("subject is small and needs manual review")
            score -= 18
        else:
            score += min(14.0, coverage * 150)
        if metrics["alphaTouchesCanvasEdge"]:
            reasons.append("subject touches the canvas edge")
            score -= 12
        if metrics["semiTransparentVisibleRatio"] > 0.42:
            reasons.append("large soft-alpha region may contain matte residue")
            score -= 8
    if kind in {"scene_background", "clean_plate", "master_frame"}:
        if not 0.50 <= metrics["aspectRatio"] <= 0.60:
            reasons.append("not a standard vertical Reel frame")
            score -= 18
        else:
            score += 8
        if not manifest and not (scene_context and scene_context.get("ready")):
            reasons.append("not linked to an accepted production manifest")
            score = min(score, 64)
    if manifest:
        if manifest["reconstructionMae"] <= 0.01 and manifest["overlapPixels"] == 0:
            score += 16
        else:
            reasons.append("registered scene reconstruction did not meet the preferred threshold")
            score -= 20
    if scene_context and scene_context.get("ready"):
        score += 10
    if kind == "source_reference":
        reasons.append("reference-only source; never composite directly")
        score = min(score, 64)
    status = "approved" if score >= 70 and not reasons else "review"
    if score < 35:
        status = "rejected"
    return status, reasons, round(max(0.0, min(100.0, score)), 2)


def build_reel_asset_catalog(source_root, library_root, site_id, db_path, write_links=True) -> dict:
    source_root = Path(source_root).resolve()
    library_root = Path(library_root).resolve()
    db_path = Path(db_path).resolve()
    site_id = int(site_id)
    site_library = library_root / str(site_id)
    site_library.mkdir(parents=True, exist_ok=True)
    overrides = _load_overrides(site_library / "overrides.json")
    context = _social_context(db_path, site_id)
    manifests = _manifest_evidence(source_root)
    assets = []
    for path in sorted(item for item in source_root.rglob("*") if item.is_file() and item.suffix.lower() in IMAGE_SUFFIXES):
        kind = _asset_type(path)
        key = _asset_key(path, source_root)
        index = _scene_index(path)
        source_context = context.get(key) or {}
        scene_context = (source_context.get("scenes") or {}).get(index) if index else None
        try:
            metrics = _image_metrics(path)
        except Exception as error:
            assets.append({
                "id": hashlib.sha1(str(path).encode()).hexdigest()[:16], "sourcePath": str(path),
                "relativePath": str(path.relative_to(source_root)), "type": kind, "status": "rejected",
                "reasons": [f"image cannot be decoded: {error}"], "qualityScore": 0,
            })
            continue
        asset = {
            "id": hashlib.sha1(str(path.relative_to(source_root)).encode()).hexdigest()[:16],
            "siteId": site_id,
            "sourcePath": str(path),
            "relativePath": str(path.relative_to(source_root)),
            "assetKey": key,
            "sceneIndex": index,
            "layerOrdinal": _layer_ordinal(path),
            "type": kind,
            "sha256": _sha256(path),
            "metrics": metrics,
            "context": scene_context or {},
            "postId": source_context.get("postId"),
            "jobId": source_context.get("jobId"),
            "postStatus": source_context.get("postStatus"),
            "reuseMode": "scene_bundle" if kind in {"scene_background", "clean_plate", "master_frame"} else "reference_only",
        }
        if kind == "registered_layer" and scene_context:
            ordinal = int(asset.get("layerOrdinal") or 0)
            roles = scene_context.get("layerRoles") or []
            descriptions = scene_context.get("layerDescriptions") or []
            if ordinal and ordinal <= len(roles):
                asset["layerRole"] = str(roles[ordinal - 1] or "")
            if ordinal and ordinal <= len(descriptions):
                asset["layerDescription"] = str(descriptions[ordinal - 1] or "")
        status, reasons, score = _initial_status(asset, source_context, manifests.get((key, index)))
        asset.update(status=status, reasons=reasons, qualityScore=score)
        manual = overrides.get(asset["relativePath"])
        if isinstance(manual, dict) and manual.get("status") in {"approved", "review", "rejected", "archive"}:
            asset["automaticStatus"] = asset["status"]
            asset["status"] = manual["status"]
            asset["manualNote"] = str(manual.get("note") or "")
        assets.append(asset)

    exact_groups = defaultdict(list)
    for asset in assets:
        if asset.get("sha256") and asset.get("status") in {"approved", "review"}:
            exact_groups[asset["sha256"]].append(asset)
    for group in exact_groups.values():
        if len(group) < 2:
            continue
        canonical = max(group, key=_canonical_rank)
        for duplicate in group:
            if duplicate is canonical:
                duplicate["duplicateCount"] = len(group) - 1
                continue
            duplicate["duplicateOf"] = canonical["id"]
            duplicate["status"] = "duplicate"
            duplicate["reasons"] = ["byte-identical duplicate"]

    candidates = [asset for asset in assets if asset.get("status") in {"approved", "review"} and asset["type"] in REFERENCE_TYPES]
    by_type = defaultdict(list)
    for asset in candidates:
        by_type[asset["type"]].append(asset)
    image_cache = {}
    for group in by_type.values():
        group.sort(key=_canonical_rank, reverse=True)
        canonicals = []
        for asset in group:
            if asset.get("duplicateOf"):
                continue
            near = None
            for canonical in canonicals:
                if abs(asset["metrics"]["aspectRatio"] - canonical["metrics"]["aspectRatio"]) > 0.012:
                    continue
                transparent = asset["metrics"]["hasTransparency"] or canonical["metrics"]["hasTransparency"]
                hash_limit = 5 if transparent else 8
                rmse_limit = 7.0 if transparent else 8.0
                if _hash_distance(asset["metrics"]["perceptualHash"], canonical["metrics"]["perceptualHash"]) > hash_limit:
                    continue
                left = image_cache.setdefault(asset["sourcePath"], Image.open(asset["sourcePath"]).copy())
                right = image_cache.setdefault(canonical["sourcePath"], Image.open(canonical["sourcePath"]).copy())
                if _thumbnail_rmse(left, right) <= rmse_limit:
                    near = canonical
                    break
            if near:
                asset["nearDuplicateOf"] = near["id"]
                asset["status"] = "duplicate"
                asset["reasons"] = ["visually equivalent render"]
            else:
                canonicals.append(asset)

    # A production scene may save the same opaque frame under different role
    # names. Only collapse cross-role images when the pixel difference is at
    # encoding-noise level; a populated master and its clean plate stay distinct.
    opaque = [
        asset for asset in candidates
        if not asset.get("duplicateOf") and not asset["metrics"]["hasTransparency"]
    ]
    opaque.sort(key=_canonical_rank, reverse=True)
    cross_type_canonicals = []
    for asset in opaque:
        if asset.get("duplicateOf") or asset.get("nearDuplicateOf"):
            continue
        near = None
        for canonical in cross_type_canonicals:
            if asset["type"] == canonical["type"]:
                continue
            if abs(asset["metrics"]["aspectRatio"] - canonical["metrics"]["aspectRatio"]) > 0.012:
                continue
            if _hash_distance(asset["metrics"]["perceptualHash"], canonical["metrics"]["perceptualHash"]) > 2:
                continue
            left = image_cache.setdefault(asset["sourcePath"], Image.open(asset["sourcePath"]).copy())
            right = image_cache.setdefault(canonical["sourcePath"], Image.open(canonical["sourcePath"]).copy())
            if _thumbnail_rmse(left, right) <= 1.5:
                near = canonical
                break
        if near:
            asset["nearDuplicateOf"] = near["id"]
            asset["status"] = "duplicate"
            asset["reasons"] = ["same opaque frame stored under another asset role"]
        else:
            cross_type_canonicals.append(asset)
    for image in image_cache.values():
        image.close()

    if write_links:
        for child in site_library.iterdir():
            if child.name in {"catalog.json", "overrides.json", "index.html", "contact-sheet.jpg", "voiceovers", "voiceovers.json"}:
                continue
            if child.is_symlink() or child.is_file():
                child.unlink()
            elif child.is_dir():
                for item in sorted(child.rglob("*"), reverse=True):
                    if item.is_symlink() or item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        item.rmdir()
                child.rmdir()
        folder_names = {
            "scene_background": "backgrounds", "registered_layer": "layers", "clean_plate": "clean-plates",
            "master_frame": "masters", "source_reference": "references",
        }
        for asset in assets:
            if asset.get("status") != "approved" or asset["type"] not in folder_names:
                continue
            folder = site_library / folder_names[asset["type"]]
            folder.mkdir(parents=True, exist_ok=True)
            link = folder / f"{asset['id']}-{Path(asset['sourcePath']).name}"
            relative_target = os.path.relpath(asset["sourcePath"], link.parent)
            link.symlink_to(relative_target)
            asset["libraryPath"] = str(link)

    counts = defaultdict(int)
    for asset in assets:
        counts[asset.get("status") or "unknown"] += 1
    catalog = {
        "version": 2,
        "generatedAt": _utc_now(),
        "siteId": site_id,
        "sourceRoot": str(source_root),
        "libraryRoot": str(site_library),
        "policy": {
            "originalsPreserved": True,
            "directReuse": "Only a complete registered scene bundle with matching semantics and geometry.",
            "layerReuse": "Standalone layers are references only outside their original registered scene.",
            "duplicateHandling": "Exact duplicates are checked across roles; near duplicates are role-aware, and only encoding-equivalent opaque cross-role frames are collapsed.",
        },
        "summary": dict(sorted(counts.items())),
        "assets": assets,
    }
    (site_library / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_review_gallery(catalog, site_library / "index.html")
    return catalog


def _write_review_gallery(catalog: dict, output_path: Path) -> None:
    cards = []
    status_order = {"approved": 0, "review": 1, "rejected": 2, "duplicate": 3, "archive": 4}
    for asset in sorted(catalog["assets"], key=lambda item: (status_order.get(item.get("status"), 9), item.get("type", ""), item.get("relativePath", ""))):
        source = Path(asset["sourcePath"])
        href = source.as_uri()
        reasons = "; ".join(asset.get("reasons") or [])
        context = asset.get("context") or {}
        semantic = context.get("visualStory") or context.get("overlayText") or ""
        cards.append(
            f'<a class="card {asset.get("status")}" href="{href}" data-status="{asset.get("status")}" data-type="{asset.get("type")}">'
            f'<img loading="lazy" src="{href}"><strong>{asset.get("type")}</strong>'
            f'<span>{asset.get("status")} · {asset.get("qualityScore", 0)}</span>'
            f'<small>{asset.get("relativePath")}</small><p>{semantic}</p><em>{reasons}</em></a>'
        )
    summary = " · ".join(f"{key}: {value}" for key, value in catalog["summary"].items())
    output_path.write_text(f'''<!doctype html><html><head><meta charset="utf-8"><title>Reel asset library</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#0b1018;color:#edf3fa;font:14px system-ui;padding:24px}}header{{position:sticky;top:0;z-index:2;background:#0b1018f2;padding:10px 0 16px;border-bottom:1px solid #2d3748}}h1{{margin:0 0 8px}}nav{{display:flex;gap:8px;flex-wrap:wrap}}button{{background:#182131;color:#e8eef7;border:1px solid #3a475b;padding:8px 12px;cursor:pointer}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px;margin-top:18px}}.card{{display:flex;flex-direction:column;gap:5px;padding:8px;background:#151c28;color:#edf3fa;text-decoration:none;border:1px solid #344054;min-width:0}}.card.approved{{border-color:#23855f}}.card.review{{border-color:#b58625}}.card.rejected{{border-color:#963f4c}}.card.duplicate,.card.archive{{opacity:.58}}.card img{{width:100%;height:300px;object-fit:contain;background:#252c36}}small,p,em{{color:#aab5c5;overflow-wrap:anywhere;margin:0}}em{{color:#d59ca3}}body[data-filter="approved"] .card:not(.approved),body[data-filter="review"] .card:not(.review),body[data-filter="rejected"] .card:not(.rejected),body[data-filter="duplicate"] .card:not(.duplicate){{display:none}}</style></head><body><header><h1>Reel asset library · site {catalog['siteId']}</h1><p>{summary}</p><nav><button onclick="document.body.dataset.filter=''">All</button><button onclick="document.body.dataset.filter='approved'">Approved</button><button onclick="document.body.dataset.filter='review'">Review</button><button onclick="document.body.dataset.filter='rejected'">Rejected</button><button onclick="document.body.dataset.filter='duplicate'">Duplicates</button></nav></header><main class="grid">{''.join(cards)}</main></body></html>''', encoding="utf-8")


def find_reel_asset_references(library_root, site_id, scene, limit=2) -> list[dict]:
    catalog_path = Path(library_root) / str(int(site_id)) / "catalog.json"
    if not catalog_path.is_file():
        return []
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    scene_text = " ".join(
        str(item or "") for item in (
            scene.get("visualStory"), scene.get("productionBackgroundPrompt"), scene.get("stageBackgroundPrompt"),
            scene.get("shotFraming"), *[layer.get("prompt") for layer in scene.get("layers") or [] if isinstance(layer, dict)],
        )
    )
    ranked = []
    for asset in catalog.get("assets") or []:
        if asset.get("status") != "approved" or asset.get("type") not in {"master_frame", "scene_background"}:
            continue
        context = asset.get("context") if isinstance(asset.get("context"), dict) else {}
        score = _semantic_similarity(scene_text, context.get("semanticText") or context.get("visualStory") or "")
        if score < 0.18:
            continue
        source_path = Path(asset.get("sourcePath") or "")
        if not source_path.is_file():
            continue
        ranked.append({"path": source_path, "score": round(score, 4), "asset": asset})
    ranked.sort(key=lambda item: (-item["score"], -float(item["asset"].get("qualityScore") or 0)))
    return ranked[: max(0, int(limit))]


def find_reel_layer_references(library_root, site_id, scene, role="protagonist", limit=1) -> list[dict]:
    catalog_path = Path(library_root) / str(int(site_id)) / "catalog.json"
    if not catalog_path.is_file():
        return []
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    requested_layers = [
        layer for layer in scene.get("layers") or []
        if isinstance(layer, dict) and str(layer.get("role") or "") == role
    ]
    if not requested_layers:
        return []
    requested_text = " ".join(
        str(item or "")
        for layer in requested_layers
        for item in (layer.get("prompt"), layer.get("action"), layer.get("relationship"))
    )
    ranked = []
    for asset in catalog.get("assets") or []:
        if asset.get("status") != "approved" or asset.get("type") != "registered_layer":
            continue
        if asset.get("layerRole") and asset.get("layerRole") != role:
            continue
        context = asset.get("context") if isinstance(asset.get("context"), dict) else {}
        reference_text = asset.get("layerDescription") or context.get("semanticText") or ""
        score = _semantic_similarity(requested_text, reference_text)
        if score < 0.16:
            continue
        source_path = Path(asset.get("sourcePath") or "")
        if not source_path.is_file():
            continue
        ranked.append({"path": source_path, "score": round(score, 4), "asset": asset})
    ranked.sort(key=lambda item: (-item["score"], -float(item["asset"].get("qualityScore") or 0)))
    return ranked[: max(0, int(limit))]
