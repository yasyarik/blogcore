from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import wave
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


FULL_VOICE_NAMES = {"reel-narration.wav", "reel-narration-full.wav"}
SCENE_VOICE_PATTERN = re.compile(r"scene-(\d+)-voice\.wav$", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _wav_info(path: Path) -> dict:
    with wave.open(str(path), "rb") as opened:
        frames = opened.getnframes()
        rate = opened.getframerate()
        return {
            "channels": opened.getnchannels(),
            "sampleWidth": opened.getsampwidth(),
            "sampleRate": rate,
            "frames": frames,
            "durationSeconds": round(frames / max(1, rate), 3),
        }


def _job_titles(db_path: Path, site_id: int) -> dict[str, str]:
    if not db_path.is_file():
        return {}
    connection = sqlite3.connect(db_path)
    try:
        rows = connection.execute(
            "select id, coalesce(nullif(title,''), topic, id) from content_jobs where site_id=?",
            (int(site_id),),
        ).fetchall()
    finally:
        connection.close()
    return {str(row[0]): str(row[1] or row[0]) for row in rows}


def _scene_set(files: list[Path]) -> list[Path]:
    indexed = []
    for path in files:
        match = SCENE_VOICE_PATTERN.fullmatch(path.name)
        if match:
            indexed.append((int(match.group(1)), path))
    indexed.sort()
    if len(indexed) < 4 or [item[0] for item in indexed] != list(range(1, len(indexed) + 1)):
        return []
    return [item[1] for item in indexed]


def _scene_signature(paths: list[Path]) -> str:
    return hashlib.sha256("|".join(_sha256(path) for path in paths).encode()).hexdigest()


def _concat_wavs(paths: list[Path], output: Path, pause_seconds: float = 0.28) -> None:
    first_info = _wav_info(paths[0])
    params = (first_info["channels"], first_info["sampleWidth"], first_info["sampleRate"])
    chunks = []
    for path in paths:
        info = _wav_info(path)
        if (info["channels"], info["sampleWidth"], info["sampleRate"]) != params:
            raise ValueError(f"Incompatible scene voice format: {path}")
        with wave.open(str(path), "rb") as opened:
            chunks.append(opened.readframes(opened.getnframes()))
    silence_frames = int(params[2] * pause_seconds)
    silence = b"\0" * silence_frames * params[0] * params[1]
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as written:
        written.setnchannels(params[0])
        written.setsampwidth(params[1])
        written.setframerate(params[2])
        for index, chunk in enumerate(chunks):
            if index:
                written.writeframes(silence)
            written.writeframes(chunk)


def build_reel_voiceover_catalog(source_root, library_root, site_id, db_path) -> dict:
    source_root = Path(source_root).resolve()
    site_library = Path(library_root).resolve() / str(int(site_id))
    output_dir = site_library / "voiceovers"
    output_dir.mkdir(parents=True, exist_ok=True)
    for child in output_dir.iterdir():
        if child.is_symlink() or child.is_file():
            child.unlink()

    groups: dict[str, list[Path]] = defaultdict(list)
    for path in source_root.rglob("*.wav"):
        relative = path.relative_to(source_root)
        if relative.parts:
            groups[relative.parts[0]].append(path)

    titles = _job_titles(Path(db_path), site_id)
    candidates = []
    excluded_partial = []
    for asset_key, files in groups.items():
        scene_files = _scene_set(files)
        scene_signature = _scene_signature(scene_files) if scene_files else ""
        full_files = [path for path in files if path.name.lower() in FULL_VOICE_NAMES and "source" not in path.name.lower()]
        for path in full_files:
            info = _wav_info(path)
            if info["durationSeconds"] < 10:
                continue
            candidates.append({
                "kind": "original_full_track", "assetKey": asset_key, "path": path,
                "sceneFiles": scene_files, "sceneSignature": scene_signature,
                "audioSha256": _sha256(path), "durationSeconds": info["durationSeconds"],
                "mtime": path.stat().st_mtime,
            })
        if not full_files and scene_files:
            candidates.append({
                "kind": "assembled_scene_set", "assetKey": asset_key, "path": None,
                "sceneFiles": scene_files, "sceneSignature": scene_signature,
                "audioSha256": "", "durationSeconds": 0, "mtime": max(path.stat().st_mtime for path in scene_files),
            })
        elif not full_files:
            clips = sorted(path for path in files if SCENE_VOICE_PATTERN.fullmatch(path.name))
            if clips:
                excluded_partial.append({"assetKey": asset_key, "sceneCount": len(clips)})

    candidates.sort(key=lambda item: (item["kind"] == "original_full_track", item["mtime"]), reverse=True)
    seen_audio = {}
    seen_scenes = {}
    voiceovers = []
    duplicates = []
    for candidate in candidates:
        duplicate_id = seen_audio.get(candidate["audioSha256"]) if candidate["audioSha256"] else None
        duplicate_id = duplicate_id or (seen_scenes.get(candidate["sceneSignature"]) if candidate["sceneSignature"] else None)
        if duplicate_id:
            duplicates.append({
                "assetKey": candidate["assetKey"], "kind": candidate["kind"],
                "duplicateOf": duplicate_id,
            })
            if candidate["sceneSignature"]:
                seen_scenes[candidate["sceneSignature"]] = duplicate_id
            continue

        stable = candidate["audioSha256"] or candidate["sceneSignature"]
        voice_id = hashlib.sha1(f"{site_id}:{stable}".encode()).hexdigest()[:16]
        target = output_dir / f"{voice_id}.wav"
        if candidate["kind"] == "original_full_track":
            target.symlink_to(os.path.relpath(candidate["path"], target.parent))
        else:
            _concat_wavs(candidate["sceneFiles"], target)
            candidate["audioSha256"] = _sha256(target)
            candidate["durationSeconds"] = _wav_info(target)["durationSeconds"]

        job_id = candidate["assetKey"].split("-", 1)[0]
        record = {
            "id": voice_id,
            "siteId": int(site_id),
            "jobId": job_id,
            "title": titles.get(job_id, "Reel voiceover"),
            "assetKey": candidate["assetKey"],
            "kind": candidate["kind"],
            "durationSeconds": candidate["durationSeconds"],
            "sceneCount": len(candidate["sceneFiles"]),
            "audioSha256": candidate["audioSha256"],
            "sceneSignature": candidate["sceneSignature"],
            "libraryPath": str(target),
            "sourceFiles": [str(path.relative_to(source_root)) for path in candidate["sceneFiles"]] or [str(candidate["path"].relative_to(source_root))],
            "createdAt": datetime.fromtimestamp(candidate["mtime"], timezone.utc).isoformat(timespec="seconds"),
        }
        voiceovers.append(record)
        seen_audio[candidate["audioSha256"]] = voice_id
        if candidate["sceneSignature"]:
            seen_scenes[candidate["sceneSignature"]] = voice_id

    voiceovers.sort(key=lambda item: item["createdAt"], reverse=True)
    catalog = {
        "version": 1,
        "generatedAt": _now(),
        "siteId": int(site_id),
        "sourceRoot": str(source_root),
        "libraryRoot": str(output_dir),
        "summary": {
            "voiceovers": len(voiceovers),
            "duplicates": len(duplicates),
            "partialSetsExcluded": len(excluded_partial),
        },
        "voiceovers": voiceovers,
        "duplicates": duplicates,
        "partialSetsExcluded": excluded_partial,
    }
    site_library.mkdir(parents=True, exist_ok=True)
    (site_library / "voiceovers.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    return catalog
