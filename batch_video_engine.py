#!/usr/bin/env python3
"""Independent batch planner for seamless generated short-form video.

This module plans assets only. It does not call a media model, render, publish,
or import the legacy Reel pipeline. Adjacent Omni clips share the same persisted
boundary keyframe ID, and those keyframes can be reused by still-image packages.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
from datetime import datetime, timezone

from content_engine import json_text, now_iso, stable_id


DEFAULT_MODEL = "gemini-omni-1.1-flash"
DEFAULT_VOICEOVER_DELIVERY = (
    "an intimate, magnetic storyteller sharing a surprising discovery with a friend; "
    "curious, conspiratorial and warmly confident, never a neutral documentary reader, announcer or voice assistant"
)
VOICEOVER_WORDS_PER_MINUTE = 132.0
# A short hook needs a perceptible beat, not a dead-air gap before the next
# factual line.  The full sentence cadence supplies the remaining separation.
VOICEOVER_HOOK_PAUSE_SECONDS = 0.16
VOICEOVER_SENTENCE_PAUSE_SECONDS = 0.32
VOICEOVER_CLAUSE_PAUSE_SECONDS = 0.16
VOICEOVER_DEFAULT_START_SECONDS = 0.4
VOICEOVER_DEFAULT_END_SECONDS = 9.2
SUPPORTED_OMNI_CLIP_DURATIONS = (6, 8, 10)
# A native Omni clip must not become a silent visual holding pattern before a
# shared boundary.  These limits are intentionally format-level rules; they do
# not depend on a particular story, place, or hook.
VOICEOVER_MAX_LEAD_IN_SECONDS = 0.25
VOICEOVER_MAX_PLANNED_TAIL_SECONDS = 0.35
VOICEOVER_MAX_ESTIMATED_TAIL_SECONDS = 1.00
VOICEOVER_TARGET_COVERAGE = 0.78
DEFAULT_STYLE = {
    "medium": "photorealistic cinematic editorial visualization",
    "palette": ["basalt charcoal", "laurel green", "Atlantic blue", "warm limestone"],
    "aspectRatio": "9:16",
    "fps": 24,
    "resolution": "720p",
    "camera": "physically plausible lens and smooth motivated movement",
    "identityRule": "reuse the exact previous boundary image; never approximate it from text",
    "exclusions": [
        "no readable text inside generated pixels",
        "no logos or watermarks",
        "no identifiable real people or documentary-event simulation",
        "no claim that the generated location is the actual place",
        "no invented objects, dates, quantities or conditions",
    ],
}


def voiceover_word_count(text):
    return len(re.findall(r"\b[\w'-]+\b", str(text or "")))


def estimate_voiceover_seconds(text, hook_text=""):
    """Estimate natural Omni narration time, including audible story pauses."""
    spoken = str(text or "").strip()
    if not spoken:
        return 0.0
    seconds = voiceover_word_count(spoken) / (VOICEOVER_WORDS_PER_MINUTE / 60.0)
    sentence_boundaries = len(re.findall(r"[.!?]+(?=\s|$)", spoken))
    if sentence_boundaries:
        # A final stop does not consume transition time after the spoken script.
        seconds += max(0, sentence_boundaries - 1) * VOICEOVER_SENTENCE_PAUSE_SECONDS
    seconds += len(re.findall(r"[,;:](?=\s|$)", spoken)) * VOICEOVER_CLAUSE_PAUSE_SECONDS
    hook = str(hook_text or "").strip()
    if hook and spoken.casefold().startswith(hook.casefold()) and voiceover_word_count(spoken) > voiceover_word_count(hook):
        seconds += VOICEOVER_HOOK_PAUSE_SECONDS
    return round(seconds, 3)


def minimum_voiceover_clip_count(text, clip_duration_seconds=10, hook_text="", max_clips=3):
    """Return the physical clip floor for naturally delivered narration."""
    duration = max(3.0, min(10.0, float(clip_duration_seconds or 10)))
    usable_seconds = max(0.1, min(VOICEOVER_DEFAULT_END_SECONDS, duration - 0.8) - VOICEOVER_DEFAULT_START_SECONDS)
    required = max(1, int(math.ceil(estimate_voiceover_seconds(text, hook_text) / usable_seconds)))
    return required


def usable_voiceover_seconds(clip_duration_seconds, start_seconds=VOICEOVER_DEFAULT_START_SECONDS):
    duration = float(clip_duration_seconds)
    return max(0.1, (duration - 0.8) - float(start_seconds))


def optimal_omni_clip_duration(text, hook_text="", start_seconds=VOICEOVER_DEFAULT_START_SECONDS, allowed_durations=SUPPORTED_OMNI_CLIP_DURATIONS):
    """Choose the shortest supported Omni duration that preserves natural pacing."""
    estimated = estimate_voiceover_seconds(text, hook_text)
    for duration in sorted({int(value) for value in allowed_durations}):
        if estimated <= usable_voiceover_seconds(duration, start_seconds) + 1e-9:
            return duration
    return None


def voiceover_fits_window(text, start_seconds, end_seconds, hook_text=""):
    available = max(0.0, float(end_seconds) - float(start_seconds))
    estimated = estimate_voiceover_seconds(text, hook_text)
    return estimated <= available + 1e-9, estimated, available


def voiceover_boundary_coverage(text, clip_duration_seconds, start_seconds, end_seconds, hook_text=""):
    """Measure whether native narration keeps a generated clip alive through its cut.

    The timing window is an instruction to Omni, while the estimated duration is
    the amount of actual speech.  Both need to reach the boundary: a wide window
    around a short line still creates a dead air/held-frame transition.
    """
    duration = float(clip_duration_seconds)
    start = float(start_seconds)
    end = float(end_seconds)
    estimated = estimate_voiceover_seconds(text, hook_text)
    spoken_end = start + estimated
    return {
        "estimatedSeconds": estimated,
        "coverage": (estimated / duration) if duration else 0.0,
        "leadInSeconds": start,
        "plannedTailSeconds": max(0.0, duration - end),
        "estimatedTailSeconds": max(0.0, duration - spoken_end),
    }


def ensure_video_batch_schema(conn):
    conn.executescript("""
    create table if not exists content_video_batches (
      id text primary key, site_id integer not null, batch_key text not null,
      contract_version text not null, model text not null, target_ideas integer not null,
      clips_per_idea integer not null, status text not null, planner_config_json text not null,
      counters_json text not null default '{}', created_at text not null, updated_at text not null,
      unique(site_id, batch_key)
    );
    create table if not exists content_video_ideas (
      id text primary key, site_id integer not null, batch_id text not null, ordinal integer not null,
      candidate_id text not null, entity_id text not null, claim_id text not null, relationship_id text,
      title text not null, hook text not null, factual_spine_json text not null,
      audience_state text not null, angle text not null, locale text not null,
      visual_bible_json text not null, duration_seconds integer not null,
      status text not null, novelty_fingerprint text not null, created_at text not null, updated_at text not null,
      unique(batch_id, ordinal), unique(batch_id, novelty_fingerprint)
    );
    create table if not exists content_keyframes (
      id text primary key, site_id integer not null, idea_id text not null, ordinal integer not null,
      role text not null, state_label text not null, prompt text not null, negative_prompt text not null,
      aspect_ratio text not null, resolution text not null, visual_bible_hash text not null,
      continuity_fingerprint text not null, generation_model text, generation_state text not null,
      asset_path text, asset_sha256 text, validation_json text not null default '{}',
      rights_state text not null, created_at text not null, updated_at text not null,
      unique(idea_id, ordinal), unique(site_id, continuity_fingerprint)
    );
    create table if not exists content_video_clips (
      id text primary key, site_id integer not null, idea_id text not null, ordinal integer not null,
      model text not null, duration_seconds integer not null, first_frame_id text not null,
      last_frame_id text not null, video_prompt text not null, motion_contract_json text not null,
      generation_state text not null, remote_job_id text, asset_path text, asset_sha256 text,
      validation_json text not null default '{}', cost_json text not null default '{}',
      created_at text not null, updated_at text not null, unique(idea_id, ordinal)
    );
    create table if not exists content_video_assemblies (
      id text primary key, site_id integer not null, idea_id text not null unique,
      clip_ids_json text not null, duration_seconds integer not null, aspect_ratio text not null,
      fps integer not null, assembly_contract_json text not null, status text not null,
      asset_path text, validation_json text not null default '{}', created_at text not null, updated_at text not null
    );
    create table if not exists content_video_publication_queue (
      id text primary key, site_id integer not null, assembly_id text not null,
      destination text not null, status text not null, scheduled_for text,
      approval_required integer not null default 1, publication_payload_json text not null default '{}',
      created_at text not null, updated_at text not null,
      unique(site_id, assembly_id, destination)
    );
    create table if not exists content_keyframe_uses (
      id text primary key, site_id integer not null, keyframe_id text not null,
      use_kind text not null, target_id text not null, position integer not null,
      crop_contract_json text not null, overlay_contract_json text not null,
      status text not null, created_at text not null, updated_at text not null,
      unique(keyframe_id, use_kind, target_id, position)
    );
    create index if not exists content_video_ideas_batch_idx on content_video_ideas(batch_id, ordinal);
    create index if not exists content_video_clips_idea_idx on content_video_clips(idea_id, ordinal);
    create index if not exists content_video_publication_queue_site_idx on content_video_publication_queue(site_id, status, scheduled_for);
    create index if not exists content_keyframes_idea_idx on content_keyframes(idea_id, ordinal);
    create index if not exists content_keyframe_uses_target_idx on content_keyframe_uses(site_id, use_kind, target_id);
    """)
    idea_columns = {row[1] for row in conn.execute("pragma table_info(content_video_ideas)")}
    if "story_plan_json" not in idea_columns:
        conn.execute("alter table content_video_ideas add column story_plan_json text not null default '{}'")
    if "duration_rationale" not in idea_columns:
        conn.execute("alter table content_video_ideas add column duration_rationale text")
    if "narration_json" not in idea_columns:
        conn.execute("alter table content_video_ideas add column narration_json text not null default '{}'")
    if "character_plan_json" not in idea_columns:
        conn.execute("alter table content_video_ideas add column character_plan_json text not null default '{}'")
    if "quality_score" not in idea_columns:
        conn.execute("alter table content_video_ideas add column quality_score real")
    if "quality_report_json" not in idea_columns:
        conn.execute("alter table content_video_ideas add column quality_report_json text not null default '{}'")
    clip_columns = {row[1] for row in conn.execute("pragma table_info(content_video_clips)")}
    if "voiceover_text" not in clip_columns:
        conn.execute("alter table content_video_clips add column voiceover_text text")
    if "voiceover_timing_json" not in clip_columns:
        conn.execute("alter table content_video_clips add column voiceover_timing_json text not null default '{}'")
    if "on_screen_text_json" not in clip_columns:
        conn.execute("alter table content_video_clips add column on_screen_text_json text not null default '[]'")
    if "character_direction_json" not in clip_columns:
        conn.execute("alter table content_video_clips add column character_direction_json text not null default '{}'")


def _safe_fact(text):
    lowered = str(text or "").casefold()
    rejected = (
        "cookie", "wishlist", "search for", "current weather", "one of the most",
        "best ", "must-see", "perfect ", "ideal ", "quickly became", "...", "telefone:", "telephone:",
        "email is protected", "endereço de email", "contact us", "privacy policy", "terms and conditions",
    )
    postal_or_contact = re.search(r"\b\d{4}\s*[-–]\s*\d{3}\b|\b(?:phone|fax|email|address)\s*:", lowered)
    return 70 <= len(str(text or "")) <= 520 and not postal_or_contact and not any(token in lowered for token in rejected)


def _short_fact(text, limit=150):
    clean = re.sub(r"\s+", " ", str(text or "")).strip()
    first = re.split(r"(?<=[.!?])\s+", clean)[0]
    if len(first) <= limit:
        return first.rstrip(".")
    clipped = first[:limit].rsplit(" ", 1)[0]
    return clipped.rstrip(" ,;:.")


def _hook(entity, fact, ordinal):
    short = _short_fact(fact, 125)
    number = re.search(r"(?:over|more than|approximately|about)?\s*\d[\d,.\s]*(?:m²|years?|km|ha|%)?", fact, re.I)
    if number:
        return f"{number.group(0).strip()} — what does that number reveal about {entity}?"
    families = (
        f"Why does {entity} work this way?",
        f"The hidden mechanism behind {entity}.",
        f"What connects {entity} to this Madeira fact?",
        f"Look closely: {short}?",
    )
    return families[(ordinal - 1) % len(families)]


def _visual_bible(entity, fact, idea_id, config):
    style = dict(DEFAULT_STYLE)
    style.update(config.get("visualStyle") or {})
    return {
        **style,
        "ideaId": idea_id,
        "entity": entity,
        "verifiedFact": fact,
        "continuitySeed": hashlib.sha256(f"{idea_id}|{entity}|{fact}".encode()).hexdigest()[:16],
        "truthBoundary": "Conceptual explanatory imagery only; the claim and source remain the evidence.",
    }


def _frame_states(entity, fact):
    short = _short_fact(fact, 180)
    return [
        ("hook", f"one visually arresting material or mechanism detail that creates curiosity about {entity}"),
        ("context", f"a wider conceptual Madeira context that locates {entity} without imitating a real map or current place"),
        ("mechanism", f"a precise explanatory cutaway showing how the verified relationship could be understood: {short}"),
        ("consequence", f"a clean visual consequence of the fact for a curious visitor or resident, without advice or invented activity"),
        ("payoff", f"a resolved editorial composition joining the entity and verified factual mechanism: {short}"),
    ]


def _keyframe_prompt(entity, fact, state_label, direction, bible):
    exclusions = "; ".join(bible["exclusions"])
    return (
        f"Generate one exact 9:16 boundary keyframe for a seamless short video. "
        f"State: {state_label}. Visual direction: {direction}. Entity: {entity}. "
        f"Verified factual spine: {fact}. Style: {bible['medium']}; palette: {', '.join(bible['palette'])}; "
        f"continuity seed {bible['continuitySeed']}; {bible['camera']}. Keep the top 18% and bottom 16% quiet for later overlays. "
        f"This is an AI-generated photorealistic cinematic visualization, not documentary footage or a photograph of the real location. {exclusions}."
    )


def _video_prompt(entity, fact, start_state, end_state, bible, ordinal, motion_direction="", voiceover_text="", voiceover_start=0.4, voiceover_end=9.2, character_direction=None, clip_duration=10, voiceover_delivery=""):
    moves = ("slow macro dolly with restrained parallax", "controlled crane reveal", "smooth orbital cutaway reveal", "measured pull-back into the resolved composition")
    character_direction = character_direction if isinstance(character_direction, dict) else {}
    character_required = bool(character_direction.get("required"))
    requested_speech_mode = str(character_direction.get("speechMode") or "voiceover").strip().casefold().replace("-", "_")
    visible_dialogue = character_required and requested_speech_mode in {"dialogue", "on_camera", "onscreen", "lip_sync"}
    speech_mode = (
        "The visible character speaks these exact words with natural synchronized lip movement"
        if visible_dialogue else "Generate an off-screen narrator speaking these exact words"
    )
    delivery = str(voiceover_delivery or DEFAULT_VOICEOVER_DELIVERY).strip()
    spoken_audio = (
        f"Audio is generated natively inside this same Omni clip, not added by TTS later. {speech_mode} immediately at {voiceover_start:.1f}s and finish naturally at {voiceover_end:.1f}s: "
        f"\"{voiceover_text}\". Performance direction: {delivery}. Perform the line; never merely read it. "
        f"Enter with an immediate curiosity pull, make one purposeful inflection shift at the factual turn, and land the final reveal with satisfying confidence. "
        f"Use natural conversational pacing with selective emphasis on the concrete noun and the withheld payoff; avoid monotone, flat cadence, sing-song delivery, exaggerated trailer voice, or empty hype. "
        f"Keep speech intelligible over restrained location ambience; no music or extra dialogue. "
        if voiceover_text else "Generate restrained location ambience only; no speech, music or extra dialogue. "
    )
    character_contract = (
        f"Character contract: {json_text(character_direction)}. Preserve the exact face, body, wardrobe and screen direction between boundary frames. "
        + ("The character performs the described action silently and never lip-syncs or speaks; narration remains off-screen. " if not visible_dialogue else "")
        if character_required else "No visible presenter or invented person; the verified place, object or mechanism carries the visual story. "
    )
    opening_hook_contract = (
        "In the first second, foreground the source-grounded physical mechanism or contradiction that proves the hook; do not open on a generic scenic establishing hold. "
        if ordinal == 1 else ""
    )
    return (
        f"Use the supplied first image as the exact first frame and the supplied second image as the exact final frame. "
        f"Generate exactly {int(clip_duration)} seconds of continuous transition between them for clip {ordinal}. Begin with {start_state}; end exactly on {end_state}. "
        f"Motion: {motion_direction or moves[(ordinal - 1) % len(moves)]}. Preserve every shared material, palette, lighting direction, lens logic and geometry from continuity seed {bible['continuitySeed']}. "
        f"The story is about {entity}; verified factual spine: {fact}. {opening_hook_contract}This is an AI-generated photorealistic cinematic visualization, not documentary footage or an exact reconstruction of the real location. {spoken_audio}{character_contract}"
        f"Do not add site-specific objects, physical features, current conditions or facts absent from the verified spine; do not add burned-in captions, logos, cuts, flashes, scene resets or a third setting. "
        f"There must be no static completed-frame hold before the cut: keep motivated visual change until the final 0.15 seconds, then land exactly on the final keyframe. "
        f"The final decoded frame must be visually identical to the supplied final keyframe so the next clip can reuse it without a crossfade."
    )


def _claim_rows(conn, site_id, limit):
    rows = conn.execute("""select min(cc.id) candidate_id, cc.entity_id, cc.claim_id, min(cc.relationship_id) relationship_id,
            max(cc.score) score, min(cc.native_angle) native_angle, min(cc.audience_state) audience_state, min(cc.locale) locale,
            min(ke.relationship_type) relationship_type,
            e.canonical_name, kc.claim_text, kc.source_url, ks.owner
        from content_candidates cc join knowledge_entities e on e.id=cc.entity_id
        join knowledge_claims kc on kc.id=cc.claim_id join knowledge_sources ks on ks.id=kc.source_id
        left join knowledge_edges ke on ke.id=cc.relationship_id
        where cc.site_id=? and cc.workflow_state in ('CANDIDATE','BRIEFED') and kc.status='VERIFIED'
        and kc.risk_class='low' and cc.relationship_id is not null
        and (kc.valid_until is null or kc.valid_until>=?)
        group by cc.claim_id order by score desc, cc.claim_id""", (site_id, now_iso())).fetchall()
    return [row for row in rows if _safe_fact(row["claim_text"])][:limit]


def video_batch_candidates(conn, site_id, limit=30):
    """Return the evidence inputs a provider-neutral story planner may use."""
    return [dict(row) for row in _claim_rows(conn, site_id, max(1, min(100, int(limit))))]


def queue_video_assembly_for_publication(conn, site_id, assembly_id, destination, payload=None):
    """Queue an assembled generated-video asset without invoking a legacy social worker or publisher."""
    destination = str(destination or "").strip().casefold()
    if not destination:
        raise ValueError("publication destination is required")
    assembly = conn.execute(
        "select * from content_video_assemblies where id=? and site_id=?", (assembly_id, site_id)
    ).fetchone()
    if not assembly or not assembly["asset_path"]:
        raise ValueError("only an assembled video asset can enter the publication queue")
    now = now_iso()
    queue_id = stable_id("vpub", site_id, assembly_id, destination)
    data = {"assetPath": assembly["asset_path"], "assemblyId": assembly_id, **(payload if isinstance(payload, dict) else {})}
    conn.execute(
        """insert into content_video_publication_queue(id,site_id,assembly_id,destination,status,scheduled_for,approval_required,publication_payload_json,created_at,updated_at)
           values(?,?,?,?,?,?,?,?,?,?)
           on conflict(site_id,assembly_id,destination) do update set publication_payload_json=excluded.publication_payload_json,updated_at=excluded.updated_at""",
        (queue_id, site_id, assembly_id, destination, "QUEUED", None, 1, json_text(data), now, now),
    )
    return {"id": queue_id, "assemblyId": assembly_id, "destination": destination, "status": "QUEUED", "approvalRequired": True}


def _resolved_story_plan(row, supplied_plan, max_clips, clip_duration_seconds=10):
    supplied_plan = supplied_plan if isinstance(supplied_plan, dict) else {}
    supplied_clips = supplied_plan.get("clips") if isinstance(supplied_plan.get("clips"), list) else []
    supplied_narration = supplied_plan.get("narration") if isinstance(supplied_plan.get("narration"), dict) else {}
    full_script = str(supplied_narration.get("fullScript") or "").strip()
    if not full_script:
        full_script = " ".join(
            str(clip.get("voiceoverText") or "").strip()
            for clip in supplied_clips if isinstance(clip, dict) and str(clip.get("voiceoverText") or "").strip()
        )
    hook = str(supplied_plan.get("hook") or "").strip()
    speech_floor = minimum_voiceover_clip_count(full_script, max(SUPPORTED_OMNI_CLIP_DURATIONS), hook) if full_script else 1
    if speech_floor > max_clips:
        raise ValueError(
            f"Voice-over requires {speech_floor} clips at natural pacing, exceeding the configured maximum of {max_clips}"
        )
    requested = supplied_plan.get("clipCount")
    if requested is None:
        fact_length = len(str(row["claim_text"] or ""))
        semantic_floor = 1 if fact_length <= 145 else (2 if fact_length <= 280 else 3)
        requested = max(semantic_floor, speech_floor)
    elif int(requested) < speech_floor:
        raise ValueError(
            f"Supplied clipCount={requested} cannot fit the voice-over naturally; at least {speech_floor} clips are required"
        )
    clip_count = max(1, min(max_clips, int(requested)))
    fallback_states = _frame_states(row["canonical_name"], row["claim_text"])
    fallback_states = fallback_states[:clip_count] + [fallback_states[-1]]
    supplied_frames = supplied_plan.get("keyframes") if isinstance(supplied_plan.get("keyframes"), list) else []
    states = []
    for index in range(clip_count + 1):
        frame = supplied_frames[index] if index < len(supplied_frames) and isinstance(supplied_frames[index], dict) else {}
        fallback_label, fallback_direction = fallback_states[index]
        states.append((
            str(frame.get("stateLabel") or fallback_label).strip(),
            str(frame.get("visualDescription") or fallback_direction).strip(),
            frame.get("visualSupport") if isinstance(frame.get("visualSupport"), list) else [],
        ))
    motions = []
    clip_contracts = []
    for index in range(clip_count):
        clip = supplied_clips[index] if index < len(supplied_clips) and isinstance(supplied_clips[index], dict) else {}
        motion = str(clip.get("motionDescription") or "").strip()
        motions.append(motion)
        clip_contracts.append({
            "durationSeconds": int(clip.get("durationSeconds") or 0),
            "motionDescription": motion,
            "voiceoverText": str(clip.get("voiceoverText") or "").strip(),
            "voiceoverDelivery": str(clip.get("voiceoverDelivery") or DEFAULT_VOICEOVER_DELIVERY).strip(),
            "voiceoverStartSeconds": float(clip.get("voiceoverStartSeconds") or VOICEOVER_MAX_LEAD_IN_SECONDS),
            "voiceoverEndSeconds": float(clip.get("voiceoverEndSeconds") or 0),
            "onScreenText": clip.get("onScreenText") if isinstance(clip.get("onScreenText"), list) else [],
            "characterDirection": clip.get("characterDirection") if isinstance(clip.get("characterDirection"), dict) else {},
        })
    for index, clip in enumerate(clip_contracts):
        clip_hook = hook if index == 0 else ""
        chosen_duration = clip["durationSeconds"] or optimal_omni_clip_duration(
            clip["voiceoverText"], clip_hook, clip["voiceoverStartSeconds"]
        )
        if chosen_duration not in SUPPORTED_OMNI_CLIP_DURATIONS:
            raise ValueError(
                f"Clip {index + 1} voice-over cannot fit any supported Omni duration {SUPPORTED_OMNI_CLIP_DURATIONS}"
            )
        clip["durationSeconds"] = chosen_duration
        maximum_end = chosen_duration - VOICEOVER_MAX_PLANNED_TAIL_SECONDS
        if not clip["voiceoverEndSeconds"]:
            estimated = estimate_voiceover_seconds(clip["voiceoverText"], clip_hook)
            clip["voiceoverEndSeconds"] = min(maximum_end, round(clip["voiceoverStartSeconds"] + estimated + 0.12, 2))
        elif clip["voiceoverEndSeconds"] > maximum_end:
            raise ValueError(
                f"Clip {index + 1} voice-over end {clip['voiceoverEndSeconds']:.2f}s leaves less than {VOICEOVER_MAX_PLANNED_TAIL_SECONDS:.2f}s for the boundary landing"
            )
        fits, estimated, available = voiceover_fits_window(
            clip["voiceoverText"], clip["voiceoverStartSeconds"], clip["voiceoverEndSeconds"], clip_hook
        )
        if not fits:
            raise ValueError(
                f"Clip {index + 1} voice-over needs about {estimated:.2f}s but its timing window provides {available:.2f}s"
            )
        if clip["voiceoverText"]:
            coverage = voiceover_boundary_coverage(
                clip["voiceoverText"], chosen_duration, clip["voiceoverStartSeconds"], clip["voiceoverEndSeconds"], clip_hook
            )
            if coverage["leadInSeconds"] > VOICEOVER_MAX_LEAD_IN_SECONDS + 1e-9:
                raise ValueError(f"Clip {index + 1} narration lead-in is too long; narration must start within {VOICEOVER_MAX_LEAD_IN_SECONDS:.2f}s")
            if coverage["plannedTailSeconds"] > VOICEOVER_MAX_PLANNED_TAIL_SECONDS + 1e-9:
                raise ValueError(f"Clip {index + 1} narration leaves a planned dead-air tail of {coverage['plannedTailSeconds']:.2f}s")
            if coverage["estimatedTailSeconds"] > VOICEOVER_MAX_ESTIMATED_TAIL_SECONDS + 1e-9 or coverage["coverage"] < VOICEOVER_TARGET_COVERAGE:
                raise ValueError(
                    f"Clip {index + 1} narration does not cover its visual duration; rewrite or repartition the script instead of holding the boundary"
                )
    character_plan = supplied_plan.get("characterPlan") if isinstance(supplied_plan.get("characterPlan"), dict) else {
        "required": False, "rationale": "The verified subject can carry the visual story without a generated on-screen character.",
        "role": "none", "continuityDescription": "",
    }
    narration = supplied_narration if supplied_narration else {
        "language": "en", "delivery": "curious, precise documentary voice", "totalTargetSeconds": clip_count * 10,
        "fullScript": " ".join(item["voiceoverText"] for item in clip_contracts if item["voiceoverText"]),
    }
    quality_audit = supplied_plan.get("qualityAudit") if isinstance(supplied_plan.get("qualityAudit"), dict) else {}
    resolved = {
        "clipCount": clip_count,
        "hook": hook or _hook(row["canonical_name"], row["claim_text"], 1),
        "hookOpenLoop": str(supplied_plan.get("hookOpenLoop") or "").strip(),
        "withheldPayoff": str(supplied_plan.get("withheldPayoff") or "").strip(),
        "swipeTest": str(supplied_plan.get("swipeTest") or "").strip(),
        "storyPromise": str(supplied_plan.get("storyPromise") or row["native_angle"]).strip(),
        "durationRationale": str(supplied_plan.get("durationRationale") or f"{clip_count} distinct visual beat(s) are required to deliver the verified payoff without repetition.").strip(),
        "keyframes": [{"stateLabel": label, "visualDescription": direction, "visualSupport": support} for label, direction, support in states],
        "clips": clip_contracts,
        "narration": narration,
        "characterPlan": character_plan,
        "retentionMechanics": supplied_plan.get("retentionMechanics") if isinstance(supplied_plan.get("retentionMechanics"), dict) else {},
        "qualityAudit": quality_audit,
    }
    # Do not fabricate an editorial approval record for older/manual
    # asset-only records. New Gemini production plans always provide both and
    # are hard-gated by the separate writer/critic path.
    if "narrativeArc" in supplied_plan or "viewerReactionBeat" in supplied_plan:
        resolved["narrativeArc"] = supplied_plan.get("narrativeArc") if isinstance(supplied_plan.get("narrativeArc"), dict) else {}
        resolved["viewerReactionBeat"] = supplied_plan.get("viewerReactionBeat") if isinstance(supplied_plan.get("viewerReactionBeat"), dict) else {}
    return resolved


def narrative_contract_issues(story_plan):
    """Return production-blocking narrative errors without topic-specific rules.

    This is deliberately structural.  Semantic entailment and whether the
    payoff leaks are judged by the isolated Gemini critic; this guard prevents
    a planner from pretending an off-video caption or a self-audit is a Reel
    beat at all.
    """
    clips = story_plan.get("clips") if isinstance(story_plan.get("clips"), list) else []
    arc = story_plan.get("narrativeArc") if isinstance(story_plan.get("narrativeArc"), dict) else {}
    reaction = story_plan.get("viewerReactionBeat") if isinstance(story_plan.get("viewerReactionBeat"), dict) else {}
    issues = []
    payoff_clip = arc.get("payoffClipOrdinal")
    beats = arc.get("beats") if isinstance(arc.get("beats"), list) else []
    if not clips:
        return ["Narrative contract has no clips"]
    if not isinstance(payoff_clip, int) or not 1 <= payoff_clip <= len(clips):
        issues.append("Narrative contract lacks a valid payoff clip")
    if len(beats) != len(clips):
        issues.append("Narrative ledger must contain exactly one beat per clip")
    else:
        for ordinal, beat in enumerate(beats, 1):
            if not isinstance(beat, dict) or int(beat.get("clipOrdinal") or 0) != ordinal:
                issues.append("Narrative ledger clip order is incomplete")
                break
            if not all(str(beat.get(field) or "").strip() for field in ("role", "newInformation", "visualProof", "whyNextBeatNecessary")):
                issues.append(f"Narrative beat {ordinal} has no executable information/proof/transition")
        if len(clips) > 1 and str(beats[0].get("role") or "").strip().casefold() != "hook":
            issues.append("First clip must be the hook beat")
        if isinstance(payoff_clip, int) and len(clips) > 1 and payoff_clip == 1:
            issues.append("Multi-clip story reveals its payoff before escalation")
    if not isinstance(reaction.get("clipOrdinal"), int) or reaction.get("clipOrdinal") != len(clips):
        issues.append("Viewer reaction must be an actual final Reel beat")
    expression = str(reaction.get("inReelExpression") or "").strip()
    comment_expression = str(reaction.get("commentExpression") or "").strip()
    expression_words = voiceover_word_count(expression)
    comment_words = voiceover_word_count(comment_expression)
    placement = str(reaction.get("placement") or "").strip().casefold()
    if not expression or placement not in {"spoken", "on_screen", "spoken_and_on_screen"}:
        issues.append("Viewer reaction lacks an in-Reel spoken/on-screen expression")
    elif clips:
        final_overlays = [str(item).strip() for item in (clips[-1].get("onScreenText") or []) if str(item).strip()]
        final_copy = " ".join([str(clips[-1].get("voiceoverText") or ""), *final_overlays]).casefold()
        if expression.casefold() not in final_copy:
            issues.append("Viewer reaction is metadata, not present in the final Reel beat")
        if str(reaction.get("responseMode") or "").strip().casefold() != "comment" or not comment_expression:
            issues.append("Viewer reaction must create a substantive in-Reel comment")
        elif comment_expression.casefold() not in final_copy:
            issues.append("Comment expression is metadata, not present in the final Reel beat")
        if not 3 <= comment_words <= 12 or expression_words > 12:
            issues.append("Final viewer reaction is too long for large readable mobile text")
        if placement == "on_screen" and final_overlays != [expression]:
            issues.append("Final viewer reaction must be one readable overlay, not duplicated CTA text")
    if any(token in placement for token in ("caption", "pinned", "comment")):
        issues.append("Viewer reaction cannot be delegated to caption or pinned comment")
    return list(dict.fromkeys(issues))


def plan_video_batch(conn, site_id, batch_key, target_ideas=30, clips_per_idea=3, model=DEFAULT_MODEL, config=None):
    ensure_video_batch_schema(conn)
    config = dict(config or {})
    target_ideas = max(1, min(100, int(target_ideas)))
    clips_per_idea = max(2, min(3, int(clips_per_idea)))
    existing = conn.execute("select * from content_video_batches where site_id=? and batch_key=?", (site_id, batch_key)).fetchone()
    if existing:
        return {"batchId": existing["id"], "created": False, **json.loads(existing["counters_json"])}
    contract = conn.execute("select contract_version from content_engine_contracts where site_id=? and active=1 order by id desc limit 1", (site_id,)).fetchone()
    if not contract:
        raise ValueError("An active content-engine contract is required")
    supplied_plans = config.get("ideaPlans") if isinstance(config.get("ideaPlans"), dict) else {}
    if supplied_plans:
        # Supplied plans have already passed the writer/critic gate and may refer
        # to any verified candidate in the site pool, not merely the top 100.
        available = {row["claim_id"]: row for row in _claim_rows(conn, site_id, 10000)}
        claims = []
        for plan_key, plan in supplied_plans.items():
            primary_claim_id = str((plan or {}).get("primaryClaimId") or (plan or {}).get("claimId") or plan_key)
            if primary_claim_id in available:
                row = dict(available[primary_claim_id])
                row["_plan_key"] = plan_key
                claims.append(row)
        claims = claims[:target_ideas]
    else:
        claims = _claim_rows(conn, site_id, target_ideas)
    if len(claims) < target_ideas:
        raise ValueError(f"Only {len(claims)} safe distinct claims are available for {target_ideas} requested ideas")
    batch_id = stable_id("vbatch", site_id, batch_key)
    now = now_iso()
    conn.execute("""insert into content_video_batches(id,site_id,batch_key,contract_version,model,target_ideas,clips_per_idea,status,planner_config_json,created_at,updated_at)
                    values(?,?,?,?,?,?,?,?,?,?,?)""", (batch_id, site_id, batch_key, contract["contract_version"], model, target_ideas, clips_per_idea, "PLANNED", json_text(config), now, now))
    totals = {"ideas": 0, "clips": 0, "keyframes": 0, "assemblies": 0, "reuseUses": 0}
    for idea_ordinal, row in enumerate(claims, start=1):
        plan_key = (row.get("_plan_key") if isinstance(row, dict) else None) or row["claim_id"]
        supplied_plan = supplied_plans.get(plan_key) or {}
        fingerprint = hashlib.sha256(f"{site_id}|{plan_key}|video_reel|{model}".encode()).hexdigest()
        idea_id = stable_id("videa", site_id, batch_key, plan_key)
        story_plan = _resolved_story_plan(row, supplied_plan, clips_per_idea, 10)
        verified_facts = supplied_plan.get("verifiedFacts") if isinstance(supplied_plan.get("verifiedFacts"), list) else []
        if not verified_facts:
            verified_facts = [{"claimId": row["claim_id"], "claim": row["claim_text"], "sourceUrl": row["source_url"], "sourceOwner": row["owner"]}]
        fact_text = " ".join(str(item.get("claim") or "").strip() for item in verified_facts if isinstance(item, dict)).strip()
        idea_clip_count = story_plan["clipCount"]
        clip_durations = [int(clip["durationSeconds"]) for clip in story_plan["clips"]]
        idea_duration = sum(clip_durations)
        quality_audit = story_plan["qualityAudit"]
        hook = story_plan["hook"]
        title = f"{row['canonical_name']}: {_short_fact(fact_text, 80)}"
        bible = _visual_bible(row["canonical_name"], fact_text, idea_id, config)
        conn.execute("""insert into content_video_ideas(id,site_id,batch_id,ordinal,candidate_id,entity_id,claim_id,relationship_id,title,hook,
            factual_spine_json,audience_state,angle,locale,visual_bible_json,duration_seconds,status,novelty_fingerprint,
            story_plan_json,duration_rationale,narration_json,character_plan_json,quality_score,quality_report_json,created_at,updated_at)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (idea_id, site_id, batch_id, idea_ordinal, row["candidate_id"], row["entity_id"], row["claim_id"], row["relationship_id"], title, hook,
             json_text({"primaryClaimId": row["claim_id"], "claimIds": [item.get("claimId") for item in verified_facts], "claims": verified_facts,
                        "claim": fact_text, "sourceUrl": row["source_url"], "sourceOwner": row["owner"]}),
             row["audience_state"], row["native_angle"], row["locale"], json_text(bible), idea_duration, "PLANNED", fingerprint,
             json_text(story_plan), story_plan["durationRationale"], json_text(story_plan["narration"]), json_text(story_plan["characterPlan"]),
             quality_audit.get("overallScore"), json_text(quality_audit), now, now))
        states = [(frame["stateLabel"], frame["visualDescription"]) for frame in story_plan["keyframes"]]
        frame_ids = []
        for frame_ordinal, (label, direction) in enumerate(states):
            frame_id = stable_id("kfrm", idea_id, frame_ordinal)
            continuity = hashlib.sha256(f"{idea_id}|{frame_ordinal}|{label}|{direction}|{bible['continuitySeed']}".encode()).hexdigest()
            prompt = _keyframe_prompt(row["canonical_name"], fact_text, label, direction, bible)
            conn.execute("""insert into content_keyframes(id,site_id,idea_id,ordinal,role,state_label,prompt,negative_prompt,aspect_ratio,resolution,
                visual_bible_hash,continuity_fingerprint,generation_model,generation_state,validation_json,rights_state,created_at,updated_at)
                values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (frame_id, site_id, idea_id, frame_ordinal, "first" if frame_ordinal == 0 else ("last" if frame_ordinal == idea_clip_count else "boundary"),
                 label, prompt, json_text(bible["exclusions"]), bible["aspectRatio"], bible["resolution"], hashlib.sha256(json_text(bible).encode()).hexdigest(),
                 continuity, config.get("keyframeModel") or "gemini-3.1-flash-image", "PLANNED", json_text({"required": ["composition", "truthBoundary", "safeZones", "continuity"]}),
                 "generated_explanatory_media", now, now))
            frame_ids.append(frame_id)
            totals["keyframes"] += 1
        clip_ids = []
        for clip_ordinal in range(1, idea_clip_count + 1):
            clip_id = stable_id("vclip", idea_id, clip_ordinal)
            first_id, last_id = frame_ids[clip_ordinal - 1], frame_ids[clip_ordinal]
            clip_plan = story_plan["clips"][clip_ordinal - 1]
            clip_duration = int(clip_plan["durationSeconds"])
            video_prompt = _video_prompt(
                row["canonical_name"], fact_text, states[clip_ordinal - 1][1], states[clip_ordinal][1], bible, clip_ordinal,
            clip_plan["motionDescription"], clip_plan["voiceoverText"], clip_plan["voiceoverStartSeconds"], clip_plan["voiceoverEndSeconds"], clip_plan["characterDirection"], clip_duration, clip_plan["voiceoverDelivery"],
            )
            motion = {"firstFrameIsAuthoritative": True, "lastFrameIsAuthoritative": True, "sharedBoundaryWithNext": clip_ordinal < idea_clip_count,
                      "noCrossfadeRequired": True, "aspectRatio": bible["aspectRatio"], "fps": bible["fps"], "resolution": bible["resolution"]}
            conn.execute("""insert into content_video_clips(id,site_id,idea_id,ordinal,model,duration_seconds,first_frame_id,last_frame_id,video_prompt,
                motion_contract_json,generation_state,validation_json,cost_json,voiceover_text,voiceover_timing_json,on_screen_text_json,
                character_direction_json,created_at,updated_at) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (clip_id, site_id, idea_id, clip_ordinal, model, clip_duration, first_id, last_id, video_prompt, json_text(motion), "PLANNED",
                 json_text({"required": ["firstFrameMatch", "lastFrameMatch", "noUnplannedCut", "factualVisualBoundary"]}),
                 json_text({"estimatedUsdAt720p": round(clip_duration * 0.10, 2), "estimateOnly": True}),
                 story_plan["clips"][clip_ordinal - 1]["voiceoverText"],
                 json_text({"startSeconds": story_plan["clips"][clip_ordinal - 1]["voiceoverStartSeconds"], "endSeconds": story_plan["clips"][clip_ordinal - 1]["voiceoverEndSeconds"]}),
                 json_text(story_plan["clips"][clip_ordinal - 1]["onScreenText"]),
                 json_text(story_plan["clips"][clip_ordinal - 1]["characterDirection"]), now, now))
            clip_ids.append(clip_id)
            totals["clips"] += 1
        assembly_id = stable_id("vasm", idea_id)
        conn.execute("""insert into content_video_assemblies(id,site_id,idea_id,clip_ids_json,duration_seconds,aspect_ratio,fps,assembly_contract_json,status,created_at,updated_at)
            values(?,?,?,?,?,?,?,?,?,?,?)""", (assembly_id, site_id, idea_id, json_text(clip_ids), idea_duration, bible["aspectRatio"], bible["fps"],
            json_text({"join": "exact_shared_boundary_frame", "crossfade": False, "audio": "generated_natively_per_clip_by_omni", "captionRender": "post-assembly", "legacyReelPipeline": False}), "PLANNED", now, now))
        totals["assemblies"] += 1
        for frame_ordinal, frame_id in enumerate(frame_ids):
            uses = [("carousel_slide", assembly_id, frame_ordinal, "4:5")]
            if frame_ordinal == len(frame_ids) - 1:
                uses += [("pinterest_pin", assembly_id, 1, "2:3"), ("photo_post", assembly_id, 1, "4:5")]
            for use_kind, target_id, position, crop_ratio in uses:
                use_id = stable_id("kuse", frame_id, use_kind, target_id, position)
                conn.execute("""insert into content_keyframe_uses(id,site_id,keyframe_id,use_kind,target_id,position,crop_contract_json,overlay_contract_json,status,created_at,updated_at)
                    values(?,?,?,?,?,?,?,?,?,?,?)""", (use_id, site_id, frame_id, use_kind, target_id, position,
                    json_text({"targetAspectRatio": crop_ratio, "mode": "derive_from_master", "preserveSubject": True, "regenerate": False}),
                    json_text({"textAddedAfterGeneration": True, "useSafeZone": True}), "PLANNED", now, now))
                totals["reuseUses"] += 1
        totals["ideas"] += 1
    conn.execute("update content_video_batches set counters_json=?,updated_at=? where id=?", (json_text(totals), now_iso(), batch_id))
    return {"batchId": batch_id, "created": True, **totals}


def batch_snapshot(conn, site_id, batch_id):
    batch = conn.execute("select * from content_video_batches where id=? and site_id=?", (batch_id, site_id)).fetchone()
    if not batch:
        return None
    ideas = conn.execute("""select vi.*, e.canonical_name from content_video_ideas vi join knowledge_entities e on e.id=vi.entity_id
                            where vi.batch_id=? order by vi.ordinal""", (batch_id,)).fetchall()
    result = {"batch": dict(batch), "ideas": []}
    for idea in ideas:
        clips = conn.execute("select * from content_video_clips where idea_id=? order by ordinal", (idea["id"],)).fetchall()
        frames = conn.execute("select * from content_keyframes where idea_id=? order by ordinal", (idea["id"],)).fetchall()
        uses = conn.execute("""select ku.* from content_keyframe_uses ku join content_keyframes k on k.id=ku.keyframe_id
                               where k.idea_id=? order by ku.use_kind,ku.position""", (idea["id"],)).fetchall()
        result["ideas"].append({"idea": dict(idea), "clips": [dict(row) for row in clips], "keyframes": [dict(row) for row in frames], "uses": [dict(row) for row in uses]})
    return result


def validate_batch(conn, site_id, batch_id):
    snapshot = batch_snapshot(conn, site_id, batch_id)
    if not snapshot:
        raise ValueError("batch not found")
    errors = []
    for item in snapshot["ideas"]:
        clips, frames = item["clips"], item["keyframes"]
        idea = item["idea"]
        if len(frames) != len(clips) + 1:
            errors.append(f"{idea['id']}: boundary count mismatch")
        for index in range(len(clips) - 1):
            if clips[index]["last_frame_id"] != clips[index + 1]["first_frame_id"]:
                errors.append(f"{idea['id']}: clips {index + 1}/{index + 2} do not share a boundary")
        if any(clip["model"] != snapshot["batch"]["model"] for clip in clips):
            errors.append(f"{idea['id']}: model mismatch")
        if any(int(clip["duration_seconds"]) not in SUPPORTED_OMNI_CLIP_DURATIONS for clip in clips):
            errors.append(f"{idea['id']}: unsupported Omni clip duration; expected one of {SUPPORTED_OMNI_CLIP_DURATIONS}")
        summed_duration = sum(int(clip["duration_seconds"]) for clip in clips)
        if int(idea["duration_seconds"]) != summed_duration:
            errors.append(f"{idea['id']}: idea duration does not equal the sum of its clip durations")
        narration = json.loads(idea.get("narration_json") or "{}")
        story_plan = json.loads(idea.get("story_plan_json") or "{}")
        # Older/manual asset-only records predate the editorial planner.  The
        # production Gemini writer always supplies both fields and is rejected
        # by its deterministic gate when they are absent; retain this validator
        # as backward-compatible infrastructure for historic records.
        if "narrativeArc" in story_plan or "viewerReactionBeat" in story_plan:
            for narrative_issue in narrative_contract_issues(story_plan):
                errors.append(f"{idea['id']}: {narrative_issue}")
        full_script = str(narration.get("fullScript") or "").strip()
        assembled_script = " ".join(str(clip.get("voiceover_text") or "").strip() for clip in clips).strip()
        if full_script and full_script != assembled_script:
            errors.append(f"{idea['id']}: narration fullScript does not equal the ordered clip voice-over")
        # Once a story is divided into clips, physical capacity is defined by
        # each clip's own duration and speech window. Re-dividing the combined
        # script by the first clip's capacity can invent a false extra clip for
        # valid mixed-duration assemblies such as 6s + 8s.
        for index, clip in enumerate(clips, 1):
            timing = json.loads(clip.get("voiceover_timing_json") or "{}")
            start = float(timing.get("startSeconds", VOICEOVER_DEFAULT_START_SECONDS))
            end = float(timing.get("endSeconds", VOICEOVER_DEFAULT_END_SECONDS))
            maximum_end = float(clip["duration_seconds"]) - VOICEOVER_MAX_PLANNED_TAIL_SECONDS
            if end > maximum_end + 1e-9:
                errors.append(
                    f"{idea['id']}: clip {index} narration ends at {end:.2f}s; must end by {maximum_end:.2f}s"
                )
            clip_hook = idea.get("hook") or "" if index == 1 else ""
            fits, estimated, available = voiceover_fits_window(clip.get("voiceover_text") or "", start, end, clip_hook)
            if not fits:
                errors.append(
                    f"{idea['id']}: clip {index} narration needs about {estimated:.2f}s but timing provides {available:.2f}s"
                )
            if clip.get("voiceover_text"):
                coverage = voiceover_boundary_coverage(
                    clip["voiceover_text"], clip["duration_seconds"], start, end, clip_hook
                )
                if coverage["leadInSeconds"] > VOICEOVER_MAX_LEAD_IN_SECONDS + 1e-9:
                    errors.append(f"{idea['id']}: clip {index} narration starts too late for a seamless boundary")
                if coverage["plannedTailSeconds"] > VOICEOVER_MAX_PLANNED_TAIL_SECONDS + 1e-9:
                    errors.append(f"{idea['id']}: clip {index} has a planned dead-air tail")
                if coverage["estimatedTailSeconds"] > VOICEOVER_MAX_ESTIMATED_TAIL_SECONDS + 1e-9 or coverage["coverage"] < VOICEOVER_TARGET_COVERAGE:
                    errors.append(f"{idea['id']}: clip {index} narration does not cover its visual duration")
    return {"ok": not errors, "errors": errors, "ideas": len(snapshot["ideas"]),
            "clips": sum(len(item["clips"]) for item in snapshot["ideas"]),
            "keyframes": sum(len(item["keyframes"]) for item in snapshot["ideas"]),
            "reuseUses": sum(len(item["uses"]) for item in snapshot["ideas"])}
